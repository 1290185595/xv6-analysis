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
        change(Makefile)
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
    @classmethod
    def commit(cls):
        pass

    @classmethod
    def copy(cls, file):
        shutil.copyfile(f"{cls.lab_name}/{file}", f"{project_name}/{file}")
        print(f"copy: {cls.lab_name}/{file} => {project_name}/{file}")
        change(f"{file}")


@LabManager.add_lab("util")
class LabUtil(LabNone):
    @classmethod
    def commit(cls, file=None):
        if file is None:
            for f in os.listdir(f"{cls.lab_name}/user"):
                cls.commit(f)
            print(f"Commit files for lab {cls.lab_name}")
        else:
            cls.copy(f"user/{file}")
            Makefile.add_UPROGS(file)


@LabManager.add_lab("syscall")
class LabSyscall(LabNone):
    @classmethod
    def commit(cls):
        for folder in os.listdir(cls.lab_name):
            for file in os.listdir(f"{cls.lab_name}/{folder}"):
                cls.copy(f"{folder}/{file}")
        for done_lab in ["trace"]:
            Makefile.add_UPROGS(done_lab)
        print(f"Commit files for lab {cls.lab_name}")


@LabManager.add_lab("pgtbl")
class LabPgtbl(LabNone):
    @classmethod
    def commit(cls):
        cls.copy("1")


class Operation:
    @classmethod
    def build(cls):
        branch = f"{loc_root}/{project_name}/.branch"
        with open(branch, 'r') as f:
            BranchInfo.set('branch', f.read().split(' ')[-1])
        os.remove(branch)
        Operation.reset()
        print(f"Rebuild the project for lab {BranchInfo.get('branch')}")

    @classmethod
    def reset(cls):
        remove_project()
        create_project()

    @classmethod
    def commit(cls):
        getattr(LabManager, BranchInfo.get("branch"), LabNone).commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", "-o", default="commit", choices=["commit", "build"])
    args = parser.parse_args()
    getattr(Operation, args.operation)()
    update()
