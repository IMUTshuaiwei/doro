from PySide6.QtCore import QTimer, QEvent, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel
from .base_state import StateHandler, menu_item, PetState


@menu_item("喂食哦润吉 🍊", "handle_feed", isGlobal=0)
class HungryStateHandler(StateHandler):
    """饥饿状态处理器"""

    def _init_state(self):
        """初始化饥饿状态特定的资源"""
        # 创建饥饿标签
        self.hunger_label = QLabel("饥饿值: 100")
        self.hunger_timer = QTimer()
        self.hunger_timer.timeout.connect(self._update_hunger)
        self.hunger_number = 100
        self.hunger_rate = self.main_layer.config.config["Hunger"]["Rate"]
        self.hunger_timer.start(int(20000 / self.hunger_rate))

        # 注册到状态机的UI组件
        self.state_machine.register_ui_component("hunger_label", self.hunger_label)

    def is_hunger(self):
        """是否到达饥饿状态"""
        return 30 > self.hunger_number >= 0

    def on_enter(self):
        if not self.is_hunger():
            return False
        elif self.state_machine.state_stack[-1] == PetState.DRAGGING:
            return False
        gif_path = self.main_layer.random_gif("Hungry")
        if gif_path:
            self.main_layer.pet_window.play_gif(gif_path)

    def on_exit(self):
        return super().on_exit()

    def handle_event(self, event: QEvent) -> bool:
        if isinstance(event, QMouseEvent):
            if event.type() == QEvent.Type.MouseButtonPress:
                return self._handle_mouse_press(event)
        return False

    def _handle_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.state_machine.transition_to(PetState.DRAGGING)
            return True
        return False

    def _update_hunger(self):
        """更新饥饿度"""
        if self.hunger_rate != self.main_layer.config.config["Hunger"]["Rate"]:
            self.hunger_rate = self.main_layer.config.config["Hunger"]["Rate"]
            self.hunger_timer.stop()
            self.hunger_timer.start(int(20000 / self.hunger_rate))
            return
        if self.hunger_number > 0:
            self.hunger_number -= 1
        self.hunger_label.setText(f"饥饿值: {self.hunger_number}")

        if self.is_hunger() and self.state_machine.current_state not in [
            PetState.HUNGRY,
            PetState.DRAGGING,
        ]:
            self.state_machine.transition_to(PetState.HUNGRY)

    def handle_feed(self):
        """处理喂食"""
        self.state_machine.transition_to(PetState.EATING)
        self.hunger_number += 40
        if self.hunger_number > 100:
            self.hunger_number = 100
        self.hunger_label.setText(f"饥饿值: {self.hunger_number}")

    def update_config(self):
        return super().update_config()
