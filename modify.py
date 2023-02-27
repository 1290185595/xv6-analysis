import os
import re
import argparse
import sys
import shutil
from manage import ssh

project_name = "xv6-lab"
loc_root = "."
ssh_root = "/root/Projects"


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
    def __init__(self):
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
            ssh.copy(f, re.sub(loc_root, ssh_root, f, 1))


SshManager = SshManager()


@SshManager.change
def change(*filename):
    return [f"{project_name}/{f}" for f in filename]


@SshManager.remove
def remove(*filename):
    return [f"{project_name}/{f}" for f in filename]


@SshManager.change
def create_project():
    return [project_name]


@SshManager.remove
def remove_project():
    return [project_name]


update = SshManager.update

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", help="remove all files on sever and push all files from local", action="store_true")
    args = parser.parse_args()
    print(args)

    if args.all:
        print(args.all)

    # remove_project()
    # create_project()

    with open("xv6-lab/Makefile") as f:
        makefile = f.read()

    UPROGS = re.search("UPROGS *=(?:.*\\\\\n)*", makefile).group()
    _UPROGS = UPROGS
    for f in os.listdir("lab/user"):
        shutil.copyfile(f"lab/user/{f}", f"xv6-lab/user/{f}")
        print(f"copy: lab/user/{f} => xv6-lab/user/{f}")
        change(f"user/{f}")
        f = f"\t$U/_{f[:-2]}\\\n"
        if f not in UPROGS:
            _UPROGS += f

    if _UPROGS != UPROGS:
        with open("xv6-lab/Makefile", 'w') as f:
            f.write(makefile.replace(UPROGS, _UPROGS))
        change("Makefile")
    create_project()
    update()
