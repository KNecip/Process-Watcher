import unittest
from src.system_info import SystemInfo
import platform

class TestSystemInfo(unittest.TestCase):

    def setUp(self):
        self.system_info = SystemInfo()

    def test_get_system_info(self):
        system_info = self.system_info.get_system_info()
        self.assertIn('os', system_info)
        self.assertIn('os_version', system_info)
        self.assertIn('hostname', system_info)
        self.assertIn('boot_time', system_info)
        self.assertIn('memory_total_gb', system_info)
        self.assertIn('memory_available_gb', system_info)
        self.assertIn('memory_used_gb', system_info)

    def test_get_disk_info(self):
        disk_info = self.system_info.get_disk_info()
        self.assertIsInstance(disk_info, list)
        for disk in disk_info:
            self.assertIn('device', disk)
            self.assertIn('mountpoint', disk)
            self.assertIn('filesystem_type', disk)
            self.assertIn('total_size', disk)
            self.assertIn('used_size', disk)
            self.assertIn('free_size', disk)
            self.assertIn('percent', disk)

    def test_get_network_info(self):
        network_info = self.system_info.get_network_info()
        self.assertIsInstance(network_info, list)
        for interface in network_info:
            self.assertIn('interface', interface)
            self.assertIn('ip_address', interface)
            self.assertIn('netmask', interface)
            self.assertIn('broadcast', interface)

    def test_get_system_summary(self):
        system_summary = self.system_info.get_system_summary()
        self.assertIn('system_info', system_summary)
        self.assertIn('disk_info', system_summary)
        self.assertIn('network_info', system_summary)

    def test_os_detection(self):
        if platform.system() == 'Darwin':
            self.assertEqual(self.system_info.get_system_info()['os'], 'MacOS')
        elif 'Linux' in platform.system():
            self.assertEqual(self.system_info.get_system_info()['os'], 'Linux')
        elif 'Windows' in platform.system():
            self.assertEqual(self.system_info.get_system_info()['os'], 'Windows')
        else:
            self.assertEqual(self.system_info.get_system_info()['os'], 'Unknown')

    def test_boot_time(self):
        boot_time = self.system_info.get_system_info()['boot_time']
        self.assertIsInstance(boot_time, str)
        self.assertEqual(len(boot_time), 19)  # YYYY-MM-DD HH:MM:SS

    def test_memory_info(self):
        memory_info = self.system_info.get_system_info()
        self.assertIsInstance(memory_info['memory_total_gb'], float)
        self.assertIsInstance(memory_info['memory_available_gb'], float)
        self.assertIsInstance(memory_info['memory_used_gb'], float)

if __name__ == '__main__':
    unittest.main()