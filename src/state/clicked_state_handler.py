import os
from PySide6.QtCore import QTimer, QUrl, QEvent, Qt
from PySide6.QtGui import QMouseEvent

from ..config import Config
from .base_state import PetState, StateHandler


class ClickedStateHandler(StateHandler):
    """点击状态处理器"""

    def _init_state(self):
        self.click_end_timer = QTimer()
        self.click_end_timer.setSingleShot(True)
        self.click_end_timer.timeout.connect(self._on_click_end)
        return super()._init_state()

    def on_enter(self):
        gif_path = self.main_layer.random_gif("Click")
        if gif_path:
            self.main_layer.pet_window.play_gif(gif_path)
        if os.path.exists(Config.PATH_CONFIG["Resources"]["Music"]["DoubleClick"]):
            self.main_layer.pet_window.audio_player.setSource(
                QUrl.fromLocalFile(self.main_layer.random_music("DoubleClick") or "")
            )
            self.main_layer.pet_window.audio_player.play()
            self.click_end_timer.start(18000)

    def on_exit(self):
        self.click_end_timer.stop()
        self.main_layer.pet_window.audio_player.stop()
        return False

    def handle_event(self, event: QEvent) -> bool:
        if isinstance(event, QMouseEvent):
            if event.type() == QEvent.Type.MouseButtonPress:
                return self._handle_mouse_press(event)
        return False

    def update_config(self):
        return super().update_config()

    def _handle_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.state_machine.transition_to(PetState.DRAGGING)
            return True
        return False

    def _on_click_end(self):
        """点击动画结束"""
        if self.state_machine.current_state == PetState.CLICKED:
            self.state_machine.pop_state()
