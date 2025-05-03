@echo off
echo Khoi tao Git repository...
git init -b main

echo.
echo Them tat ca cac file vao staging area...
git add .

echo.
echo Commit cac thay doi...
git commit -m "Initial commit"

echo.
echo Ket noi voi remote repository...
git remote add origin https://github.com/buihien9969/craw_dantri_tinymce.git

echo.
echo Day code len GitHub...
git push -u origin main

echo.
echo Hoan thanh! Kiem tra repository cua ban tren GitHub.
echo.
echo Nhan phim bat ky de thoat...
pause > nul
