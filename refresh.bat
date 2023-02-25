if "%1"=="xv6-riscv" (
    set URL=https://github.com/mit-pdos
    set PROJECT=xv6-riscv
) else (
    set URL=git://g.csail.mit.edu
    set PROJECT=xv6-labs-2022
)
set LOCAL_PROJECT=xv6-lab

git clone %URL%/%PROJECT%

if exist %LOCAL_PROJECT% rmdir /s/q %LOCAL_PROJECT%
rename %PROJECT% "xv6-lab"
python modify.py %LOCAL_PROJECT%

cd %LOCAL_PROJECT%
rmdir /s/q .git
del .gitignore

