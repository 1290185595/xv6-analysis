import os
import paramiko

import configparser
import stat


def get_ssh_info():
    class SshInfo:
        def __init__(self):
            self.config_path = os.path.join(os.path.dirname(__file__), "ssh.ini")
            self.config = configparser.ConfigParser()
            self.config.read(self.config_path)

            self.section = "ssh"
            if self.section not in self.config.sections():
                self.config.add_section(self.section)

        def get(self, option):
            if option not in self.config.options(self.section):
                self.config.set(self.section, option, input(f"Enter the {option}:"))
            return self.config.get(self.section, option)

        def __del__(self):
            with open(self.config_path, 'w') as f:
                self.config.write(f)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            del self

    with SshInfo() as f:
        return {k: f.get(k) for k in ["hostname", "port", "username", "password"]}


class Transport:
    def __init__(self):
        ssh_info = get_ssh_info()
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
            print(f"mkdir {dst}")
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

    def __del__(self):
        self.sftp.close()


def copy(src, dst):
    Transport().copy(src, dst)


def remove(dst):
    pass


__all__ = ["copy"]
