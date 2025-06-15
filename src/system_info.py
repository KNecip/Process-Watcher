import platform
import psutil
import datetime

class SystemInfo:
    def __init__(self):
        self.info = {}

    def get_system_info(self):
        """Get system information"""
        self.info['os'] = "MacOS" if platform.system() == 'Darwin' else "Linux" if 'Linux' in platform.system() else "Windows" if 'Windows' in platform.system() else "Unknown"
        self.info['os_version'] = platform.version()
        self.info['hostname'] = platform.node()
        self.info['boot_time'] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        self.info['memory_total_gb'] = psutil.virtual_memory().total / (1024.0 ** 3)
        self.info['memory_available_gb'] = psutil.virtual_memory().available / (1024.0 ** 3)
        self.info['memory_used_gb'] = psutil.virtual_memory().used / (1024.0 ** 3)
        return self.info

    def get_disk_info(self):
        """Get disk information"""
        disk_info = []
        partitions = psutil.disk_partitions()
        if not partitions:
            return disk_info
        for disk in partitions:
            usage = psutil.disk_usage(disk.mountpoint)
            disk_info.append({
                'device': disk.device,
                'mountpoint': disk.mountpoint,
                'filesystem_type': disk.fstype,
                'total_size': usage.total / (1024.0 ** 3),
                'used_size': usage.used / (1024.0 ** 3),
                'free_size': usage.free / (1024.0 ** 3),
                'percent': usage.percent
            })
        return disk_info

    def get_network_info(self):
        """Get network information"""
        network_info = []
        for interface in psutil.net_if_addrs():
            if not psutil.net_if_addrs()[interface]:
                continue
            network_info.append({
                'interface': interface,
                'ip_address': psutil.net_if_addrs()[interface][0].address,
                'netmask': psutil.net_if_addrs()[interface][0].netmask,
                'broadcast': psutil.net_if_addrs()[interface][0].broadcast
            })

        return network_info
    

    
    def get_system_summary(self):
        system_info = self.get_system_info()
        disk_info = self.get_disk_info()
        network_info = self.get_network_info()
        return {
            'system_info': system_info,
            'disk_info': disk_info,
            'network_info': network_info
        }

if __name__ == '__main__':
    system_info = SystemInfo()
    print(system_info.get_system_info())
    print(system_info.get_disk_info())
    print(system_info.get_network_info())