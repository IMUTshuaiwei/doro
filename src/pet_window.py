import os
import random
from typing import Dict, Optional, TYPE_CHECKING
from PySide6.QtCore import Qt, QSize, QUrl, QEvent, Signal
from PySide6.QtGui import QMovie, QTransform, QPainter, QPaintEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from .state import StateMachine
from .config import Config
from .style_sheet import generate_pet_info_css

if TYPE_CHECKING:
    from MainLayer import MainLayer


class PetAnimationLabel(QLabel):
    """自定义动画标签: 通过重写 paintEvent 实现镜像而不逐帧信号处理, 避免残影"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._mirror: bool = False

    def set_mirror(self, mirror: bool):
        if self._mirror != mirror:
            self._mirror = mirror
            self.update()

    def paintEvent(self, event: QPaintEvent):  # type: ignore[override]
        movie = self.movie()
        if movie and movie.state() != QMovie.MovieState.NotRunning:
            frame = movie.currentPixmap()
            if self._mirror and not frame.isNull():
                frame = frame.transformed(QTransform().scale(-1, 1))
            painter = QPainter(self)
            x = (self.width() - frame.width()) // 2
            y = (self.height() - frame.height()) // 2
            painter.drawPixmap(x, y, frame)
        else:
            super().paintEvent(event)


class PetWindow(QMainWindow):
    """宠物主窗口类"""

    config_changed = Signal(str)  # 配置改变信号

    def __init__(self, config: Config, main_layer: "MainLayer"):
        super().__init__()
        self.config: Config = config
        self.movie: Optional[QMovie] = None  # 当前动画
        self.movie_cache: Dict[str, QMovie] = {}
        self.main_layer: MainLayer = main_layer

        # 分步骤初始化
        self._setup_ui()            # 基础 UI 组件 & 动画标签 & 信息面板
        self._setup_window()        # 窗口 flag 与尺寸等
        self._load_resources()      # 加载 GIF / 资源
        self._setup_audio()         # 音频
        self._setup_state_machine() # 状态机
        self.update_config()        # 根据配置应用显示/主题/窗口模式

    # ---------------- Internal setup methods -----------------
    def _setup_ui(self):
        """初始化主部件/布局/动画标签/信息窗口"""
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(4)

        # 动画标签
        self.animation_label = PetAnimationLabel(self.main_widget)
        self.animation_label.setFixedSize(
            self.config.config["Window"]["Width"],
            self.config.config["Window"]["Height"],
        )
        self.animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 信息窗口
        self._setup_info_widget()

        # 放入布局 (顺序: 动画 -> 信息)
        self.main_layout.addWidget(self.animation_label)
        self.main_layout.addWidget(self.info_widget)

    def _setup_window(self):
        """窗口基础属性"""
        self.setWindowTitle("Doro")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self._update_window_size()

    def _load_gif_files(self):
        """预加载 GIF (可按需懒加载, 这里只收集路径)"""
        self.gif_files = self.main_layer.resource_manager.get_all_gif()

    def _load_resources(self):
        """加载资源文件"""
        self._load_gif_files()
        # 鼠标跟踪 & 屏幕几何
        self.setMouseTracking(True)
        self.screen_geometry = self.screen().availableGeometry()

    def _setup_audio(self):
        """初始化音频系统"""
        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_player.setAudioOutput(self.audio_output)
        music_root = Config.PATH_CONFIG["Resources"]["Music"].get("DoubleClick")
        if music_root and os.path.exists(music_root):
            candidates = self.main_layer.resource_manager.get_music("DoubleClick")
            if candidates:
                self.audio_player.setSource(QUrl.fromLocalFile(random.choice(candidates)))
                self.audio_player.stop()

    def _setup_state_machine(self):
        self.state_machine = StateMachine(self)
        self.state_machine.ui_components["cpu_label"] = self.cpu_label
        self.state_machine.ui_components["memory_label"] = self.memory_label
        self.state_machine.ui_components["network_label"] = self.network_label

    def _setup_info_widget(self):
        """初始化信息窗口"""
        self.info_widget = QWidget()
        self.info_widget.setFixedSize(150, 100)
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(10, 5, 10, 5)
        self.info_layout.setSpacing(2)

        # 系统信息标签
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("内存: 0%")
        self.network_label = QLabel("网速: 0 KB/s")

        for label in [
            self.cpu_label,
            self.memory_label,
            self.network_label,
        ]:
            self.info_layout.addWidget(label)

        self.update_theme()

    # -------------------- Info widget --------------------

    def _update_window_size(self):
        """根据是否显示信息窗口调整主窗口尺寸"""
        pet_w = self.config.config["Window"]["Width"]
        pet_h = self.config.config["Window"]["Height"]
        self.animation_label.setFixedSize(pet_w, pet_h)
        if self.config.config["Info"]["ShowInfo"]:
            total_width = pet_w + self.info_widget.width() + self.main_layout.spacing()
        else:
            total_width = pet_w
        self.resize(total_width, max(pet_h, self.info_widget.height()))

    # ========== 公共方法 ==========
    def play_gif(self, gif_path: str, mirror: bool = False):
        """播放 GIF 动画 (mirror=True 镜像)

        使用自定义标签 paintEvent 镜像避免残影。
        """
        if not os.path.exists(gif_path):
            print(f"GIF文件不存在: {gif_path}")
            return

        # 停止旧动画 (不必清除标签, 由新 movie 覆盖)
        if self.movie:
            self.movie.stop()

        movie = self.movie_cache.get(gif_path)
        if movie is None:
            movie = QMovie(gif_path)
            movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie_cache[gif_path] = movie

        movie.setScaledSize(
            QSize(
                self.config.config["Window"]["Width"],
                self.config.config["Window"]["Height"],
            )
        )
        self.movie = movie

        # 设置标签 movie 并切换镜像模式
        self.animation_label.setMovie(self.movie)
        self.animation_label.set_mirror(mirror)
        self.movie.start()

    def set_info_visible(self):
        self.info_widget.setVisible(self.config.config["Info"]["ShowInfo"])
        self._update_window_size()

    def set_always_on_top(self, always_on_top: bool):
        """设置窗口是否置顶"""
        flags = self.windowFlags()
        if always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def set_frameless_mode(self, frameless: bool):
        """
        切换窗口模式: True 为标准窗口(带边框, 便于录屏), False 为无边框(桌宠模式)
        """
        flags: Qt.WindowType = self.windowFlags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        flags &= ~Qt.WindowType.WindowMinimizeButtonHint  # 禁止最小化
        if not frameless:  # 标准窗口模式
            flags &= ~Qt.WindowType.Tool
            flags &= ~Qt.WindowType.FramelessWindowHint
        else:  # 无边框模式
            flags |= Qt.WindowType.Tool
            flags |= Qt.WindowType.FramelessWindowHint

        self.setWindowFlags(flags)
        self.show()

    def update_theme(self):
        colors = self.config.get_theme_colors()
        self.info_widget.setStyleSheet(generate_pet_info_css(colors))
        self.info_widget.setObjectName("PetInfoWindowInfoWidget")

    def update_config(self):
        # 信息窗口
        self.set_info_visible()
        # 窗口模式 / 置顶
        self.set_always_on_top(self.config.config["Window"].get("StaysOnTop", True))
        self.set_frameless_mode(self.config.config["Window"].get("Frameless", True))
        # 主题
        self.update_theme()
        if hasattr(self, "state_machine"):
            self.state_machine.update_config()

    # ========== 事件处理 ==========
    def event(self, event: QEvent) -> bool:
        """事件处理"""
        if hasattr(self, "state_machine") and self.state_machine.handle_event(event):
            return True
        return super().event(event)

    def closeEvent(self, event: QEvent):
        """窗口关闭事件"""
        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()

        if hasattr(self, "audio_player"):
            self.audio_player.stop()
            self.audio_player.deleteLater()
        if hasattr(self, "audio_output"):
            self.audio_output.deleteLater()

        event.accept()
        os._exit(0)
