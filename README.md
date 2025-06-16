# Process Watcher CLI Tool

## Overview
The Process Watcher is a command-line interface (CLI) tool designed to generate detailed reports of running processes on a Windows laptop. It collects information about system processes, memory usage, and other relevant system details, providing output in both JSON and CSV formats.
Currently Supports Windows, MacOS and Linux(Tested on Ubuntu and Debian)


## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/process-watcher.git
   cd process-watcher
   ```

2. **Install Dependencies**
   Ensure you have Python 3.x installed. Then, install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Execution

To run the Process Watcher CLI tool, navigate to the project directory and double click given starter files (run.bat/sh) and let it open terminal or execute one of commands given below in desired terminal:
For Windows
```
cd Process-Watcher
./run.bat
```

For MacOS and Linux 
```
cd Process-Watcher
./run.sh
```

OS insensitive call:
```bash
python -m src.cli
```

For automation calls, pass `--automation True` in order to skip interactive command-line.

```bash
python -m src.cli --output json --limit 10 --automation True
```


### Command-Line Options
- `--output` or `-o`: Specify the output format (`json` or `csv`).
- `--file` or `-f`: Define the output file path (default is console output).
- `--limit` or `-l`: Set the maximum number of processes to return (default is 5).
- `--verbose` or `-v`: Enable verbose mode for detailed output.
- `--show_denied`: Show detailed information of denied processes.
- `--include_system_info`: Include system information in the output.
- `--advanced`: Use advanced output format.
- `--automation`: Used for Autopmation (Ansible) to skip interactive input.
- `--help-visualization`: Explanation for after CLI call, processing output data to more visual way.
- `--collect data`: Starts fetching process informations.


## Portability

You can move the project anywhere you want or create a shortcut of starter scripts (run.bat or run.sh) then you can call there any path you want.


## Testing

There is unittest covered for all classes and can be called as
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```


## CI Integration

GitAction checks functions if they return expected parameters. If everything returns success, it runs process watcher on Git runner with automation True.

## Dependencies

Project requires Python and Pip(Python lib installer/Pip installs packages) installed in host. As external dependency, we need to install psutils.
Project can be written without psutil dependency with some minor code changes but psutil is kept because
it provides simple solution
it runs inter-OS, means things which are hard to watch/fetch can be easily gathered by psutils
unified function calls means unified response type
one of the most reliable libraries of Python for OS processes
It is not deeply implemented to whole project to keep discussion open to remove it back from project with least effort.


## Example Usage

To collect and display the top 10 processes in JSON format:

```bash
python src/cli.py --output json --limit 10
```

To save the output to a CSV file:

```bash
python src/cli.py --output csv --file < path you want to create output file at > --limit 10
```
After creating CSV file, you can import it to any desired worksheet file (Excel/Google Sheets/Libra...)
For Example for Excel, Data -> From Text/CSV
![Button](/examples/virtualization%20pictures/image-1.png)
Please choose comma as delimitter and let it import.
![Comma Delimitter](/examples/virtualization%20pictures/image-2.png)
Once it is done, you will see something like:
![CSV After Export](/examples/virtualization%20pictures/image-3.png)
From here, you can see any information you desire to investigate or save as xlsx


## Automation

For Automation, Ansible is used.
Project can be kept in control node.
Once control node runs playbook on requested hosts, project will be copied to destination host's /temp folder.
Check for destinaton host's OS and runs compatible version of script.
After running the automation, script is deleted from temp folder back.
Variables can be passed as extra variables while calling Ansible Playbook.
Tested on Linux as control node (through WSL) and Windows as host to run automation.


## Accuracy

- **CPU Percentage**: Tool uses `psutil’s` `cpu_percent()` method to measure per-process CPU usage. The first call always returns 0.0 as it establishes a baseline. Then measures CPU usage over a short interval (default: 0.5 seconds). This approach provides a snapshot of CPU activity, but very short-lived processes or rapid CPU spikes may not be fully captured. To catch these spikes, interval can be increased
- **Memory usage**: It is fetched using `psutil’s` `memory_info().rss`, which reports the resident set size (actual memory used in RAM) in megabytes. This value is accurate at the moment of collection but can fluctuate rapidly as processes allocate or release memory.
- **Processes**: Some processes may terminate, hung or change state during data collection or could not fetch details of process which leads to “process not found” or “access denied” errors.
The tool marks such processes as inaccessible and includes error details in the output if requested.


## Troubleshooting Tips

- **Python Not Found**: Ensure Python is installed and added to your system's PATH.
- **Permission Denied**: Run the CLI tool with administrative privileges if you encounter permission issues when accessing process information.
- **Invalid Output Path**: Check that the specified output file path is valid and writable.
- **Dependencies Issues**: If you encounter errors related to missing packages, ensure all dependencies are installed as per the `requirements.txt`.
