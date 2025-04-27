import os
from typing import Any, Dict, Literal, Optional

from .utils.FileIO import json_dump, json_load
from .const_hint import ConfigParam, StyleSheetParam


class Config:
    # 预定义主题
    PATH_CONFIG: Dict[str, Dict[str, str]] = json_load(
        "resources/config/file_index.json"
    )
    THEMES: StyleSheetParam = json_load(PATH_CONFIG["THEME"]["RELATIVE_PATH"])

    def __init__(self):
        self._config: Optional[ConfigParam] = json_load(
            Config.PATH_CONFIG["CONFIG"]["RELATIVE_PATH"]
        )

        # 托盘配置
        default_ico_path: str = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "resources",
            "icons",
            "favicon.ico",
        )
        self.tray_icon: str = self.config["TRAY"].get(
            "TRAY_ICON"
        ) or Config.PATH_CONFIG["ICON"].get("RELATIVE_PATH", default_ico_path)

        # 工作区配置
        self.allow_random_movement: bool = self.config["WORKSPACE"].get(
            "ALLOW_RANDOM_MOVEMENT", True
        )

    @property
    def config(self) -> ConfigParam:
        """获取当前配置项"""
        if self._config is None:
            self._config = json_load(
                Config.PATH_CONFIG["CONFIG"]["RELATIVE_PATH"], replace=True
            )

        if self._config is None:
            self._config = self._read_default_config()
            self.save()

        return self._config

    def _read_default_config(self) -> ConfigParam:
        return json_load(
            Config.PATH_CONFIG["DEFAULT_CONFIG"]["RELATIVE_PATH"],
            replace=True,
        )

    def get_theme_colors(
        self,
    ) -> StyleSheetParam:
        """获取当前主题的颜色"""
        return StyleSheetParam(
            Config.THEMES.get(self.config["THEME"]["DEFAULT_THEME"], {})
        )

    def get(
        self,
        key: Literal[
            "WINDOW",
            "ANIMATION",
            "RANDOM",
            "INFO",
            "THEME",
            "TRAY",
            "WORKSPACE",
        ],
    ) -> Dict[str, Any]:
        """获取配置项的值"""
        return self.config.get(key, None) or {}

    def save(self):
        json_dump(Config.PATH_CONFIG["CONFIG"]["RELATIVE_PATH"], self.config)
