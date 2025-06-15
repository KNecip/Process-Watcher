#!/usr/bin/env python3
"""
Process Collector Module
Handles cross-platform process information collection with minimal external dependencies.
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import psutil

class ProcessInfo:
    
    def __init__(self, pid: int):
        self.pid = pid
        self.name: Optional[str] = None
        self.user: Optional[str] = None
        self.cpu_percent: float = 0.000
        self.memory_megabyte: float = 0.0
        self.status: Optional[str] = None
        self.accessible: bool = True
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pid': self.pid,
            'name': self.name,
            'user': self.user,
            'cpu_percent': round(self.cpu_percent, 2) if self.cpu_percent is not None else 0.0 ,
            'memory_megabyte': round(self.memory_megabyte, 2) if self.memory_megabyte is not None else 0.0,
            'status': self.status,
            'accessible': self.accessible,
            'error': self.error
        }

class ProcessCollector:
    
    def __init__(self):
        self.os = sys.platform
        self.collection_timestamp = None
        self.total_memory = self._get_total_memory()
        self.cpu_count = psutil.cpu_count() or 1

    def _get_total_memory(self) -> int:
        """Get total system memory"""
        try:
            if 'darwin' in self.os.lower():
                result = subprocess.run(['sysctl', 'hw.memsize'], capture_output=True, text=True)
                if result.returncode == 0:
                    return int(result.stdout.split(':')[1].strip())
            
            elif 'linux' in self.os.lower():
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            # Convert from KB to bytes
                            return int(line.split()[1]) * 1024
            
            elif 'win' in self.os.lower():
                try:
                    ps_cmd = ['powershell', '-Command','Get-WMIObject win32_ComputerSystem | foreach {$_.TotalPhysicalMemory /1GB}']
                    total_memory = subprocess.run(ps_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    return int(float(total_memory.stdout.strip()))
                except Exception as e:
                    print('Could not fetch Physical memory amount of host.')
                    print(e)
            else:
                print("Current OS is not supported. Please reach out to the developer.")
                return 0
            
        except Exception:
            return 8 * 1024 * 1024 * 1024
    
    def _get_pid_list(self) -> List[int]:
        """Get list of all process PIDs"""
        pids = []
        try:
            if self.os == 'darwin':
                pid_list = subprocess.run(['ps', '-axo', 'pid'], capture_output=True, text=True)
                if pid_list.returncode == 0:
                    for pid in pid_list.stdout.strip().split('\n')[1:]:
                        try:
                            pids.append(int(pid.strip()))
                        except ValueError:
                            continue
            
            elif self.os.startswith('linux'):
                proc_dir = Path('/proc')
                for process in proc_dir.iterdir():
                    if process.is_dir() and process.name.isdigit():
                        pids.append(int(process.name))
            
            elif 'win' in self.os:
                pid_list = subprocess.run(['powershell', '-Command', 'Get-Process | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
                if pid_list.returncode == 0:
                    for pid in pid_list.stdout.strip().split('\n')[3:]:
                        try:
                            pids.append(int(pid.split()[0]))
                        except (ValueError, IndexError):
                            continue
            else:
                print("Cannot get PID list for current operating system. Please reach out to the developer.")
        except Exception as e:
            print(f"Failed to get PID list: {e}")
        
        # Sort PIDs in descending order to not get system processes at the top
        return sorted(pids, reverse=True)
    
    def _read_proc_stat(self, pid: int) -> Optional[Dict[str, Any]]:
        """Read process statistics from /proc/pid/stat (ALL SYSTEMS)
            Note: This method is not in use but if we want to keep psutil as a dependency, we can use it since it works on all operating systems.
        """
        try:
            proc = psutil.Process(pid)
            if not proc.is_running():
                return None
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'state': proc.status(),
                'ppid': proc.ppid(),
                'utime': proc.cpu_times().user,
                'stime': proc.cpu_times().system,
                'starttime': int(proc.create_time()),
                'vsize': proc.memory_info().vms,
                'rss': proc.memory_info().rss,
                'user': proc.username()
            }

        
        except (IOError, OSError, ValueError, IndexError):
            return None
    
    def _read_proc_status(self,  pid: int, verbose=False) -> Optional[Dict[str, Any]]:
        """Read process status from /proc/pid/status (Linux)"""
        try:
            status_file = Path(f'/proc/{pid}/status')
            if not status_file.exists():
                return None
            
            status_info = {}
            with open(status_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        status_info[key.strip()] = value.strip()
            
            return status_info
        except Exception as e:
            print("Cannot read proc. Please be sure you are running this script with sufficient permissions.")
            if verbose:
                print(f"Verbose error: {e}")
            return None
    
    def _get_process_info_linux(self, pid: int) -> ProcessInfo:
        """Get process information on Linux"""
        process = ProcessInfo(pid)
        try:
            stat_data = self._read_proc_status(pid)
            if not stat_data:
                process.accessible = False
                process.error = "Cannot read /proc/pid/stat"
                return process
            
            process.name = stat_data['Name']
            process.status = stat_data['State']
            process.user = psutil.Process(pid).username()
            process.cpu_percent = self._get_cpu_usage(pid, interval=1.0)
            process.memory_megabyte = psutil.Process(pid).memory_info().rss / (1024 * 1024)
            
        except (PermissionError):
            process.accessible = False
            process.error = "Permission denied"
        except Exception as e:
            process.accessible = False
            process.error = str(e)
        
        return process.to_dict()
    
    def _get_process_info_macos(self, pid: int) -> ProcessInfo:
        """Get process information on macOS"""
        proc_info = ProcessInfo(pid)
        try:
            result = subprocess.run(['ps', '-p', str(pid), '-o', 'pid,user,%cpu,%mem,stat'],capture_output=True, text=True, timeout=5)
            if result.returncode != 0 or not result.stdout.strip():
                proc_info.accessible = False
                proc_info.error = "Process not found or permission denied"
                return proc_info
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                proc_info.accessible = False
                proc_info.error = "Invalid ps output"
                return proc_info
            data_line = lines[1].strip()
            fields = data_line.split(maxsplit=6)
            
            if len(fields) < 5:
                proc_info.accessible = False
                proc_info.error = "Invalid ps output format"
                return proc_info
            proc_info.pid = int(fields[0])
            proc_info.user = fields[1]
            proc_info.cpu_percent = float(fields[2])
            proc_info.memory_megabyte = float(fields[3])
            proc_info.status = fields[4]
            proc_info.name = os.path.basename(proc_info.command.split()[0]) if proc_info.command else f"pid_{pid}"
        except Exception as e:
            proc_info.accessible = False
            proc_info.error = f"Unexpected error: {e}"

        return proc_info
    
    def _get_process_info_windows(self, pid: int) -> ProcessInfo:
        """Get process information on Windows using PowerShell"""
        process = ProcessInfo(pid)
        try:
            ps_cmd = 'powershell -Command "Get-Process -Id %d | ForEach-Object { $_ | Select-Object Id, Name, @{Name=\'User\'; Expression={ (Get-WmiObject Win32_Process -Filter \'ProcessId=%d\').GetOwner().User }}, CPU, @{Name=\'Memory (MB)\'; Expression={ [math]::round($_.WorkingSet / 1MB, 2) }} } | ConvertTo-Json"' % (pid, pid)
            proc_data = subprocess.run(ps_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if proc_data.returncode == 0 and proc_data.stdout.strip():
                proc_json = json.loads(proc_data.stdout.strip())
                process.accessible = True
                process.name = proc_json.get('Name')
                process.user = proc_json.get('User')
                process.status = 'Running'  # I am fetching only running processes
                process.cpu_percent = self._get_cpu_usage(pid, interval=1.0) 
                process.memory_megabyte = proc_json.get('Memory (MB)')
            if not process.name:
                process.accessible = False
                process.error = "Unable to retrieve process information"
        
        except Exception as e:
            process.accessible = False
            process.error = str(e)
            print(e)
        return process.to_dict()
    
    def get_process_info(self, pid: int) -> ProcessInfo:
        """Get information for a process"""
        if self.os.startswith('linux'):
            return self._get_process_info_linux(pid)
        elif self.os == 'darwin':
            return self._get_process_info_macos(pid)
        elif 'win' in self.os:
            return self._get_process_info_windows(pid)
    
    def _get_cpu_usage(self, pid: int, interval: float = 1.0) -> float:
        """Get CPU usage for a specific process
        - Note: It does not work on macOS due to psutil limitations, whole CPU core count is returned instead."""
        try:
            proc = psutil.Process(pid)
            if proc.is_running():
                cpu_usage = (proc.cpu_percent(interval=interval)/len(psutil.Process(pid).cpu_affinity()))
                return cpu_usage
            return 0.0
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"Could not get CPU usage for PID {pid}: process not found or access denied")
            return 0.0

    def collect_processes(self, verbose: bool = False, include_denied_details: bool = False, max_processes: int = 100) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Collect information for all processes
        Returns:
            - process_list  -> List of processes.
            - access_info   -> More information about denied processes
        """
        
        if verbose:
            print("Getting process list...")
        
        pids = self._get_pid_list()
        if max_processes > 0:
            pids = pids[:max_processes]
        
        if verbose:
            print(f"Total pids: {len(pids)}")
        
        processes = []
        denied_processes = []
        accessible_count = 0
        denied_count = 0
        
        for i, pid in enumerate(pids):
            if verbose and i % 50 == 0:
                print(f"Processing: {i}/{len(pids)} ({(i/len(pids)*100):.1f}%)")

            try:
                proc_info = self.get_process_info(pid)
                if proc_info.get('accessible'):
                    processes.append(proc_info)
                    accessible_count += 1
                else:
                    denied_count += 1
                    if include_denied_details:
                        denied_processes.append({
                            'pid': pid,
                            'error': proc_info.get('error'),
                            'name': proc_info.get('name') if proc_info.get('name') else f"pid_{pid}"
                        })
            
            except Exception as e:
                print(e)
                denied_count += 1
                if include_denied_details:
                    denied_processes.append({
                        'pid': pid,
                        'error': str(e),
                        'name': f"pid_{pid}"
                    })
        
        if verbose:
            print(f"Collection complete: {accessible_count} accessible, {denied_count} denied")
        
        access_info = {
            'total_found_process': len(pids),
            'accessible_processes': accessible_count,
            'permission_denied': denied_count
        }
        
        if include_denied_details and denied_processes:
            access_info['denied_details'] = denied_processes
        
        return processes, access_info
    
    def get_collection_timestamp(self) -> Optional[str]:
        """Get the timestamp of the last collection"""
        return self.collection_timestamp

if __name__ == '__main__':
    collector = ProcessCollector()
    
    print(f"OS: {collector.os}")
    print(f"Total Memory: {collector.total_memory / (1024**3):.2f} GB")
    print(f"CPU Count: {collector.cpu_count}")
    
    # Test single process (current process)
    current_pid = os.getpid()
    print(f"Testing with current process (PID: {current_pid}):")
    proc_info = collector.get_process_info(current_pid)
    print(json.dumps(proc_info, indent=2))

    
    # Test collection of first 10 processes
    print("Testing process collection (first 10 processes):")
    processes, access_info = collector.collect_processes(verbose=True)
    print(f"Collected {len(processes)} processes.")
    print(json.dumps(processes[:10], indent=2))
    print("Access Info:")
    print(json.dumps(access_info, indent=2))
