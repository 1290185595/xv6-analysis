import os
import re
import argparse
import sys
import shutil

with open("xv6-lab/Makefile") as f:
    makefile = f.read()

UPROGS = re.search("UPROGS *=(?:.*\\\\\n)*", makefile).group()
_UPROGS = UPROGS
for f in os.listdir("lab/user"):
    shutil.copyfile(f"lab/user/{f}", f"xv6-lab/user/{f}")
    print(f"xv6-lab/user/{f}")
    f = f"\t$U/_{f[:-2]}\\\n"
    if f not in UPROGS:
        _UPROGS += f

if _UPROGS != UPROGS:
    with open("xv6-lab/Makefile", 'w') as f:
        f.write(makefile.replace(UPROGS, _UPROGS))
