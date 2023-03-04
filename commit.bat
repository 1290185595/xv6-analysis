@echo off

@REM python modify.py --operation=commit

if "%1" == "" (
    set MASSAGE="."
) else (
    set MASSAGE=%1
)
@echo on

git add .
git commit -m %MASSAGE%
git push