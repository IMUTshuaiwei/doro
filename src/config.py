import os
import configparser

class Config:
    # 预定义主题
    THEMES = {
        "粉色主题": {
            "primary": "#FF69B4",
            "secondary": "#FFB6C1",
            "background": "#FFF0F5",
            "text": "#333333",
            "border": "rgba(255, 192, 203, 0.5)"
        },
        "蓝色主题": {
            "primary": "#4169E1",
            "secondary": "#87CEEB",
            "background": "#F0F8FF",
            "text": "#333333",
            "border": "rgba(65, 105, 225, 0.5)"
        },
        "紫色主题": {
            "primary": "#9370DB",
            "secondary": "#DDA0DD",
            "background": "#F8F8FF",
            "text": "#333333",
            "border": "rgba(147, 112, 219, 0.5)"
        },
        "绿色主题": {
            "primary": "#2E8B57",
            "secondary": "#98FB98",
            "background": "#F0FFF0",
            "text": "#333333",
            "border": "rgba(46, 139, 87, 0.5)"
        },
        "橙色主题": {
            "primary": "#FF8C00",
            "secondary": "#FFA07A",
            "background": "#FFFAF0",
            "text": "#333333",
            "border": "rgba(255, 140, 0, 0.5)"
        }
    }

    def __init__(self):
        self.config_path = "config.ini"
        self.parser = configparser.ConfigParser()

        # 默认配置
        self.default_config = {
            "WINDOW": {
                "WINDOW_WIDTH": "200",
                "WINDOW_HEIGHT": "200",
            },
            "ANIMATION": {
                "ANIMATION_FPS": "30",
            },
            "RANDOM": {
                "RANDOM_INTERVAL": "5"
            },
            "INFO": {
                "SHOW_INFO": "True"
            },
            "THEME": {
                "CURRENT_THEME": "粉色主题"
            },
            "TRAY": {
                "TRAY_ICON": os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "favicon.ico")
            },
            "WORKSPACE": {
                "ALLOW_RANDOM_MOVEMENT": "True"
            }
        }

        # 如果没有 config.ini 则创建
        if not os.path.exists(self.config_path):
            self._create_default_config()

        self.parser.read(self.config_path, encoding="utf-8")


        # 窗口配置
        self.window_width = self.parser.getint("WINDOW", "WINDOW_WIDTH", fallback=200)
        self.window_height = self.parser.getint("WINDOW", "WINDOW_HEIGHT", fallback=200)

        # 动画配置
        self.animation_fps = self.parser.getint("ANIMATION", "ANIMATION_FPS", fallback=30)
        self.frame_delay = 1000 // self.animation_fps  # 每帧延迟（毫秒）

        # 随机切换配置
        self.random_interval = self.parser.getint("RANDOM", "RANDOM_INTERVAL", fallback=5)  # 秒

        # 信息框配置
        self.show_info = self.parser.getboolean("INFO", "SHOW_INFO", fallback=True)

        # 主题配置
        self.current_theme = self.parser.get("THEME", "CURRENT_THEME", fallback="粉色主题")

        # 托盘配置
        self.tray_icon = self.parser.get("TRAY", "TRAY_ICON", fallback=os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "favicon.ico"))

        # 工作区配置
        self.allow_random_movement = self.parser.getboolean("WORKSPACE", "ALLOW_RANDOM_MOVEMENT", fallback=True)

    def _create_default_config(self):
        for section, options in self.default_config.items():
            self.parser[section] = options
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.parser.write(f)

    def get_theme_colors(self):
        """获取当前主题的颜色"""
        return self.THEMES.get(self.current_theme, self.THEMES["粉色主题"])

    def save(self):
        """保存配置到 config.ini 文件"""
        # 更新 parser 对象
        self.parser.set("WINDOW", "WINDOW_WIDTH", str(self.window_width))
        self.parser.set("WINDOW", "WINDOW_HEIGHT", str(self.window_height))
        self.parser.set("ANIMATION", "ANIMATION_FPS", str(self.animation_fps))
        self.parser.set("RANDOM", "RANDOM_INTERVAL", str(self.random_interval))
        self.parser.set("INFO", "SHOW_INFO", str(self.show_info))
        self.parser.set("THEME", "CURRENT_THEME", self.current_theme)
        self.parser.set("WORKSPACE", "ALLOW_RANDOM_MOVEMENT", str(self.allow_random_movement))
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                self.parser.write(f)
        except Exception as e:
            print(f"保存配置文件时出错: {str(e)}")