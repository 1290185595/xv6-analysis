import os
import paramiko

from .config import Config
import stat
from .singleton import singleton


class BranchInfo:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        self.config = Config()
        self.config.read(self.config_path)

        self.section = "branch"
        if self.section not in self.config.sections():
            self.config.add_section(self.section)

    def set(self, option, value):
        self.config.set(self.section, option, value)
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def get(self, option):
        return self.config.get(self.section, option)


BranchInfo = BranchInfo()
