@echo off
echo Khoi tao Git repository...
git init

echo Them tat ca cac file vao staging area...
git add .

echo Commit cac thay doi...
git commit -m "Initial commit"

echo.
echo Da hoan thanh cac buoc co ban. Bay gio ban can:
echo 1. Tao repository tren GitHub (hoac dich vu Git khac)
echo 2. Chay cac lenh sau de ket noi va day code len:
echo    git remote add origin URL_REPOSITORY_CUA_BAN
echo    git push -u origin master
echo.
echo Nhan phim bat ky de thoat...
pause > nul
