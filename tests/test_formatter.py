import unittest
import json
from src.output_formatter import OutputFormatter
import argparse

class TestOutputFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = OutputFormatter()

    def test_to_json_basic(self):
        args = argparse.Namespace(verbose=False, limit=5, include_system_info=False, advanced=False, show_denied=False, output='json', file=None)
        data = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ]
        }
        expected_output = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ]
        }
        self.assertEqual(json.loads(self.formatter.to_json(data, args)), expected_output)

    def test_to_json_advanced(self):
        args = argparse.Namespace(verbose=False, limit=5, include_system_info=False, advanced=True, show_denied=False, output='json', file=None)
        data = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ]
        }
        expected_output = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ]
        }
        self.assertEqual(json.loads(self.formatter.to_json(data, args)), expected_output)

    def test_to_json_include_system_info(self):
        args = argparse.Namespace(verbose=False, limit=5, include_system_info=True, advanced=False, show_denied=True, output='json', file=None)
        data = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ],
            'system_info': 'System info'
        }
        expected_output = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ],
            'system_info': 'System info'
        }
        self.assertEqual(json.loads(self.formatter.to_json(data, args)), expected_output)

    def test_to_json_show_denied(self):
        args = argparse.Namespace(verbose=False, limit=5, include_system_info=False, advanced=False, show_denied=True, output='json', file=None)
        data = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ],
            'denied_processes': 'Denied processes'
        }
        expected_output = {
            'processes': [
                {'pid': 1, 'name': 'process1', 'user': 'user1', 'cpu_percent': 10.0, 'memory_megabyte': 100.0},
                {'pid': 2, 'name': 'process2', 'user': 'user2', 'cpu_percent': 20.0, 'memory_megabyte': 200.0}
            ],
            'denied_processes': 'Denied processes'
        }
        self.assertEqual(json.loads(self.formatter.to_json(data, args)), expected_output)