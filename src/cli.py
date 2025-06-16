#!/usr/bin/env python3
"""
Process Watcher CLI Tool
Cross-platform process monitoring tool that collects system process information
and outputs in CSV or JSON format for visualization.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from .process_collector import ProcessCollector
from .output_formatter import OutputFormatter
from .system_info import SystemInfo

class ProcessMonitorCLI:

    def __init__(self):
        self.collector = ProcessCollector()
        self.system_info = SystemInfo()

    def create_parser(self) -> argparse.ArgumentParser:
        """Parser configuration"""
        parser = argparse.ArgumentParser(
            description="Monitor system processes and export data",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # OUTPUT OPTIONS
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "--output",
            "-o",
            choices=["json", "csv"],
            default="json",
            help="Output format (default: json)",
        )
        output_group.add_argument(
            "--file", "-f", type=str, help="Output file path (default: console)"
        )
        output_group.add_argument(
            "--advanced", "-a", type=bool, help="If true, use advanced output format (default: false)" , default=False
        )
        # OUTPUT OPTIONS END

        # PERMISSIONS
        reporting_group = parser.add_argument_group("Reporting Options")
        reporting_group.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Verbose mode for more detailed output",
        )
        reporting_group.add_argument(
            "--show_denied",
            action="store_true",
            default=False,
            help="Show detailed information of denied processes",
        )
        reporting_group.add_argument(
            "--include_system_info",
            action="store_true",
            default=False,
            help="Include system information",
        )
        # PERMISSIONS END

        # UTILITIES
        utility_group = parser.add_argument_group("Utility Options")
        utility_group.add_argument(
            "--help-visualization",
            action="store_true",
            help="Show help for visualizing the output data",
        )
        utility_group.add_argument(
            "--limit",
            "-l",
            type=int,
            default=5,
            help="Maximum number of processes to return (default: 100)",
        )
        utility_group.add_argument(
            "--automation",
            "-au",
            type=bool,
            default=False,
            help="If application is called from Ansible or other automation tool, set to true (default: false)",
        )
        # UTILITIES END
        
        return parser

    def validate_arguments(self, args: argparse.Namespace) -> bool:
        """Validate arguments"""
        errors = []
        if args.limit <= 0:
            errors.append("Process limit must be greater than 0")
            return False

        if args.file:
            output_path = Path(args.file)
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if output_path.exists() and not output_path.is_file():
                    errors.append(f"Output path exists but is not a file: {args.file}")
            except PermissionError:
                errors.append(f"Permission denied: cannot write to {args.file}")
            except Exception as e:
                errors.append(f"Invalid output path {args.file}: {e}")

        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    def show_visualization_help(self):
        """Display help for data visualization"""
        help_text = """
          VISUALIZATION GUIDE
          ==================

          The process monitor outputs data in CSV or JSON format that can be easily 
          visualized using various tools:
          
          ## Excel / Google Sheets:
          1. In Excel -> Data -> Get Data -> From Text/CSV
          2. In Google Sheets -> File -> Import -> Upload CSV
          Choose CSV as comma (,) as delimiter.
        """
        print(help_text)

    def collect_and_format_data(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Collect process data"""
        if args.verbose:
            print("Collecting process information...")

        processes, access_info = self.collector.collect_processes(verbose=args.verbose, include_denied_details=args.show_denied, max_processes=args.limit)

        if args.verbose:
            print(f"Found {len(processes)} processes")
            if access_info.get("permission_denied", 0) > 0:
                print(f"Permission denied for {access_info['permission_denied']} processes")
        top_processes = sorted(processes, key=lambda p: p.get('memory_megabyte', 0), reverse=True)

        output_data = {
            "processes": top_processes,
            "metadata": {
                "collection_timestamp": self.collector.get_collection_timestamp(),
                "total_processes_found": access_info.get("total_found", len(processes)),
                "accessible_processes": len(processes),
                "permission_denied": access_info.get("permission_denied", 0)
            },
        }
        if args.include_system_info:
            output_data["system_info"] = self.system_info.get_system_summary()

        if args.show_denied and access_info.get("denied_details"):
            output_data["denied_processes"] = access_info["denied_details"]

        return output_data

    def output_data(self, data: Dict[str, Any], args: argparse.Namespace):
        """Output data in requested format"""
        formatter = OutputFormatter()

        if args.output == "json":
            output_content = formatter.to_json(data, args)
        elif args.output == "csv":
            output_content = formatter.to_csv(data, args)

        if args.file:
            if not args.file.endswith('.txt'):
                os.makedirs(args.file, exist_ok=True)
                args.file = os.path.join(args.file, 'processes.txt')
            with open(args.file, 'w', newline='') as f:
                f.write(output_content)
            if args.verbose:
                print(f"Output written to: {args.file}")
        else:
            print(output_content)

    def help(self):
        print("Usage: process_collector [options]")
        print("  cpu weight <value>      Set the weight for CPU usage")
        print("  memory weight <value>   Set the weight for memory usage")
        print("  limit <value>           Set the maximum number of processes to collect")
        print("  output <format>         Set the output format (json, csv)")
        print("  file <path>             Set the output file path")
        print("  verbose                 Enable verbose output")
        print("  show denied             Show denied processes")
        print("  include system info     Include system information in output")
        print("  help visualization      Show help for visualization options")
        print("  test permissions        Test permissions and exit")
        print("  help                    Show this help message")
        print("  clear                   Clean up console")
        print("  show parameters         Show all parameters")
        print("  collect data            Collect data and exit")
        print("  help                    Show this help message")
        print("  exit                    Exit the application")

    def show_parameters(self, args: argparse.Namespace):
        print(f"Limit: {args.limit}")
        print(f"Output format: {args.output}")
        print(f"Output file: {args.file}")
        print(f"Verbose: {args.verbose}")
        print(f"Show denied: {args.show_denied}")
        print(f"Include system info: {args.include_system_info}")
        print(f"Advanced: {args.advanced}")

    def run(self, args: Optional[list] = None) -> int:
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.automation:
            self.show_parameters(parsed_args)
            print("=" * 50)
            print("Process Watcher CLI started. Type 'exit' to quit. Type 'help' for help.")
            print("Type show parameters to see all parameters.")
            print("=" * 50)
            print("Default Values:")
            while True:
                user_input = input("Process Watcher CLI > ")
                if      "exit"                  in user_input.lower():
                    print("Exiting Process Watcher CLI...")
                    break
                elif    "help"                  in user_input.lower():
                    # Change to main help
                    self.help()
                elif    "limit"                 in user_input.lower():
                    if len(user_input.split()) < 2:
                        print("Error: Missing limit value.")
                        print("Usage: limit <value>")
                    else:
                        parsed_args.limit = int(user_input.split(" ")[-1])
                        print(f"Limit set to: {parsed_args.limit}")
                elif    "output"                in user_input.lower():
                    if parsed_args.output != "csv" and parsed_args.output != "json":
                        print("Error: Invalid output format. Use 'json' or 'csv'.")
                    parsed_args.output = user_input.split(" ")[-1]
                    print(f"Output format set to: {parsed_args.output}")
                elif    "file"                  in user_input.lower():
                    parsed_args.file = user_input.split(" ")[-1]
                    print(f"Output file set to: {parsed_args.file}")
                elif    "verbose"               in user_input.lower():
                    if parsed_args.verbose:
                        parsed_args.verbose = False
                        print("Verbose mode disabled.")
                    else:
                        parsed_args.verbose = True
                        print("Verbose mode enabled.")
                elif    "advanced"               in user_input.lower():
                    if parsed_args.advanced:
                        parsed_args.advanced = False
                        print("Advanced output disabled.")
                    else:
                        parsed_args.advanced = True
                        print("Advanced output enabled.")
                elif    "show denied"           in user_input.lower():
                    if parsed_args.show_denied:
                        parsed_args.show_denied = False
                        print("Showing denied processes disabled.")
                    else:
                        parsed_args.show_denied = True
                        print("Showing denied processes enabled.")
                elif    "include system info"   in user_input.lower():
                    if parsed_args.include_system_info:
                        parsed_args.include_system_info = False
                        print("Including system info disabled.")
                    else:
                        parsed_args.include_system_info = True
                        print("Including system info enabled.")
                elif    "collect data"          in user_input.lower():
                    data = self.collect_and_format_data(parsed_args)
                    self.output_data(data, parsed_args)
                elif    "visualization help"   in user_input.lower():
                    self.show_visualization_help()
                elif    "clear"                 in user_input.lower():
                    os.system('cls') if 'win' in sys.platform else os.system('clear')
                elif    "show parameters"       in user_input.lower():
                    self.show_parameters(parsed_args)
                else:
                    print("Unknown command. Type 'help' for available commands.")
            return 0
        else:
            if not self.validate_arguments(parsed_args):
                return 1

            data = self.collect_and_format_data(parsed_args)
            self.output_data(data, parsed_args)
            return 0

def main():
    """Entry point for the CLI application"""
    cli = ProcessMonitorCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()