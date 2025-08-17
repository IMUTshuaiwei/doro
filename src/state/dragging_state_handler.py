from typing import Optional
from PySide6.QtCore import Qt, QEvent, QTimer, QPoint
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from .base_state import StateHandler


class DraggingStateHandler(StateHandler):
    """拖拽状态处理器"""

    def _init_state(self):
        self.is_dragging = False
        self.old_pos: Optional[QPoint] = None
        self.debounce_drag_end_timer = QTimer()
        self.debounce_drag_end_timer.setSingleShot(True)
        self.debounce_drag_end_timer.timeout.connect(self._real_end_dragging)
        return super()._init_state()

    def on_enter(self):
        if self.is_dragging:
            return False
        self.is_dragging = True
        self.debounce_end_dragging()
        gif_path = self.main_layer.random_gif("Drag")
        if gif_path:
            self.main_layer.pet_window.play_gif(gif_path)
        self.old_pos = None
        self.state_machine.timers["monitor"].stop()
        return True

    def on_exit(self):
        self.is_dragging = False
        self.state_machine.timers["monitor"].start(2000)
        return False

    def debounce_end_dragging(self):
        """请求结束拖拽状态(防抖)"""
        self.debounce_drag_end_timer.start(2000)  # 2000ms防抖

    def _real_end_dragging(self):
        """真正结束拖拽状态"""
        if self.is_dragging:
            self.state_machine.pop_state()

    def handle_event(self, event: QEvent) -> bool:
        if isinstance(event, QMouseEvent):
            self.debounce_end_dragging()
            if event.type() == QEvent.Type.MouseButtonPress:
                return self._handle_mouse_press(event)
            elif event.type() == QEvent.Type.MouseMove:
                return self._handle_mouse_move(event)
            elif event.type() == QEvent.Type.MouseButtonRelease:
                return self._handle_mouse_release(event)
        return False

    def update_config(self):
        return super().update_config()

    def _handle_mouse_press(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            return True
        return False

    def _handle_mouse_move(self, event: QMouseEvent) -> bool:
        if not self.is_dragging:
            return False

        if not self.old_pos:
            self.old_pos = event.globalPos()
            return True

        current_pos = event.globalPos()
        delta = current_pos - self.old_pos
        new_pos = self.main_layer.pet_window.pos() + delta

        # 多显示器适配
        screen_geometry = QApplication.screenAt(current_pos).availableGeometry()
        new_pos.setX(
            max(
                screen_geometry.left(),
                min(
                    new_pos.x(),
                    screen_geometry.right() - self.main_layer.pet_window.width(),
                ),
            )
        )
        new_pos.setY(
            max(
                screen_geometry.top(),
                min(
                    new_pos.y(),
                    screen_geometry.bottom() - self.main_layer.pet_window.height(),
                ),
            )
        )

        self.main_layer.pet_window.move(new_pos)
        self.old_pos = current_pos
        return True

    def _handle_mouse_release(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.state_machine.pop_state()
            return True
        return False
