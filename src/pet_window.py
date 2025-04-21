from PySide6.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QPushButton, QScrollArea,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPoint, QSize, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QFont, QMovie
import os
import random
import time
import psutil
from .deepseek_client import DeepSeekClient

class ChatDialog(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Tool | 
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint  # 添加置顶标志
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 500)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题栏
        title_layout = QHBoxLayout()
        self.title_label = QLabel("DORO")
        title_layout.addWidget(self.title_label)
        
        # 关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                font-size: 20px;
                border: none;
            }
        """)
        close_button.clicked.connect(self.hide)
        title_layout.addWidget(close_button)
        
        main_layout.addLayout(title_layout)
        
        # 聊天记录区域
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        main_layout.addWidget(self.chat_area)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(60)
        self.input_box.setPlaceholderText("输入消息...")
        input_layout.addWidget(self.input_box)
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFixedWidth(80)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        # 鼠标跟踪
        self.setMouseTracking(True)
        self.old_pos = None
        
        # 设置样式
        self.update_theme()
        
        # 添加调试信息
        print("ChatDialog initialized")
        
    def update_theme(self):
        """更新主题样式"""
        colors = self.parent().config.get_theme_colors()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['background']};
                border-radius: 15px;
                border: 1px solid {colors['border']};
            }}
            QTextEdit {{
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid {colors['border']};
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: {colors['text']};
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {colors['primary']};
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(255, 255, 255, 0.5);
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['primary']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        self.title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {colors['primary']};")
        
    def show(self):
        """显示对话框"""
        super().show()
        print("ChatDialog shown")
        
    def hide(self):
        """隐藏对话框"""
        super().hide()
        print("ChatDialog hidden")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.old_pos = None
        
    def add_message(self, sender, message, is_user=True):
        """添加消息到聊天记录"""
        colors = self.parent().config.get_theme_colors()
        color = colors['primary'] if is_user else colors['secondary']
        alignment = "right" if is_user else "left"
        self.chat_area.append(f"""
            <div style='margin: 10px; text-align: {alignment};'>
                <div style='color: {color}; font-weight: bold;'>{sender}</div>
                <div style='background-color: rgba(0, 0, 0, 0.05); padding: 10px; border-radius: 10px; margin-top: 5px;'>
                    {message}
                </div>
            </div>
        """)
        # 滚动到底部
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )

class PetWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.deepseek_client = DeepSeekClient(config)
        
        # 连接信号
        self.deepseek_client.response_received.connect(self.handle_response)
        self.deepseek_client.error_occurred.connect(self.handle_error)
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.Tool  # 不在任务栏显示
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建主窗口部件
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 创建信息显示框
        self.info_widget = QWidget()
        self.info_widget.setFixedSize(150, 100)
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(10, 5, 10, 5)
        self.info_layout.setSpacing(2)
        
        # 创建信息标签
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("内存: 0%")
        self.network_label = QLabel("网速: 0 KB/s")
        
        # 设置标签样式
        for label in [self.cpu_label, self.memory_label, self.network_label]:
            self.info_layout.addWidget(label)
            
        # 创建动画标签
        self.animation_label = QLabel()
        self.animation_label.setFixedSize(config.window_width, config.window_height)
        self.animation_label.setAlignment(Qt.AlignCenter)
        
        # 添加部件到主布局
        self.main_layout.addWidget(self.animation_label)
        self.main_layout.addWidget(self.info_widget, 0, Qt.AlignRight | Qt.AlignTop)
        
        # 创建对话窗口
        self.chat_dialog = ChatDialog(self)
        self.chat_dialog.send_button.clicked.connect(self.send_message)
        print("ChatDialog created")
        
        # 设置窗口大小
        self.setFixedSize(config.window_width, config.window_height)
        
        # 加载GIF动画
        self.load_gif_animation()
        
        # 系统监控
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()
        
        # 设置定时器
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_system_info)
        self.monitor_timer.start(1000)
        
        # 鼠标跟踪
        self.setMouseTracking(True)
        self.old_pos = None
        
        # 信息框显示状态
        self.info_visible = True
        
        # 显示对话窗口
        if self.config.enable_chat:
            self.show_chat_dialog()
            
        # 更新主题
        self.update_theme()
        
    def load_gif_animation(self):
        """加载GIF动画"""
        gif_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "doro", "doro-nikke-unscreen.gif")
        if os.path.exists(gif_path):
            print(f"正在加载GIF动画: {gif_path}")
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(self.config.window_width, self.config.window_height))
            self.animation_label.setMovie(self.movie)
            self.movie.start()
            print("GIF动画加载完成")
        else:
            print(f"错误: GIF文件不存在: {gif_path}")
            
    def show_chat_dialog(self):
        """显示对话窗口"""
        self.chat_dialog.move(
            self.pos().x() + self.width(),
            self.pos().y()
        )
        self.chat_dialog.show()
        print("ChatDialog shown")
        
    def set_info_visible(self, visible):
        """设置信息框显示状态"""
        self.info_visible = visible
        self.info_widget.setVisible(visible)
        
    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        if event.button() == Qt.LeftButton:
            # 双击时切换对话窗口的显示状态
            if self.chat_dialog.isVisible():
                self.chat_dialog.hide()
            else:
                self.show_chat_dialog()
                
    def send_message(self):
        """发送消息到DeepSeek"""
        message = self.chat_dialog.input_box.toPlainText().strip()
        if not message:
            return
            
        print(f"Sending message: {message}")
        
        # 添加用户消息到聊天记录
        self.chat_dialog.add_message("你", message, True)
        self.chat_dialog.input_box.clear()
        
        # 发送消息到DeepSeek
        self.deepseek_client.send_message(message)
        
    def handle_response(self, response):
        """处理API响应"""
        print(f"Received response: {response}")
        self.chat_dialog.add_message("桌宠", response, False)
        
    def handle_error(self, error):
        """处理错误信息"""
        print(f"Error: {error}")
        self.chat_dialog.add_message("系统", error, False)
        
    def set_chat_enabled(self, enabled):
        """设置对话功能是否启用"""
        self.config.enable_chat = enabled
        self.config.save()
        
        if enabled:
            self.show_chat_dialog()
        else:
            self.chat_dialog.hide()
        
    def update_system_info(self):
        """更新系统信息显示"""
        if not self.info_visible:
            return
            
        # 更新CPU和内存使用率
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        # 计算网速
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_net_time
        
        if time_diff > 0:
            bytes_sent = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
            bytes_recv = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
            total_speed = (bytes_sent + bytes_recv) / 1024  # 转换为KB/s
            
            self.cpu_label.setText(f"CPU: {cpu_usage}%")
            self.memory_label.setText(f"内存: {memory_usage}%")
            self.network_label.setText(f"网速: {total_speed:.1f} KB/s")
            
            self.last_net_io = current_net_io
            self.last_net_time = current_time
            
    def update_theme(self):
        """更新主题样式"""
        colors = self.config.get_theme_colors()
        self.info_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['background']};
                border-radius: 10px;
                color: {colors['primary']};
                border: 1px solid {colors['border']};
            }}
            QLabel {{
                color: {colors['primary']};
                font-size: 12px;
            }}
        """)
        self.chat_dialog.update_theme() 

    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.is_dragging = True
            self.monitor_timer.stop()    # 暂停系统监控
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.old_pos and self.is_dragging:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            self.is_dragging = False
            self.monitor_timer.start(1000)  # 恢复系统监控 