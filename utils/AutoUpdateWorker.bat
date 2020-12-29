@ECHO off
REM Batch file to check Kodi setup and run Kodi when installation is finished

ECHO ####################################
ECHO ### KodiAutoUpdate script v1.0.0 ###
ECHO ####################################
ECHO=
SET useTask=%1
SET "kodiexepath="
SET setupfound=false
SET /A timeout=60
SET /A currenttime=1

REM Get Kodi executable path
for /f "tokens=2 delims=," %%I in (
    'wmic process where "name='kodi.exe'" get ExecutablePath^,Handle /format:csv ^| find /i "kodi.exe"'
) do set "kodiexepath=%%~I"
IF "%kodiexepath%"=="" GOTO BADEND


ECHO ^> Waiting for the closing of Kodi...

:LOOPKODI
   tasklist /FI "IMAGENAME eq Kodi.exe" 2>NUL | find /I /N "Kodi.exe">NUL
   IF "%ERRORLEVEL%" NEQ "0" (
      REM Kodi process not found, means that Kodi is full closed
      GOTO STARTOPS
   )
   REM Wait 1 second
   SET /A currenttime=%currenttime%+1
   timeout 1 >NUL
   IF "%currenttime%"=="%timeout%" GOTO BADEND
GOTO LOOPKODI


:STARTOPS
ECHO ^> Start installation of Kodi update...
IF "%useTask%"=="useTask" (
  schtasks /RUN /TN "Kodi_Install_NoUAC"
) ELSE (
  Start "" "%useTask%"
)

ECHO ^> Waiting for the installation completed...
SET /A currenttime = 1
:LOOPINSTALLER
   REM Check setup installer on processes list
   tasklist /FI "IMAGENAME eq KodiInstaller.exe" 2>NUL | find /I /N "KodiInstaller.exe">NUL
   IF "%setupfound%"=="false" (
      IF "%ERRORLEVEL%" EQU "0" (
         ECHO ^> Installer found, Please wait...
         SET setupfound=true
      )
   ) ELSE (
      IF "%ERRORLEVEL%" NEQ "0" (
         REM Setup process not found, means the installation is finished
         GOTO :RUNKODI
      )
   )
   REM Wait 1 second
   SET currenttime = %currenttime% + 1
   timeout 1 >NUL
   IF "%currenttime%"=="%timeout%" GOTO :RUNKODI
GOTO LOOPINSTALLER


:BADEND
ECHO ERROR: Something was wrong. Operations interrupted.
pause
exit


:RUNKODI
ECHO ^> All done! Starting Kodi...
Start "" "%kodiexepath%"

REM Ensure Kodi have the focus
timeout 1 >NUL
set batchPath=%~dp0
WScript %batchPath%FocusKodiWindow.vbs
