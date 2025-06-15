import unittest
import argparse
import sys
from src.cli import ProcessMonitorCLI
from unittest.mock import patch
from io import StringIO

class TestProcessMonitorCLI(unittest.TestCase):
    def setUp(self):
        self.cli = ProcessMonitorCLI()

    def test_create_parser(self):
        parser = self.cli.create_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_validate_arguments(self):
        args = argparse.Namespace(verbose=False, limit=5, include_system_info=False,advanced=False, show_denied=False, output='json', file=None)
        self.assertTrue(self.cli.validate_arguments(args))
        args.limit = 0
        self.assertFalse(self.cli.validate_arguments(args))
        args.limit = 5
        self.assertTrue(self.cli.validate_arguments(args))

    @patch('sys.stdout', new=StringIO())
    def test_show_visualization_help(self):
        self.cli.show_visualization_help()
        self.assertIn('VISUALIZATION GUIDE', sys.stdout.getvalue())

    def test_collect_and_format_data(self):
        args = argparse.Namespace(verbose=False, limit=5, include_system_info=False,advanced=False, show_denied=False, output='json', file=None)
        data = self.cli.collect_and_format_data(args)
        self.assertIsInstance(data, dict)
        self.assertIn('processes', data)
        self.assertIn('metadata', data)

    @patch('sys.stdout', new=StringIO())
    def test_output_data(self):
        data = {'processes': [], 'metadata': {}}
        args = argparse.Namespace(verbose=False, limit=5, include_system_info=False,advanced=False, show_denied=False, output='json', file=None)
        self.cli.output_data(data, args)
        self.assertIn('processes', sys.stdout.getvalue())

if __name__ == '__main__':
    unittest.main()