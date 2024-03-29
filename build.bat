@echo off

set URL=git://g.csail.mit.edu
set PROJECT=xv6-labs-2021

echo clone from %PROJECT%:
git clone %URL%/%PROJECT%

set LOCAL_PROJECT=xv6-lab
if exist %LOCAL_PROJECT% rmdir /s/q %LOCAL_PROJECT%
rename %PROJECT% %LOCAL_PROJECT%

cd %LOCAL_PROJECT%
echo %cd%
git config --global --add safe.directory %cd:\=/%
git checkout %1%
git branch -a | findstr "*" > .branch
rmdir /s/q .git
del .gitignore
cd ..


pip install -r requirements.txt
python modify.py --operation=build
