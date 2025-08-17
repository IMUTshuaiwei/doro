import random
from ..system_tray import SystemTray
from ..config import Config
from ..ResourceManager import ResourceManager
from ..pet_window import PetWindow
from ..auto_typehint import GifHint, MusicHint


class MainLayer:
    """全局管理层"""

    def __init__(self) -> None:
        self.config: Config = Config(self)
        self.resource_manager: ResourceManager = ResourceManager(
            Config.PATH_CONFIG["Resources"], self
        )
        self.pet_window: PetWindow = PetWindow(self.config, self)
        self.system_tray: SystemTray = SystemTray(self.pet_window, self.config, self)

    # ---------------- 资源统一接口封装 ----------------
    def get_gif(
        self, key: GifHint.GifDirLiteral
    ):  # 具体字面量类型在 ResourceManager 已声明
        return self.resource_manager.get_gif(key)

    def get_all_gif(self):
        return self.resource_manager.get_all_gif()

    def get_music(self, key: MusicHint.MusicDirLiteral):
        return self.resource_manager.get_music(key)

    def get_all_music(self):
        return self.resource_manager.get_all_music()

    # 常用便捷接口
    def random_gif(self, key: GifHint.GifDirLiteral):
        files = self.get_gif(key)
        if files:
            return random.choice(files)
        return None

    def random_music(self, key: MusicHint.MusicDirLiteral):
        files = self.get_music(key)
        if files:
            return random.choice(files)
        return None


__all__ = [
    "MainLayer",
]
