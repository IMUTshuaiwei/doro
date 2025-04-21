import requests
import json
from PySide6.QtCore import QObject, Signal
from threading import Thread

class DeepSeekClient(QObject):
    # 定义信号
    response_received = Signal(str)  # 用于发送API响应
    error_occurred = Signal(str)     # 用于发送错误信息
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.api_key = config.deepseek_api_key
        self.api_url = config.deepseek_api_url
        
    def send_message(self, message):
        """发送消息到DeepSeek API"""
        # 创建并启动新线程
        thread = Thread(target=self._send_message_thread, args=(message,))
        thread.daemon = True
        thread.start()
        
    def _send_message_thread(self, message):
        """在新线程中发送消息"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            print(f"Sending request to {self.api_url}/chat/completions")
            print(f"Headers: {headers}")
            print(f"Data: {data}")
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                self.response_received.emit(response.json()["choices"][0]["message"]["content"])
            elif response.status_code == 402:
                self.error_occurred.emit("抱歉，当前API Key余额不足。请通过设置菜单更新API Key。")
            else:
                error_message = "未知错误"
                try:
                    error_data = response.json()
                    if "error" in error_data and "message" in error_data["error"]:
                        error_message = error_data["error"]["message"]
                except:
                    pass
                self.error_occurred.emit(f"错误: {response.status_code} - {error_message}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
            self.error_occurred.emit(f"错误: {str(e)}")
            
    def get_emotion_response(self, system_status):
        """根据系统状态获取情感响应"""
        message = f"当前系统状态：CPU使用率 {system_status['cpu']}%，内存使用率 {system_status['memory']}%。请给出一个简短的情感回应。"
        self.send_message(message) 