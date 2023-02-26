@echo off
if "%1"=="xv6-riscv" (
    set URL=https://github.com/mit-pdos
    set PROJECT=xv6-riscv
) else (
    set URL=https://github.com/1290185595
    set PROJECT=xv6-labs-2022
)
echo clone from %PROJECT%:
git clone %URL%/%PROJECT%

set LOCAL_PROJECT=xv6-lab
if exist %LOCAL_PROJECT% rmdir /s/q %LOCAL_PROJECT%
rename %PROJECT% %LOCAL_PROJECT%

cd %LOCAL_PROJECT%
rmdir /s/q .git
del .gitignore
cd ..

pip install -r requirements.txt
python modify.py

