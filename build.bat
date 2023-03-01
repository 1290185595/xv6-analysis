@echo off

set URL=git://g.csail.mit.edu
set PROJECT=xv6-labs-2022

echo clone from %PROJECT%:
git clone %URL%/%PROJECT%

set LOCAL_PROJECT=xv6-lab
if exist %LOCAL_PROJECT% rmdir /s/q %LOCAL_PROJECT%
rename %PROJECT% %LOCAL_PROJECT%

cd %LOCAL_PROJECT%
git checkout %1%
git branch -a | findstr "remotes/origin/HEAD" > .branch
rmdir /s/q .git
del .gitignore
cd ..

pip install -r requirements.txt
python modify.py --operation=build
