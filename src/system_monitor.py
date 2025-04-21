import psutil

class SystemMonitor:
    def __init__(self, config):
        self.config = config
        
    def get_cpu_usage(self):
        """获取CPU使用率"""
        return psutil.cpu_percent(interval=1)
        
    def get_memory_usage(self):
        """获取内存使用率"""
        return psutil.virtual_memory().percent
        
    def get_disk_usage(self):
        """获取磁盘使用率"""
        return psutil.disk_usage('/').percent
        
    def get_network_usage(self):
        """获取网络使用情况"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        } 