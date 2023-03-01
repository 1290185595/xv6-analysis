import os
import paramiko

from .config import Config
import stat
from .singleton import singleton


class SshInfo:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        self.config = Config()
        self.config.read(self.config_path)

        self.section = "ssh"
        if self.section not in self.config.sections():
            self.config.add_section(self.section)

    def get(self, option, modify=True):
        if option not in self.config.options(self.section):
            self.config.set(self.section, option, input(f"Enter the {option}:"))
            if modify:
                with open(self.config_path, 'w') as f:
                    self.config.write(f)
        return self.config.get(self.section, option)

    def __getitem__(self, option):
        return self.get(option)


@singleton
class Transport:
    def __init__(self):
        ssh_info = SshInfo()
        # ssh传输
        transport = paramiko.Transport((ssh_info["hostname"], int(ssh_info["port"])))
        transport.connect(**{k: ssh_info[k] for k in ["username", "password"]})
        self.sftp = paramiko.SFTPClient.from_transport(transport)
        print('sftp传输已建立')

    def mkdir(self, dst):
        try:
            if not stat.S_ISDIR(self.sftp.stat(dst).st_mode):
                self.sftp.remove(dst)
                raise
        except:
            self.mkdir(os.path.dirname(dst))
            print(f"mkdir: {dst}")
            self.sftp.mkdir(dst)

    def __copy(self, src, dst):
        if os.path.isfile(src):
            print(f"copy: {src} => {dst}")
            self.sftp.put(src, dst)
        else:
            self.mkdir(dst)
            for f in os.listdir(src):
                self.__copy(f"{src}/{f}", f"{dst}/{f}")

    def copy(self, src, dst):
        if os.path.isfile(src):
            self.mkdir(os.path.dirname(dst))
        self.__copy(src, dst)

    def remove(self, dst):
        try:
            if stat.S_ISDIR(self.sftp.stat(dst).st_mode):
                for f in self.sftp.listdir(dst):
                    self.remove(f"{dst}/{f}")
                self.sftp.rmdir(dst)
            else:
                self.sftp.remove(dst)
            print(f"remove: {dst}")
        except:
            print(f"no such file: {dst}")

    def listdir(self, dst):
        try:
            return self.sftp.listdir(dst)
        except:
            return []

    def __del__(self):
        self.sftp.close()


def copy(src, dst):
    Transport().copy(src, dst)


def remove(dst):
    Transport().remove(dst)


def listdir(dst):
    return Transport().listdir(dst)


__all__ = ["copy", "remove", "listdir"]
