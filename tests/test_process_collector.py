import unittest
from src.process_collector import ProcessCollector
import psutil
import platform

class TestProcessCollector(unittest.TestCase):

    def setUp(self):
        self.collector = ProcessCollector()

    def test_init(self):
        self.assertIsInstance(self.collector.os, str)
        self.assertIsInstance(self.collector.collection_timestamp, type(None))
        self.assertIsInstance(self.collector.total_memory, int)
        self.assertIsInstance(self.collector.cpu_count, int)

    def test_get_process_info_linux(self):
        if platform.system() == 'Linux':
            pid = psutil.Process().pid
            process_info = self.collector.get_process_info(pid)
            self.assertIsInstance(process_info, dict)
            self.assertIn('pid', process_info)
            self.assertIn('name', process_info)
            self.assertIn('user', process_info)
            self.assertIn('cpu_percent', process_info)
            self.assertIn('memory_megabyte', process_info)
            self.assertIn('status', process_info)
            self.assertIn('accessible', process_info)
            self.assertIn('error', process_info)

    def test_get_process_info_windows(self):
        if platform.system() == 'Windows':
            pid = psutil.Process().pid
            process_info = self.collector.get_process_info(pid)
            self.assertIsInstance(process_info, dict)
            self.assertIn('pid', process_info)
            self.assertIn('name', process_info)
            self.assertIn('user', process_info)
            self.assertIn('cpu_percent', process_info)
            self.assertIn('memory_megabyte', process_info)
            self.assertIn('status', process_info)
            self.assertIn('accessible', process_info)
            self.assertIn('error', process_info)

    def test_get_process_info_macos(self):
        if platform.system() == 'Darwin':
            pid = psutil.Process().pid
            process_info = self.collector.get_process_info(pid)
            self.assertIsInstance(process_info, dict)
            self.assertIn('pid', process_info)
            self.assertIn('name', process_info)
            self.assertIn('user', process_info)
            self.assertIn('cpu_percent', process_info)
            self.assertIn('memory_megabyte', process_info)
            self.assertIn('status', process_info)
            self.assertIn('accessible', process_info)
            self.assertIn('error', process_info)

    def test_get_collection_timestamp(self):
        self.assertIsInstance(self.collector.get_collection_timestamp(), type(None))

    def test_collect_processes(self):
        processes, access_info = self.collector.collect_processes()
        self.assertIsInstance(processes, list)
        self.assertIsInstance(access_info, dict)
        for process in processes:
            self.assertIsInstance(process, dict)
            self.assertIn('pid', process)
            self.assertIn('name', process)
            self.assertIn('user', process)
            self.assertIn('cpu_percent', process)
            self.assertIn('memory_megabyte', process)
            self.assertIn('status', process)
            self.assertIn('accessible', process)
            self.assertIn('error', process)

    def test_get_total_memory(self):
        self.assertIsInstance(self.collector._get_total_memory(), int)

    def test_get_cpu_usage(self):
        pid = psutil.Process().pid
        cpu_usage = self.collector._get_cpu_usage(pid)
        self.assertIsInstance(cpu_usage, float)

if __name__ == '__main__':
    unittest.main()