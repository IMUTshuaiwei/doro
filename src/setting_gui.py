from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from .auto_typehint import ThemeHint
from .config import Config
from .style_sheet import generate_full_css, generate_preview_css

if TYPE_CHECKING:
    from .pet_window import PetWindow  # 仅用于类型检查，不会实际导入


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent: Optional["PetWindow"] = None):
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
        self.theme_combo.setCurrentText(self.config.config["Theme"]["DefaultTheme"])
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
        self.width_spin.setValue(config.config["Window"]["Width"])
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 1000)
        self.height_spin.setValue(config.config["Window"]["Height"])
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.height_spin)
        form_layout.addRow("宠物大小:", size_layout)

        # 随机切换时间设置
        self.random_interval_spin = QSpinBox()
        self.random_interval_spin.setRange(1, 60)
        self.random_interval_spin.setValue(config.config["Random"]["Interval"])
        self.random_interval_spin.setSuffix(" 秒")
        form_layout.addRow("随机切换间隔:", self.random_interval_spin)

        self.hunger_rate_spin = QSpinBox()
        self.hunger_rate_spin.setRange(1, 10)
        self.hunger_rate_spin.setValue(int(config.config["Hunger"]["Rate"]))
        form_layout.addRow("饥饿值倍率:", self.hunger_rate_spin)

        # 信息框显示设置
        self.show_info_checkbox = QCheckBox()
        self.show_info_checkbox.setChecked(config.config["Info"]["ShowInfo"])
        form_layout.addRow("显示系统信息:", self.show_info_checkbox)

        # 随机移动设置
        self.allow_random_movement_checkbox = QCheckBox()
        self.allow_random_movement_checkbox.setChecked(
            config.config["Workspace"]["AllowRandomMovement"]
        )
        form_layout.addRow("允许自主随机运动:", self.allow_random_movement_checkbox)

        # 置顶窗口设置
        self.always_on_top_checkbox = QCheckBox()
        self.always_on_top_checkbox.setChecked(
            self.config.config["Window"]["StaysOnTop"]
        )
        form_layout.addRow("窗口置顶:", self.always_on_top_checkbox)

        # 窗口模式设置
        self.window_mode_checkbox = QCheckBox()
        self.window_mode_checkbox.setChecked(self.config.config["Window"]["Frameless"])
        form_layout.addRow("无边框模式:", self.window_mode_checkbox)

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
        colors: ThemeHint.ThemeParam = self.config.get_theme_colors()
        self.setStyleSheet(generate_full_css(colors))

    def theme_changed(self, theme_name: str):
        """主题改变时的处理"""
        self.config.config["Theme"]["DefaultTheme"] = theme_name
        self.update_theme()
        self.theme_preview.setStyleSheet(
            generate_preview_css(self.config.get_theme_colors())
        )

    def save_settings(self):
        """保存设置"""
        # 更新配置
        self.config.config["Window"]["Width"] = self.width_spin.value()
        self.config.config["Window"]["Height"] = self.height_spin.value()
        self.config.config["Window"][
            "StaysOnTop"
        ] = self.always_on_top_checkbox.isChecked()
        self.config.config["Window"][
            "Frameless"
        ] = self.window_mode_checkbox.isChecked()
        self.config.config["Theme"]["DefaultTheme"] = self.theme_combo.currentText()
        self.config.config["Random"]["Interval"] = self.random_interval_spin.value()
        self.config.config["Hunger"]["Rate"] = self.hunger_rate_spin.value()
        self.config.config["Info"]["ShowInfo"] = self.show_info_checkbox.isChecked()
        self.config.config["Workspace"][
            "AllowRandomMovement"
        ] = self.allow_random_movement_checkbox.isChecked()
        # 保存到环境变量文件
        self.config.save()

        self.parent_window: PetWindow = self.parent()  # type: ignore[assignment]

        # # 更新随机切换间隔
        # parent_window.random_move_timer.setInterval(
        #     self.config.config["Random"]["Interval"] * 1000
        # )

        # 更新对话功能状态
        # TODO: 这里原版本里是有这个的, 但似乎并未实现(NotImplemented)
        # parent_window.set_chat_enabled(self.config.enable_chat)

        self.parent_window.update_config()

        # 显示保存成功提示
        QMessageBox.information(self, "提示", "设置已保存！")

        # 关闭对话框
        self.close()
