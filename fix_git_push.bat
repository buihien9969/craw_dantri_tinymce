@echo off
echo Kiem tra cac nhanh hien tai...
git branch

echo.
echo Kiem tra trang thai git...
git status

echo.
echo Tao nhanh main neu chua ton tai...
git checkout -b main

echo.
echo Them tat ca cac file vao staging area...
git add .

echo.
echo Commit cac thay doi...
git commit -m "Initial commit"

echo.
echo Day code len GitHub...
git push -u origin main

echo.
echo Hoan thanh! Kiem tra repository cua ban tren GitHub.
echo.
echo Nhan phim bat ky de thoat...
pause > nul
