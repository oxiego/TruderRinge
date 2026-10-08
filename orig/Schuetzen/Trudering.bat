@echo off
E:
cd E:\Schuetzen\
set datum=%date:~6,4%%date:~3,2%%date:~,2%
D:\Programme\7-Zip\7z a %datum%-Schuetzen.zip @backup.lst
copy "E:\Schuetzen\*.zip" "C:\Users\SG_User\Backup\"
move "E:\Schuetzen\*.zip" "E:\Schuetzen\Backup\"
REM E:\Schuetzen\Schuetzen.odt
