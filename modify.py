import os
import re
import argparse
import sys
import shutil
from manage.branch import BranchInfo
from manage.makefile import Makefile
from manage.ssh_manager import SshManager

project_name = "xv6-lab"
loc_root = "."
ssh_root = "/root/Projects"

BranchInfo = BranchInfo()
Makefile = Makefile("/".join([loc_root, project_name, "Makefile"]))
SshManager = SshManager(loc_root, ssh_root)


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


def update():
    if Makefile.update():
        change("Makefile")
    SshManager.update()


class LabManager:
    @classmethod
    def add_lab(cls, lab_name):
        def wrapper(lab_class):
            setattr(cls, lab_name, lab_class)
            setattr(lab_class, "lab_name", lab_name)
            return lab_class

        return wrapper


@LabManager.add_lab("none")
class LabNone:
    lab_name = None

    @classmethod
    def commit(cls):
        print(f"Commit files for lab {cls.lab_name}")
        if cls.lab_name is not None:
            cls.copy()

    @classmethod
    def copy(cls, file=None):
        if file is None:
            for folder in os.listdir(cls.lab_name):
                for file in os.listdir(f"{cls.lab_name}/{folder}"):
                    cls.copy(f"{folder}/{file}")
        else:
            shutil.copyfile(f"{cls.lab_name}/{file}", f"{project_name}/{file}")
            print(f"copy: {cls.lab_name}/{file} => {project_name}/{file}")
            change(f"{file}")

    @classmethod
    def add_UPROGS(cls, *files):
        for f in files:
            Makefile.add_UPROGS(f)


@LabManager.add_lab("util")
class LabUtil(LabNone):
    @classmethod
    def commit(cls, file=None):
        if file is None:
            print(f"Commit files for lab {cls.lab_name}")
            for f in os.listdir(f"{cls.lab_name}/user"):
                cls.commit(f)
        else:
            cls.copy(f"user/{file}")
            cls.add_UPROGS(file)


@LabManager.add_lab("syscall")
class LabSyscall(LabNone):
    @classmethod
    def commit(cls):
        super().commit()
        Makefile.add_UPROGS("trace", "sysinfotest")


@LabManager.add_lab("pgtbl")
class LabPgtbl(LabNone):
    pass


@LabManager.add_lab("traps")
class LabTraps(LabNone):
    @classmethod
    def commit(cls):
        super().commit()
        # Makefile.add_UPROGS("alarmtest")


@LabManager.add_lab("cow")
class LabCow(LabNone):
    pass


@LabManager.add_lab("thread")
class LabThread(LabNone):
    pass


class Operation:
    @classmethod
    def build(cls, args):
        branch = f"{loc_root}/{project_name}/.branch"
        with open(branch, 'r') as f:
            BranchInfo.set('branch', re.match(".*\\* *(.*)", f.read()).group(1))
        os.remove(branch)
        Operation.reset()
        print(f"Rebuild the project for lab {BranchInfo.get('branch')}")

    @classmethod
    def reset(cls):
        remove_project()
        create_project()

    @classmethod
    def commit(cls, args):
        getattr(LabManager, BranchInfo.get("branch"), LabNone).commit()

    @classmethod
    def download(cls, args):
        filename = getattr(args, "filename", None)
        if filename is not None:
            SshManager.download(f"{project_name}/{filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", "-o", default="commit", choices=["build", "commit", "download"])
    parser.add_argument("--filename", "-f", default=None, type=str)
    args = parser.parse_args()
    getattr(Operation, args.operation)(args)
    update()
