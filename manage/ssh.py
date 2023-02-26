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

    def check_folder(self, dst):
        try:
            if not stat.S_ISDIR(self.sftp.stat(dst).st_mode):
                self.sftp.remove(dst)
                raise
        except Exception as e:
            self.sftp.mkdir(dst)

    def __upload(self, src, dst):
        if os.path.isfile(src):
            self.sftp.put(src, dst)
        else:
            self.check_folder(dst)
            for f in os.listdir(src):
                self.__upload(f"{src}/{f}", f"{dst}/{f}")

    def upload(self, src, dst):
        if os.path.isfile(src):
            self.check_folder(os.path.dirname(dst))
        self.__upload(src, dst)

    def __del__(self):
        self.sftp.close()


def upload(src, dst):
    Transport().upload(src, dst)
