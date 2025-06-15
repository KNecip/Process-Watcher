import json

class OutputFormatter:
    def to_json(self, data, args=None):
        return_json = {}
        return_json['processes'] = []

        if not args.advanced:
            for process in data['processes']:
                return_json['processes'].append({
                    'pid': process['pid'],
                    'name': process['name'],
                    'user': process['user'],
                    'cpu_percent': process['cpu_percent'],
                    'memory_megabyte': process['memory_megabyte']
                })
        else:
            return_json['processes'] = data['processes']
        if args.include_system_info:
            return_json['system_info'] = data['system_info'] if data.get('system_info') else {"system_info": "No system information was collected. Please reach to the developer."}
        if args.show_denied and data.get('denied_processes'):
            return_json['denied_processes'] = data['denied_processes']
        return json.dumps(return_json, indent=4)

    def to_csv(self, data, args=None):
        # instead of building/processing data twice, just let json function do the work
        data_json = json.loads(self.to_json(data, args))
        processes = data_json.get('processes', [])
        if not processes:
            raise ValueError("No process data passed.")
        headers = processes[0].keys()
        csv_lines = []
        csv_lines.append(",".join(headers))
        for process in data_json['processes']:
            csv_lines.append(",".join(str(process[key]) for key in headers))
        csv_data = "\n".join(csv_lines)
        return csv_data