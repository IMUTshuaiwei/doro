import os

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QHBoxLayout,
    QFormLayout,
    QCheckBox,
    QMessageBox,
    QComboBox,
)

from .config import Config
from .const_hint import StyleSheetParam
from .pet_window import PetWindow
from .style_sheet import generate_preview_css, generate_full_css


class SettingsDialog(QDialog):

    def __init__(self, config: Config, parent: PetWindow):
        super().__init__(parent)
        self.config: Config = config
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
        for theme_name in self.config.THEMES.keys():
            self.theme_combo.addItem(theme_name)
        self.theme_combo.setCurrentText(self.config.config["THEME"]["DEFAULT_THEME"])
        self.theme_combo.currentTextChanged.connect(self.theme_changed)
        theme_layout.addWidget(self.theme_combo)

        # 主题预览
        self.theme_preview = QLabel()
        self.theme_preview.setFixedSize(30, 30)
        self.theme_preview.setStyleSheet(
            generate_preview_css(self.config.get_theme_colors())
        )
        theme_layout.addWidget(self.theme_preview)

        form_layout.addRow("主题:", theme_layout)

        # 宠物大小设置
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 1000)
        self.width_spin.setValue(config.config["WINDOW"]["WINDOW_WIDTH"])
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 1000)
        self.height_spin.setValue(config.config["WINDOW"]["WINDOW_HEIGHT"])
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.height_spin)
        form_layout.addRow("宠物大小:", size_layout)

        # 帧率设置
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(config.config["ANIMATION"]["ANIMATION_FPS"])
        form_layout.addRow("动画帧率 (FPS):", self.fps_spin)

        # 随机切换时间设置
        self.random_interval_spin = QSpinBox()
        self.random_interval_spin.setRange(1, 60)
        self.random_interval_spin.setValue(config.config["RANDOM"]["RANDOM_INTERVAL"])
        self.random_interval_spin.setSuffix(" 秒")
        form_layout.addRow("随机切换间隔:", self.random_interval_spin)

        # 信息框显示设置
        self.show_info_checkbox = QCheckBox()
        self.show_info_checkbox.setChecked(config.config["INFO"]["SHOW_INFO"])
        form_layout.addRow("显示系统信息:", self.show_info_checkbox)

        # 随机移动设置
        self.allow_random_movement_checkbox = QCheckBox()
        self.allow_random_movement_checkbox.setChecked(
            config.config["WORKSPACE"]["ALLOW_RANDOM_MOVEMENT"]
        )
        form_layout.addRow("允许自主随机运动:", self.allow_random_movement_checkbox)

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
        colors: StyleSheetParam = self.config.get_theme_colors()
        self.setStyleSheet(generate_full_css(colors))

    def theme_changed(self, theme_name: str):
        """主题改变时的处理"""
        self.config.config["THEME"]["DEFAULT_THEME"] = theme_name
        self.update_theme()
        self.theme_preview.setStyleSheet(
            generate_preview_css(self.config.get_theme_colors())
        )

    def save_settings(self):
        """保存设置"""
        # 更新配置
        self.config.get("WINDOW")["WINDOW_WIDTH"] = self.width_spin.value()
        self.config.get("WINDOW")["WINDOW_HEIGHT"] = self.height_spin.value()
        self.config.get("ANIMATION")["ANIMATION_FPS"] = self.fps_spin.value()
        self.config.get("THEME")["DEFAULT_THEME"] = self.theme_combo.currentText()
        self.config.get("RANDOM")["RANDOM_INTERVAL"] = self.random_interval_spin.value()
        self.config.get("INFO")["SHOW_INFO"] = self.show_info_checkbox.isChecked()
        self.config.get("WORKSPACE")[
            "ALLOW_RANDOM_MOVEMENT"
        ] = self.allow_random_movement_checkbox.isChecked()
        # 保存到环境变量文件
        self.config.save()

        parent_window: PetWindow = self.parent()  # type: ignore[assignment]

        # 更新窗口大小
        parent_window.setFixedSize(
            self.config.config["WINDOW"]["WINDOW_WIDTH"],
            self.config.config["WINDOW"]["WINDOW_HEIGHT"],
        )

        # 更新动画帧率
        parent_window.animation_timer.setInterval(
            1000 // self.config.config["ANIMATION"]["ANIMATION_FPS"]
        )

        # 更新随机切换间隔
        parent_window.random_move_timer.setInterval(
            self.config.config["RANDOM"]["RANDOM_INTERVAL"] * 1000
        )

        # 更新信息框显示状态
        parent_window.set_info_visible(self.config.config["INFO"]["SHOW_INFO"])

        # 更新对话功能状态
        # TODO: 这里原版本里是有这个的, 但似乎并未实现(NotImplemented)
        # parent_window.set_chat_enabled(self.config.enable_chat)

        # 更新主题
        parent_window.update_theme()

        # 显示保存成功提示
        QMessageBox.information(self, "提示", "设置已保存！")

        # 关闭对话框
        self.close()


class SystemTray:

    def __init__(self, pet_window: PetWindow, config: Config) -> None:
        self.pet_window: PetWindow = pet_window
        self.config: Config = config

        # 创建系统托盘图标
        self.tray_icon: QSystemTrayIcon = QSystemTrayIcon()

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

    def show_tray_icon(self):
        """显示托盘图标"""
        self.tray_icon.show()

    def hide_tray_icon(self):
        """隐藏托盘图标"""
        self.tray_icon.hide()

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
        os._exit(0)
