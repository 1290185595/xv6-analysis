import os

from . import ssh
import re


class PathDict:
    def __init__(self, root, listdir):
        self.root = root
        self.listdir = listdir
        self.dict = {}

    def push(self, v: str, d=None):
        if d is None:
            d = self.dict
        v = v.split('/', 1)
        if len(v) == 1:
            d[v[0]] = None
        else:
            d = d.setdefault(v[0], {})
            if d is not None:
                self.push(v[1], d)

    def pop(self, v: str, d=None, r=None):

        if d is None:
            d = self.dict
        if r is None:
            r = self.root
        v = v.split('/', 1)
        if v[0] not in d.keys():
            d[v[0]] = {k: None for k in self.listdir(r)}
        if len(v) == 1:
            d.pop(v[0])
        elif self.pop(v[1], d[v[0]], f"{r}/{v[0]}") == 0:
            d.pop(v[0])
        return len(d)

    def reset(self):
        self.dict = {}

    def view(self, check=True, d=None, r=None):
        if d is None:
            d = self.dict
        if r is None:
            r = self.root
        filelist = self.listdir(r) if check else []
        for k, v in list(d.items()):
            if check and k not in filelist:
                d.pop(k)
            elif v is None:
                yield f"{r}/{k}"
            else:
                for f in self.view(check, v, f"{r}/{k}"):
                    yield f

    def __contains__(self, v: str):
        d = self.dict
        v = v.split('/')
        while len(v) > 0 and v[0] in d.keys():
            d = d[v.pop(0)]
        return len(v) == 0


class SshManager:
    def __init__(self, loc_root, ssh_root):
        self.loc_root = loc_root
        self.ssh_root = ssh_root
        self.__change = PathDict(loc_root, os.listdir)
        self.__remove = PathDict(ssh_root, ssh.listdir)

    def change(self, func):
        def _func(*args, **kwargs):
            files = func(*args, **kwargs)
            for f in files:
                self.__change.push(f)
            return files

        return _func

    def remove(self, func):
        def _func(*args, **kwargs):
            files = func(*args, **kwargs)
            for f in files:
                self.__remove.push(f)
                self.__change.pop(f)
            return files

        return _func

    def update(self):
        for f in self.__remove.view():
            ssh.remove(f)

        for f in self.__change.view():
            ssh.copy(f, re.sub(self.loc_root, self.ssh_root, f, 1))

    def download(self, filename):
        src = f"{self.ssh_root}/{filename}"
        dst = f"{self.loc_root}/{filename}"
        print(f"copy: {src} => {dst}")
        ssh.Transport().sftp.get(src, dst)
