import yaml
from yaml import safe_load


class TimesheetManager:
    filepath: str

    def __init__(self):
        self.filepath = 'pom_tracker/config/pom_sheet_times_template.yaml'

    def get(self):
        timesheet_data = self.loader()
        return timesheet_data.get('time_blocks')

    def loader(self):
        with open(self.filepath, 'r') as f:
            data = safe_load(f)
        return data

    def dump(self, timesheet_data):
        with open(self.filepath, 'w') as f:
            yaml.dump(timesheet_data, f, default_flow_style=False)


tsm = TimesheetManager()
