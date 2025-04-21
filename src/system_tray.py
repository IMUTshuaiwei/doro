from PySide6.QtWidgets import (
    QSystemTrayIcon, QMenu, QDialog, QVBoxLayout, 
    QLabel, QPushButton, QLineEdit, QSpinBox, 
    QHBoxLayout, QFormLayout, QCheckBox, QMessageBox, QComboBox
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt
import os

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("设置")
        self.setFixedSize(400, 350)
        
        # 设置对话框样式
        self.update_theme()
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # 主题选择
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.config.THEMES.keys())
        self.theme_combo.setCurrentText(self.config.current_theme)
        self.theme_combo.currentTextChanged.connect(self.theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        # 主题预览
        self.theme_preview = QLabel()
        self.theme_preview.setFixedSize(30, 30)
        self.theme_preview.setStyleSheet(f"""
            background-color: {self.config.get_theme_colors()['primary']};
            border-radius: 15px;
            border: 1px solid {self.config.get_theme_colors()['border']};
        """)
        theme_layout.addWidget(self.theme_preview)
        
        form_layout.addRow("主题:", theme_layout)
        
        # DeepSeek API Key设置
        api_key_layout = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(config.deepseek_api_key)
        self.api_key_edit.setEchoMode(QLineEdit.Password)  # 密码模式显示
        self.api_key_edit.setPlaceholderText("输入新的API Key")
        api_key_layout.addWidget(self.api_key_edit)
        
        # 显示/隐藏API Key按钮
        self.toggle_api_key_button = QPushButton("👁")
        self.toggle_api_key_button.setFixedWidth(30)
        self.toggle_api_key_button.setToolTip("显示/隐藏API Key")
        self.toggle_api_key_button.clicked.connect(self.toggle_api_key_visibility)
        api_key_layout.addWidget(self.toggle_api_key_button)
        
        form_layout.addRow("DeepSeek API Key:", api_key_layout)
        
        # 宠物大小设置
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 1000)
        self.width_spin.setValue(config.window_width)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 1000)
        self.height_spin.setValue(config.window_height)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.height_spin)
        form_layout.addRow("宠物大小:", size_layout)
        
        # 帧率设置
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(config.animation_fps)
        form_layout.addRow("动画帧率 (FPS):", self.fps_spin)
        
        # 随机切换时间设置
        self.random_interval_spin = QSpinBox()
        self.random_interval_spin.setRange(1, 60)
        self.random_interval_spin.setValue(config.random_interval)
        self.random_interval_spin.setSuffix(" 秒")
        form_layout.addRow("随机切换间隔:", self.random_interval_spin)
        
        # 信息框显示设置
        self.show_info_checkbox = QCheckBox()
        self.show_info_checkbox.setChecked(config.show_info)
        form_layout.addRow("显示系统信息:", self.show_info_checkbox)
        
        # 对话窗口设置
        self.enable_chat_checkbox = QCheckBox()
        self.enable_chat_checkbox.setChecked(config.enable_chat)
        form_layout.addRow("启用对话功能:", self.enable_chat_checkbox)
        
        main_layout.addLayout(form_layout)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def update_theme(self):
        """更新主题样式"""
        colors = self.config.get_theme_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
            }}
            QLabel {{
                color: {colors['primary']};
                font-size: 14px;
            }}
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid {colors['border']};
                border-radius: 5px;
                padding: 5px;
                color: {colors['text']};
            }}
            QSpinBox {{
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid {colors['border']};
                border-radius: 5px;
                padding: 5px;
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
            QCheckBox {{
                color: {colors['primary']};
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            QComboBox {{
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid {colors['border']};
                border-radius: 5px;
                padding: 5px;
                color: {colors['text']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['primary']};
                margin-right: 5px;
            }}
        """)
        
    def theme_changed(self, theme_name):
        """主题改变时的处理"""
        self.config.current_theme = theme_name
        self.update_theme()
        self.theme_preview.setStyleSheet(f"""
            background-color: {self.config.get_theme_colors()['primary']};
            border-radius: 15px;
            border: 1px solid {self.config.get_theme_colors()['border']};
        """)
        
    def toggle_api_key_visibility(self):
        """切换API Key的显示/隐藏状态"""
        if self.api_key_edit.echoMode() == QLineEdit.Password:
            self.api_key_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_api_key_button.setText("👁")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.Password)
            self.toggle_api_key_button.setText("👁")
            
    def save_settings(self):
        """保存设置"""
        # 更新配置
        self.config.window_width = self.width_spin.value()
        self.config.window_height = self.height_spin.value()
        self.config.animation_fps = self.fps_spin.value()
        self.config.deepseek_api_key = self.api_key_edit.text()
        self.config.random_interval = self.random_interval_spin.value()
        self.config.show_info = self.show_info_checkbox.isChecked()
        self.config.enable_chat = self.enable_chat_checkbox.isChecked()
        
        # 保存到环境变量文件
        self.config.save()
        
        # 更新窗口大小
        self.parent().setFixedSize(self.config.window_width, self.config.window_height)
        
        # 更新动画帧率
        self.parent().animation_timer.setInterval(1000 // self.config.animation_fps)
        
        # 更新随机切换间隔
        self.parent().random_timer.setInterval(self.config.random_interval * 1000)
        
        # 更新信息框显示状态
        self.parent().set_info_visible(self.config.show_info)
        
        # 更新对话功能状态
        self.parent().set_chat_enabled(self.config.enable_chat)
        
        # 更新主题
        self.parent().update_theme()
        
        # 显示保存成功提示
        QMessageBox.information(self, "提示", "设置已保存！")
        
        # 关闭对话框
        self.close()

class SystemTray:
    def __init__(self, pet_window, config):
        self.pet_window = pet_window
        self.config = config
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon()
        
        # 加载图标
        icon_path = config.tray_icon
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            print(f"警告: 图标文件不存在: {icon_path}")
        
        # 创建托盘菜单
        self.menu = QMenu()
        
        # 添加菜单项
        self.show_action = QAction("显示桌宠", self.menu)
        self.show_action.triggered.connect(self.show_pet)
        self.menu.addAction(self.show_action)
        
        self.hide_action = QAction("隐藏桌宠", self.menu)
        self.hide_action.triggered.connect(self.hide_pet)
        self.menu.addAction(self.hide_action)
        
        self.menu.addSeparator()
        
        self.settings_action = QAction("设置", self.menu)
        self.settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.settings_action)
        
        self.menu.addSeparator()
        
        self.quit_action = QAction("关闭程序", self.menu)
        self.quit_action.triggered.connect(self.quit_application)
        self.menu.addAction(self.quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.menu)
        
        # 显示托盘图标
        self.tray_icon.show()
        
    def show_pet(self):
        """显示桌宠"""
        self.pet_window.show()
        
    def hide_pet(self):
        """隐藏桌宠"""
        self.pet_window.hide()
        
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config, self.pet_window)
        dialog.exec()
        
    def quit_application(self):
        """退出应用程序"""
        self.tray_icon.hide()
        self.pet_window.close() 