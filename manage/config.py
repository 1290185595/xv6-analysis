from .singleton import singleton

from configparser import ConfigParser


@singleton
class Config(ConfigParser):
    pass
