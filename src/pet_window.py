from PySide6.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QMenu,QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QSize, QPoint, QUrl
from PySide6.QtGui import QMovie, QIcon, QAction
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
import random
import time
import psutil


class PetWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config

        # 设置窗口无边框、置顶和透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口图标（favicon.ico）
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "favicon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.animation_timer = QTimer()

        # 主窗口部件和布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)  # 水平布局
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 信息显示部件（右侧）
        self.info_widget = QWidget()
        self.info_widget.setFixedSize(150, 100)
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(10, 5, 10, 5)
        self.info_layout.setSpacing(2)

        # 系统信息标签
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("内存: 0%")
        self.network_label = QLabel("网速: 0 KB/s")
        self.hunger_label = QLabel("饥饿值: 100")  # 新增饥饿值标签
        for label in [self.cpu_label, self.memory_label, self.network_label, self.hunger_label]:
            self.info_layout.addWidget(label)

        # 饥饿值机制
        self.hunger = 100  # 初始饥饿值
        self.hunger_timer = QTimer()
        self.hunger_timer.timeout.connect(self.decrease_hunger)
        self.hunger_timer.start(2000)
        self.is_hungry_playing = False

        # 动画显示标签（左侧）
        self.animation_label = QLabel()
        self.animation_label.setFixedSize(config.window_width, config.window_height)
        self.animation_label.setAlignment(Qt.AlignCenter)

        # 将动画和信息部件添加到主布局
        self.main_layout.addWidget(self.animation_label)
        self.main_layout.addWidget(self.info_widget)

        # 计算并设置窗口总大小
        total_width = config.window_width + self.info_widget.width() + self.main_layout.spacing()
        total_height = config.window_height
        self.setFixedSize(total_width, total_height)

        music_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "music")

        # 动画资源路径
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "doro")
        self.load_gif_files(base_path)

        self.click_mp3_path = os.path.join(music_path, "music.mp3")
        self.current_state = "normal"

        # 动画缓存
        self.gif_cache = {}

        # 音频播放器初始化
        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_player.setAudioOutput(self.audio_output)

        # 加载初始动画
        self.load_gif_animation()

        # 网络监控初始化
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()

        # 系统监控定时器
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_system_info)
        self.monitor_timer.start(2000)

        # 鼠标交互相关设置
        self.setMouseTracking(True)
        self.old_pos = None
        self.is_dragging = False
        self.info_visible = True

        # Doro移动相关设置
        self.is_moving = False
        self.move_direction = None
        self.move_speed = 3
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_pet)

        # 随机移动定时器
        self.random_move_timer = QTimer()
        self.random_move_timer.timeout.connect(self.start_random_movement)
        # 根据配置决定是否启动随机移动
        if self.config.allow_random_movement:
            self.random_move_timer.start(self.config.random_interval * 1000)

        # 屏幕几何信息
        self.screen_geometry = self.screen().availableGeometry()

        # 应用主题
        self.update_theme()

    # 新增方法：显示关于信息
    def show_about_info(self):
        """显示关于Doro的信息弹窗"""
        about_text = """Doro 桌宠使用指南

欢迎使用 Doro 桌宠！


1. 基本交互
   - 拖动: 按住左键拖动动画区域。
   - 双击: 双击动画区域播放特殊动画。
   - 右键菜单: 点击动画区域弹出菜单。
     - 喂食哦润吉 🍊: 恢复饥饿值。
     - 关于Doro: 显示此指南。

2. 主要功能
   - 动画: 多种状态动画。
   - 随机移动: 不时在屏幕上走动。
   - 系统信息: 显示 CPU、内存、网速。
   - 主题: 可在设置中更改。

3. 系统托盘图标
   - 右键点击托盘图标可进行显示/隐藏、设置、关闭等操作。

        """
        # 使用 QMessageBox 显示纯文本信息
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("关于 Doro 宠物")
        msg_box.setText(about_text)
        # 可选：设置图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "favicon.ico")
        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path)) # 为弹窗也设置图标
        msg_box.setStandardButtons(QMessageBox.Ok) # 只显示“确定”按钮
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fdf5fe; /* 淡灰色背景 */
            }
            QLabel { /* 调整文本标签样式 */
                color: #ef5aad; /* 深灰色文本 */
                font-size: 13px; /* 稍大字体 */
            }
            QPushButton { /* 按钮样式 */
                background-color: #f771c8;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #f282cb;
            }
        """)
        msg_box.exec() # 显示弹窗

    def load_gif_animation(self):
        """加载并播放随机普通状态GIF"""
        self.play_random_normal_gif()

    def play_gif(self, gif_path):
        """播放指定路径的GIF动画"""
        if not os.path.exists(gif_path):
            print(f"GIF文件不存在: {gif_path}")
            return

        # 停止当前动画
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
            self.animation_label.setMovie(None)

        # 从缓存中获取或创建新动画
        if gif_path not in self.gif_cache:
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(self.config.window_width, self.config.window_height))
            self.gif_cache[gif_path] = movie
        else:
            movie = self.gif_cache[gif_path]

        self.movie = movie
        self.animation_label.setMovie(self.movie)
        self.movie.start()

    def play_random_normal_gif(self):
        """播放随机普通状态GIF"""
        if self.current_state != "normal":
            return
        gif_path = random.choice(self.normal_gif_paths)
        self.play_gif(gif_path)

    def set_info_visible(self, visible):
        """设置信息窗口可见性，并动态调整窗口大小"""
        self.info_visible = visible
        self.info_widget.setVisible(visible)
        # 动态调整窗口宽度，防止信息栏隐藏后动画被挤压
        if visible:
            total_width = self.config.window_width + self.info_widget.width() + self.main_layout.spacing()
        else:
            total_width = self.config.window_width
        total_height = self.config.window_height
        self.setFixedSize(total_width, total_height)

    def decrease_hunger(self):
        """Periodically decrease hunger value"""
        if self.hunger > 0:
            self.hunger -= 1
        self.hunger_label.setText(f"饥饿值: {self.hunger}")
        if 30 > self.hunger > 0 and not self.is_hungry_playing:
            self.is_hungry_playing = True
            self.play_gif(random.choice(self.hungry_gif_paths))
            QTimer.singleShot(800, self.reset_hungry_flag)

    def reset_hungry_flag(self):
        self.is_hungry_playing = False

    def update_system_info(self):
        """更新系统监控信息"""
        if not self.info_visible:
            return

        # CPU使用率
        cpu_usage = psutil.cpu_percent()

        # 内存使用率
        memory_usage = psutil.virtual_memory().percent

        # 网络速度计算
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_net_time

        if time_diff > 0:
            bytes_sent = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
            bytes_recv = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
            total_speed = bytes_sent + bytes_recv

            # 根据速度大小选择合适的单位
            if total_speed < 1024 * 1024:
                speed_str = f"{total_speed / 1024:.1f} KB/s"
            else:
                speed_str = f"{total_speed / (1024 * 1024):.1f} MB/s"

            # 更新标签文本
            self.cpu_label.setText(f"CPU: {cpu_usage}%")
            self.memory_label.setText(f"内存: {memory_usage}%")
            self.network_label.setText(f"网速: {speed_str}")

            # 保存当前网络状态
            self.last_net_io = current_net_io
            self.last_net_time = current_time

    def update_theme(self):
        """更新主题颜色"""
        colors = self.config.get_theme_colors()

        # 设置信息窗口样式
        bg_color = colors['background']
        self.info_widget.setStyleSheet(f"""
            QWidget#PetInfoWindowInfoWidget {{
                background-color: {bg_color};
                border-radius: 10px;
                color: {colors['primary']};
                border: 1px solid {colors['border']};
            }}
            QLabel {{
                color: {colors['primary']};
                font-size: 12px;
                background-color: transparent;
                border: none;
            }}
        """)
        self.info_widget.setObjectName("PetInfoWindowInfoWidget")

    def start_random_movement(self):
        """启动随机移动"""
        if not self.is_moving and not self.is_dragging and random.random() < 0.1 and self.config.allow_random_movement:
            delay = random.randint(5000, 5000)  # 减少移动频率
            QTimer.singleShot(delay, self.prepare_movement)

    def prepare_movement(self):
        """准备移动动画和方向"""
        if self.is_dragging:
            return

        self.current_state = "move"
        self.play_gif(random.choice(self.move_gif_paths))

        # 随机选择移动方向
        self.move_direction = random.choice(["left", "right", "up", "down"])
        self.move_duration = random.randint(5000, 10000)  # 减少移动持续时间
        self.is_moving = True
        self.move_timer.start(50)

        # 设置移动持续时间
        QTimer.singleShot(self.move_duration, self.stop_movement)

    def move_pet(self):
        """执行Doro移动"""
        if not self.is_moving:
            return

        current_pos = self.pos()
        new_pos = current_pos

        # 根据方向移动并处理屏幕边界
        if self.move_direction == "left":
            new_pos += QPoint(-self.move_speed, 0)
            if new_pos.x() < self.screen_geometry.left():
                self.move_direction = "right"
        elif self.move_direction == "right":
            new_pos += QPoint(self.move_speed, 0)
            if new_pos.x() > self.screen_geometry.right() - self.width():
                self.move_direction = "left"
        elif self.move_direction == "up":
            new_pos += QPoint(0, -self.move_speed)
            if new_pos.y() < self.screen_geometry.top():
                self.move_direction = "down"
        elif self.move_direction == "down":
            new_pos += QPoint(0, self.move_speed)
            if new_pos.y() > self.screen_geometry.bottom() - self.height():
                self.move_direction = "up"

        self.move(new_pos)

    def stop_movement(self):
        """停止移动"""
        if self.is_moving:
            self.is_moving = False
            self.move_timer.stop()
            self.return_to_normal()

    def return_to_normal(self):
        """返回普通状态"""
        self.current_state = "normal"
        self.play_random_normal_gif()

    def mousePressEvent(self, event):
        """鼠标按下事件处理（用于拖动窗口和弹出菜单）"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击在动画区域
            if self.animation_label.geometry().contains(event.position().toPoint()):
                self.old_pos = event.globalPosition().toPoint()
                self.is_dragging = True
                self.monitor_timer.stop()
                self.stop_movement()
                # 拖动时切换为 drag.gif
                self.current_state = "drag"
                self.play_gif(self.drag_gif_path)
            else:
                super().mousePressEvent(event)
        elif event.button() == Qt.RightButton:
            # 检查是否点击在动画区域
            if self.animation_label.geometry().contains(event.position().toPoint()):
                # 弹出美观菜单
                menu = QMenu(self)
                # 可选：为菜单设置样式
                menu.setStyleSheet("""
                    QMenu {
                        background-color: #f5f5f5;
                        border: 1px solid #aaa;
                        padding: 8px;
                        font-size: 14px;
                    }
                    QMenu::item {
                        padding: 6px 24px 6px 24px;
                        border-radius: 6px;
                    }
                    QMenu::item:selected {
                        background-color: #87cefa;
                        color: #222;
                    }
                """)
                feed_action = QAction("喂食哦润吉 🍊", self)
                feed_action.triggered.connect(self.feed_pet)
                menu.addAction(feed_action)
                # 可选：添加分隔线和更多选项
                menu.addSeparator()
                info_action = QAction("关于Doro", self)
                info_action.triggered.connect(self.show_about_info) # 连接到更新后的方法
                menu.addAction(info_action)
                # 弹出菜单
                menu.exec(event.globalPosition().toPoint())
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def feed_pet(self):
        """喂食Doro，恢复饱食度并播放吃饭动画"""
        self.current_state = "eat"
        self.play_gif(self.eat_gif_path)
        QTimer.singleShot(5000, self.return_to_normal)
        self.hunger = min(self.hunger + 40, 100)
        self.hunger_label.setText(f"饥饿值: {self.hunger}")

    def mouseMoveEvent(self, event):
        """鼠标移动事件处理（拖动窗口）"""
        if self.old_pos and self.is_dragging:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.old_pos = None
            self.is_dragging = False
            self.monitor_timer.start(2000)
            QTimer.singleShot(3000, self.start_random_movement)
            # 拖动结束恢复普通动画
            self.return_to_normal()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件处理（播放特殊动画或音效）"""
        if event.button() == Qt.LeftButton:
            if self.animation_label.geometry().contains(event.position().toPoint()):
                # 播放点击动画和音效
                self.current_state = "click"
                self.play_gif(self.click_gif_path)
                if os.path.exists(self.click_mp3_path):
                    self.audio_player.setSource(QUrl.fromLocalFile(self.click_mp3_path))
                    self.audio_player.play()
                # 动画播放完后恢复普通状态
                QTimer.singleShot(18000, self.return_to_normal)
            else:
                super().mouseDoubleClickEvent(event)
        else:
            super().mouseDoubleClickEvent(event)

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        # 停止所有动画
        if hasattr(self, 'movie'):
            self.movie.stop()
            self.movie.deleteLater()

        # 停止所有定时器
        self.monitor_timer.stop()
        self.random_move_timer.stop()
        self.move_timer.stop()

        # 清理音频资源
        if hasattr(self, 'audio_player'):
            self.audio_player.stop()
            self.audio_player.deleteLater()
        if hasattr(self, 'audio_output'):
            self.audio_output.deleteLater()

        # 清空缓存
        for movie in self.gif_cache.values():
            movie.stop()
            movie.deleteLater()
        self.gif_cache.clear()

        event.accept()

    def load_gif_files(self, base_path):
        """加载指定路径下的所有GIF文件"""
        if not os.path.exists(base_path):
            print(f"路径不存在: {base_path}")
            return

        # 加载common文件夹中的GIF
        common_path = os.path.join(base_path, "common")
        self.normal_gif_paths = [
            os.path.join(common_path, f)
            for f in os.listdir(common_path)
            if f.endswith(".gif")
        ]

        # 加载move文件夹中的GIF
        move_path = os.path.join(base_path, "move")
        self.move_gif_paths = [
            os.path.join(move_path, f)
            for f in os.listdir(move_path)
            if f.endswith(".gif")
        ]

        self.hungry_gif_paths = self.load_gif_from_folder(os.path.join(base_path, "hungry"))
        self.click_gif_path = os.path.join(base_path, "click", "click.gif")
        self.eat_gif_path = os.path.join(base_path, "eat", "eat.gif")
        self.drag_gif_path = os.path.join(base_path, "drag", "drag.gif")

    def load_gif_from_folder(self, folder_path):
        """从指定文件夹加载所有GIF文件"""
        if not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            return []
        return [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".gif")
        ]
