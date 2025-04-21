import os
from dotenv import load_dotenv

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
        # 尝试以不同编码加载环境变量
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        for encoding in encodings:
            try:
                load_dotenv(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"加载环境变量时出错: {str(e)}")
                break
        
        # DeepSeek API配置
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.deepseek_api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
        
        # 窗口配置
        self.window_width = int(os.getenv("WINDOW_WIDTH", "300"))
        self.window_height = int(os.getenv("WINDOW_HEIGHT", "300"))
        self.window_title = "桌面宠物"
        
        # 动画配置
        self.animation_fps = int(os.getenv("ANIMATION_FPS", "30"))
        self.animation_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "TF", "body")
        self.frame_delay = 1000 // self.animation_fps  # 每帧延迟（毫秒）
        
        # 随机切换配置
        self.random_interval = int(os.getenv("RANDOM_INTERVAL", "5"))  # 秒
        
        # 信息框配置
        self.show_info = os.getenv("SHOW_INFO", "True").lower() == "true"
        
        # 对话窗口配置
        self.enable_chat = os.getenv("ENABLE_CHAT", "True").lower() == "true"
        self.chat_visible = os.getenv("CHAT_VISIBLE", "True").lower() == "true"
        
        # 主题配置
        self.current_theme = os.getenv("CURRENT_THEME", "粉色主题")
        
        # 托盘配置
        self.tray_icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "favicon.ico")
        
    def get_theme_colors(self):
        """获取当前主题的颜色"""
        return self.THEMES.get(self.current_theme, self.THEMES["粉色主题"])
        
    def save(self):
        """保存配置到环境变量文件"""
        try:
            with open(".env", "w", encoding='utf-8') as f:
                f.write(f"DEEPSEEK_API_KEY={self.deepseek_api_key}\n")
                f.write(f"DEEPSEEK_API_URL={self.deepseek_api_url}\n")
                f.write(f"WINDOW_WIDTH={self.window_width}\n")
                f.write(f"WINDOW_HEIGHT={self.window_height}\n")
                f.write(f"ANIMATION_FPS={self.animation_fps}\n")
                f.write(f"RANDOM_INTERVAL={self.random_interval}\n")
                f.write(f"SHOW_INFO={self.show_info}\n")
                f.write(f"ENABLE_CHAT={self.enable_chat}\n")
                f.write(f"CHAT_VISIBLE={self.chat_visible}\n")
                f.write(f"CURRENT_THEME={self.current_theme}\n")
        except Exception as e:
            print(f"保存环境变量时出错: {str(e)}") 