import argparse
import json


class Config:
    def __init__(self, name):
        parser = argparse.ArgumentParser(description='Config file for the component.')
        parser.add_argument('-f', '--config-file', default='config.json', type=str, dest='config_file')
        parsed = parser.parse_args()
        with open(parsed.config_file, 'r') as f:
            json_conf = json.loads(f.read())

        self.name            = name
        self.scheduler_in    = json_conf['deploy']['monique']['scheduler-in']
        self.scheduler_out   = json_conf['deploy']['monique']['scheduler-out']
        self.controller_host = json_conf['deploy']['monique']['controller']['host']
        self.controller_port = json_conf['params'][self.name]['port'] if 'port' in json_conf['params'][self.name] else None
        self.creator         = json_conf['params'][self.name]['creator']
        self.logfile         = json_conf['params'][self.name]['logfile']
        self.mon_frequency   = json_conf['params'][self.name]['frequency']
