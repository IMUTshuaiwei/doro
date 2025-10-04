import os
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QMouseEvent, QIcon
from PySide6.QtWidgets import QMessageBox, QApplication
from ..setting_gui import SettingsDialog
from .base_state import StateHandler, menu_item, PetState
from ..style_sheet import (
    generate_messagebox_css,
)
from ..setting_gui import SettingsDialog
from ..pages import get_page


@menu_item("关于Doro", "handle_about", isGlobal=0)
@menu_item("设置", "handle_settings", separator=True, isGlobal=1)
@menu_item("退出桌宠", "handle_quit", isGlobal=1)
class NormalStateHandler(StateHandler):
    """正常状态处理器"""

    def _init_state(self):
        self.normal_timer = QTimer()
        self.normal_timer.timeout.connect(self.change_gif)
        return super()._init_state()

    def on_enter(self):
        self.normal_timer.start(
            1000 * self.main_layer.config.config["Random"]["Interval"]
        )
        gif_path = self.main_layer.random_gif("Common")
        if gif_path:
            self.main_layer.pet_window.play_gif(gif_path)

    def on_exit(self):
        self.normal_timer.stop()
        return super().on_exit()

    def handle_event(self, event: QEvent) -> bool:
        if isinstance(event, QMouseEvent):
            if event.type() == QEvent.Type.MouseButtonPress:
                return self._handle_mouse_press(event)
            elif event.type() == QEvent.Type.MouseButtonDblClick:
                return self._handle_double_click(event)
        return False

    def update_config(self):
        self.normal_timer.stop()
        self.normal_timer.start(
            1000 * self.main_layer.config.config["Random"]["Interval"]
        )
        return super().update_config()

    def _handle_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.state_machine.transition_to(PetState.DRAGGING)
            return True
        return False

    def _handle_double_click(self, event: QMouseEvent) -> bool:
        """处理鼠标双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.state_machine.transition_to(PetState.CLICKED)
            return True
        return False

    def change_gif(self):
        if self.state_machine.current_state == PetState.NORMAL:
            gif_path = self.main_layer.random_gif("Common")
            if gif_path:
                self.main_layer.pet_window.play_gif(gif_path)

    def handle_about(self):
        """处理关于"""
        self.show_about_info()

    def handle_settings(self):
        """处理设置"""
        self.show_settings()

    def handle_quit(self):
        print("Doro will miss you!")

        # 获取程序实例
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.main_layer.config, self.main_layer.pet_window)
        dialog.exec()

    def show_about_info(self):
        """显示关于信息"""
        about_text = get_page("about.html")
        msg_box = QMessageBox(self.main_layer.pet_window)
        msg_box.setWindowTitle("关于 Doro 宠物")
        msg_box.setText(about_text)
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "favicon.ico"
        )
        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet(generate_messagebox_css())
        msg_box.exec()
