from PySide6.QtCore import QTimer, QEvent, Qt
from PySide6.QtGui import QMouseEvent
from .base_state import StateHandler, PetState


class EatingStateHandler(StateHandler):
    """进食状态处理器"""

    def _init_state(self):
        self.eating_end_timer = QTimer()
        self.eating_end_timer.setSingleShot(True)
        self.eating_end_timer.timeout.connect(self._on_eating_end)
        return super()._init_state()

    def on_enter(self):
        self.eating_end_timer.start(3000)
        gif_path = self.main_layer.random_gif("Eat")
        if gif_path:
            self.main_layer.pet_window.play_gif(gif_path)

    def on_exit(self):
        self.eating_end_timer.stop()
        return super().on_exit()

    def handle_event(self, event: QEvent) -> bool:
        if isinstance(event, QMouseEvent):
            if event.type() == QEvent.Type.MouseButtonPress:
                return self._handle_mouse_press(event)
            elif event.type() == QEvent.Type.MouseButtonDblClick:
                return self._handle_double_click(event)
        return False

    def update_config(self):
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

    def _on_eating_end(self):
        """进食结束"""
        if self.state_machine.current_state == PetState.EATING:
            self.state_machine.pop_state()
