import random
from typing import Literal, Optional
from PySide6.QtCore import QTimer, QEvent, Qt, QPoint
from PySide6.QtGui import QMouseEvent
from .base_state import StateHandler, PetState


class MovingStateHandler(StateHandler):
    """移动状态处理器"""

    def _init_state(self):
        # 开始定时器
        self.random_start_timer = QTimer()
        self.random_start_timer.timeout.connect(self.start_random_movement)
        # 根据配置决定是否启动随机移动
        if self.main_layer.config.config["Workspace"]["AllowRandomMovement"]:
            self.random_start_timer.start(
                self.main_layer.config.config["Random"]["Interval"] * 1000
            )

        # 移动计时器
        self.is_moving = False
        self.move_direction: Optional[Literal["left", "right", "up", "down"]] = None
        self.move_speed = 3  # 速度
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_pet)

        # 停止计时器
        self.stop_timer = QTimer()
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.stop_movement)

        return super()._init_state()

    def on_enter(self):
        if not self.check_can_random_move():
            return False
        self.prepare_movement()

    def on_exit(self):
        self.stop_timer.stop()
        self.move_timer.stop()
        self.is_moving = False
        return

    def handle_event(self, event: QEvent) -> bool:
        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonPress
        ):
            if event.button() == Qt.MouseButton.LeftButton:
                self.state_machine.transition_to(PetState.DRAGGING)
                return True
        return False

    def update_config(self):
        self.random_start_timer.stop()
        self.random_start_timer.start(
            int(self.main_layer.config.config["Random"]["Interval"] * 1000)
        )
        if self.state_machine.current_state == PetState.MOVING:
            self.state_machine.pop_state()
        return super().update_config()

    def check_can_random_move(self):
        """检查是否可以随机移动"""
        return (
            self.state_machine.current_state in [PetState.NORMAL]
            and self.main_layer.config.config["Workspace"]["AllowRandomMovement"]
        )

    def start_random_movement(self):
        """启动随机移动"""
        if (
            not self.is_moving
            and random.random() < 0.1
            and self.check_can_random_move()
        ):
            self.state_machine.transition_to(PetState.MOVING)

    def prepare_movement(self):
        """准备移动动画和方向，自动适配 GIF 方向"""
        self.move_direction = random.choice(["left", "right", "up", "down"])
        move_gif = self.main_layer.random_gif("Move")

        # 右移时镜像
        mirror = self.move_direction == "right"
        if move_gif:
            self.main_layer.pet_window.play_gif(move_gif, mirror=mirror)

        move_duration = random.randint(5000, 10000)
        self.is_moving = True
        self.move_timer.start(50)
        self.stop_timer.start(move_duration)

    def stop_movement(self):
        """停止移动"""
        if self.state_machine.current_state == PetState.MOVING:
            self.state_machine.pop_state()

    def move_pet(self):
        """移动宠物"""
        if not self.move_direction:
            return

        current_pos = self.main_layer.pet_window.pos()
        new_pos = current_pos

        if self.move_direction == "left":
            new_pos += QPoint(-self.move_speed, 0)
            if new_pos.x() < self.main_layer.pet_window.screen_geometry.left():
                self.move_direction = "right"
        elif self.move_direction == "right":
            new_pos += QPoint(self.move_speed, 0)
            if (
                new_pos.x()
                > self.main_layer.pet_window.screen_geometry.right()
                - self.main_layer.pet_window.width()
            ):
                self.move_direction = "left"
        elif self.move_direction == "up":
            new_pos += QPoint(0, -self.move_speed)
            if new_pos.y() < self.main_layer.pet_window.screen_geometry.top():
                self.move_direction = "down"
        elif self.move_direction == "down":
            new_pos += QPoint(0, self.move_speed)
            if (
                new_pos.y()
                > self.main_layer.pet_window.screen_geometry.bottom()
                - self.main_layer.pet_window.height()
            ):
                self.move_direction = "up"

        self.main_layer.pet_window.move(new_pos)
