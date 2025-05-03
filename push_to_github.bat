@echo off
echo Ket noi repository local voi repository remote...
set /p repo_url="Nhap URL repository GitHub cua ban (vi du: https://github.com/username/news-crawler.git): "

echo.
echo Dang ket noi voi repository remote...
git remote add origin %repo_url%

echo.
echo Dang day code len GitHub...
git push -u origin master

echo.
echo Hoan thanh! Kiem tra repository cua ban tren GitHub.
echo.
echo Nhan phim bat ky de thoat...
pause > nul
