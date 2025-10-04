"""Pet window module (clean rebuild)."""

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
    QSizePolicy,
    QSpacerItem,
)

from .state import StateMachine
from .config import Config
from .style_sheet import generate_pet_info_css

if TYPE_CHECKING:
    from MainLayer import MainLayer


class PetAnimationLabel(QLabel):
    """Display animated GIF with optional horizontal mirror."""

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
    """Main pet window with animation + info panel.

    Adds a fixed gap spacer to ensure the info panel never overlaps the pet
    even after dynamic resize operations.
    """

    config_changed = Signal(str)

    GAP_WIDTH = 24  # Reserved horizontal space between animation and info panel

    def __init__(self, config: Config, main_layer: "MainLayer"):
        super().__init__()
        self.config: Config = config
        self.movie: Optional[QMovie] = None
        self.movie_cache: Dict[str, QMovie] = {}
        self.current_gif_path: Optional[str] = None  # 记录当前播放的 GIF 路径
        self.main_layer: MainLayer = main_layer
        self._last_pet_w = self.config.config["Window"]["Width"]
        self._last_pet_h = self.config.config["Window"]["Height"]

        self._setup_ui()
        self._setup_window()  # 初始窗口尺寸
        self._load_resources()  # 加载 GIF 列表等资源
        self._setup_audio()
        self._setup_state_machine()
        self.update_config()  # 应用配置（再次刷新尺寸与主题）

    # ---------------- UI / Layout ----------------
    def _setup_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)

        self.animation_label = PetAnimationLabel(self.main_widget)
        self.animation_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.animation_label.setFixedSize(
            self.config.config["Window"]["Width"],
            self.config.config["Window"]["Height"],
        )
        self.animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._setup_info_widget()

        self.main_layout.addWidget(
            self.animation_label, 0, Qt.AlignmentFlag.AlignVCenter
        )
        # Fixed-width spacer to reserve gap
        self.gap_spacer = QSpacerItem(
            self.GAP_WIDTH, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )
        self.main_layout.addItem(self.gap_spacer)
        self.main_layout.addWidget(self.info_widget, 0, Qt.AlignmentFlag.AlignVCenter)

    def _setup_info_widget(self):
        self.info_widget = QWidget()
        self.info_widget.setFixedSize(150, 100)
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(10, 6, 10, 6)
        self.info_layout.setSpacing(2)
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("内存: 0%")
        self.network_label = QLabel("网速: 0 KB/s")
        for label in [self.cpu_label, self.memory_label, self.network_label]:
            self.info_layout.addWidget(label)
        self.update_theme()

    def _setup_window(self):
        self.setWindowTitle("Doro")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self._update_window_size()

    def _load_gif_files(self):
        self.gif_files = self.main_layer.resource_manager.get_all_gif()

    def _load_resources(self):
        self._load_gif_files()
        self.setMouseTracking(True)
        self.screen_geometry = self.screen().availableGeometry()

    def _setup_audio(self):
        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_player.setAudioOutput(self.audio_output)
        music_root = Config.PATH_CONFIG["Resources"]["Music"].get("DoubleClick")
        if music_root and os.path.exists(music_root):
            candidates = self.main_layer.resource_manager.get_music("DoubleClick")
            if candidates:
                self.audio_player.setSource(
                    QUrl.fromLocalFile(random.choice(candidates))
                )
                self.audio_player.stop()

    def _setup_state_machine(self):
        self.state_machine = StateMachine(self)
        self.state_machine.ui_components["cpu_label"] = self.cpu_label
        self.state_machine.ui_components["memory_label"] = self.memory_label
        self.state_machine.ui_components["network_label"] = self.network_label

    # ---------------- Sizing ----------------
    def _update_window_size(self):
        """Recalculate window & animation size with global scale and gap."""
        pet_w = self.config.config["Window"]["Width"]
        pet_h = self.config.config["Window"]["Height"]
        self.animation_label.setFixedSize(pet_w, pet_h)
        self._last_pet_w, self._last_pet_h = pet_w, pet_h

        gap_cfg = max(
            0, int(self.config.config.get("Info", {}).get("Gap", self.GAP_WIDTH))
        )
        show_info = self.config.config["Info"]["ShowInfo"]
        if show_info:
            self.info_widget.show()
            info_w = self.info_widget.sizeHint().width()
            total_width = pet_w + self.main_layout.spacing() + gap_cfg + info_w
            total_height = max(pet_h, self.info_widget.sizeHint().height())
            self.gap_spacer.changeSize(
                gap_cfg, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
            )
        else:
            self.info_widget.hide()
            total_width = pet_w
            total_height = pet_h
            self.gap_spacer.changeSize(
                0, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
            )

        self.main_layout.invalidate()
        self.setMinimumSize(total_width, total_height)
        self.resize(total_width, total_height)

        # 强制重设缩放并刷新当前播放的 GIF，确保缩小时全部 GIF 收缩
        if self.movie:
            was_running = self.movie.state() == QMovie.MovieState.Running
            self.movie.stop()
            self.movie.setScaledSize(QSize(pet_w, pet_h))
            if was_running:
                self.movie.start()
            self.animation_label.update()

        # 预缩放缓存中的其它 GIF，确保后续播放立即使用新尺寸
        for m in self.movie_cache.values():
            if m is not self.movie:
                m.setScaledSize(QSize(pet_w, pet_h))

        # 全部 GIF 资源重新加载
        self.reload_all_gifs()

    # ---------------- Public API ----------------
    def play_gif(self, gif_path: str, mirror: bool = False):
        if not os.path.exists(gif_path):
            print(f"GIF文件不存在: {gif_path}")
            return
        if self.movie:
            self.movie.stop()
        movie = self.movie_cache.get(gif_path)
        if movie is None:
            movie = QMovie(gif_path)
            movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie_cache[gif_path] = movie

        w = self.config.config["Window"]["Width"]
        h = self.config.config["Window"]["Height"]
        movie.setScaledSize(QSize(w, h))
        self.movie = movie
        self.animation_label.setMovie(self.movie)
        self.animation_label.set_mirror(mirror)
        self.movie.start()
        self.current_gif_path = gif_path

    def reload_all_gifs(self):
        """重新从磁盘加载所有 GIF 资源并按当前缩放倍率设置尺寸。"""
        w = self.config.config["Window"]["Width"]
        h = self.config.config["Window"]["Height"]

        # 重新构建缓存
        new_cache: Dict[str, QMovie] = {}
        for path in getattr(self, "gif_files", []):
            if not os.path.exists(path):
                continue
            m = QMovie(path)
            m.setCacheMode(QMovie.CacheMode.CacheAll)
            m.setScaledSize(QSize(w, h))
            new_cache[path] = m
        self.movie_cache = new_cache

        # 如果当前有正在播放的 GIF, 切换到新实例
        if self.current_gif_path and self.current_gif_path in self.movie_cache:
            prev_state_running = (
                self.movie and self.movie.state() == QMovie.MovieState.Running
            )
            self.movie = self.movie_cache[self.current_gif_path]
            self.animation_label.setMovie(self.movie)
            if prev_state_running:
                self.movie.start()
            self.animation_label.update()

    def set_info_visible(self):
        self.info_widget.setVisible(self.config.config["Info"]["ShowInfo"])
        self._update_window_size()

    def set_always_on_top(self, always_on_top: bool):
        flags = self.windowFlags()
        if always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def set_frameless_mode(self, frameless: bool):
        flags: Qt.WindowType = self.windowFlags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        flags &= ~Qt.WindowType.WindowMinimizeButtonHint
        if not frameless:
            flags &= ~Qt.WindowType.Tool
            flags &= ~Qt.WindowType.FramelessWindowHint
        else:
            flags |= Qt.WindowType.Tool
            flags |= Qt.WindowType.FramelessWindowHint
        self.setWindowFlags(flags)
        self.show()

    def update_theme(self):
        colors = self.config.get_theme_colors()
        self.info_widget.setStyleSheet(generate_pet_info_css(colors))
        self.info_widget.setObjectName("PetInfoWindowInfoWidget")

    def update_config(self):
        self.set_info_visible()
        self.set_always_on_top(self.config.config["Window"].get("StaysOnTop", True))
        self.set_frameless_mode(self.config.config["Window"].get("Frameless", True))
        self.update_theme()
        if hasattr(self, "state_machine"):
            self.state_machine.update_config()
        self._update_window_size()

    # ---------------- Qt Events ----------------
    def event(self, event: QEvent) -> bool:  # type: ignore[override]
        if hasattr(self, "state_machine") and self.state_machine.handle_event(event):
            return True
        return super().event(event)

    def closeEvent(self, event: QEvent):  # type: ignore[override]
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
