import os
import re
import argparse
import sys
import shutil
from manage import ssh
from manage.branch import BranchInfo

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


class Makefile:
    path = "/".join([loc_root, project_name, "Makefile"])

    def __init__(self):
        with open(self.path) as f:
            self.makefile = f.read()
        self.UPROGS = re.search("UPROGS *=(?:.*\\\\\n)*", self.makefile).group().split("\n")
        self._UPROGS = set(self.UPROGS[1:-1])

    def add_UPROGS(self, *args):
        for f in args:
            self._UPROGS.add(f"\t$U/_{re.sub('.c$', '', f)}\\\n")

    def remove_UPROGS(self, *args):
        for f in args:
            self._UPROGS.remove(f"\t$U/_{re.sub('.c$', '', f)}\\\n")

    def update_UPROGS(self):
        if self._UPROGS != set(self.UPROGS[1:-1]):
            with open(self.path, 'w') as f:
                f.write(self.makefile.replace(
                    "\n".join(self.UPROGS),
                    "\n".join([self.UPROGS[0], *self._UPROGS, self.UPROGS[-1]])
                ))
            change("Makefile")

    def update(self):
        self.update_UPROGS()


Makefile = Makefile()


def update():
    Makefile.update()
    SshManager.update()


class LabCommit:
    @staticmethod
    def util_append(file=None):
        if file is None:
            for f in os.listdir("util/user"):
                LabCommit.util_append(f)
        else:
            shutil.copyfile(f"util/user/{file}", f"xv6-lab/user/{file}")
            print(f"copy: util/user/{file} => xv6-util/user/{file}")
            change(f"user/{file}")
            Makefile.add_UPROGS(file)


class Operation:
    @staticmethod
    def build(argv):
        branch = f"{loc_root}/{project_name}/.branch"
        with open(branch, 'r') as f:
            BranchInfo.set("branch", f.read().split('/')[-1])
        os.remove(branch)
        remove_project()
        create_project()

    @staticmethod
    def commit(argv):
        remove_project()
        create_project()
        LabCommit.util_append


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", "-o", default="commit", choices=["commit", "build"])
    args = parser.parse_args()
    getattr(Operation, args.operation)(args)
    update()
