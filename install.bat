@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM py-process-monitor Windows 自动安装脚本
REM 支持在没有 Python 环境的 Windows 系统上自动安装和运行

echo ======================================
echo   py-process-monitor 自动安装脚本
echo ======================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] 检测到管理员权限
) else (
    echo [WARNING] 建议以管理员身份运行此脚本
    echo [INFO] 继续安装...
)

REM 检查 Python 是否已安装
echo [INFO] 检查 Python 安装状态...
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [SUCCESS] Python !PYTHON_VERSION! 已安装
    set PYTHON_CMD=python
    goto :check_pip
)

python3 --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [SUCCESS] Python !PYTHON_VERSION! 已安装
    set PYTHON_CMD=python3
    goto :check_pip
)

REM 安装 Python
echo [WARNING] 未检测到 Python
echo [INFO] 正在下载并安装 Python...

REM 检查是否有 Chocolatey
choco --version >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] 使用 Chocolatey 安装 Python...
    choco install python -y
    set PYTHON_CMD=python
) else (
    echo [INFO] Chocolatey 未安装，下载 Python 安装程序...
    
    REM 创建临时目录
    set TEMP_DIR=%TEMP%\py-process-install
    if not exist "!TEMP_DIR!" mkdir "!TEMP_DIR!"
    
    REM 下载 Python
    echo [INFO] 正在下载 Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile '!TEMP_DIR!\python-installer.exe'"
    
    if exist "!TEMP_DIR!\python-installer.exe" (
        echo [INFO] 正在安装 Python...
        "!TEMP_DIR!\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1
        
        REM 等待安装完成
        timeout /t 30 /nobreak >nul
        
        REM 刷新环境变量
        call refreshenv >nul 2>&1
        
        set PYTHON_CMD=python
    ) else (
        echo [ERROR] Python 下载失败
        echo [INFO] 请手动下载并安装 Python: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM 验证 Python 安装
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python 安装失败或未添加到 PATH
    echo [INFO] 请重新启动命令提示符或手动添加 Python 到 PATH
    pause
    exit /b 1
)

:check_pip
REM 检查 pip
echo [INFO] 检查 pip...
pip --version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] pip 已安装
    set PIP_CMD=pip
) else (
    echo [INFO] 安装 pip...
    %PYTHON_CMD% -m ensurepip --upgrade
    set PIP_CMD=pip
)

REM 设置项目目录
set PROJECT_DIR=%USERPROFILE%\py-process-monitor

REM 下载项目
echo [INFO] 正在下载 py-process-monitor...

if exist "%PROJECT_DIR%" (
    echo [WARNING] 项目目录已存在，正在更新...
    cd /d "%PROJECT_DIR%"
    
    git --version >nul 2>&1
    if %errorLevel% == 0 (
        if exist ".git" (
            git pull
        ) else (
            cd ..
            rmdir /s /q "py-process-monitor"
            git clone https://github.com/mhxy13867806343/py-process.git py-process-monitor
        )
    ) else (
        echo [INFO] Git 未安装，重新下载项目...
        cd ..
        rmdir /s /q "py-process-monitor"
        goto :download_zip
    )
) else (
    cd /d "%USERPROFILE%"
    
    git --version >nul 2>&1
    if %errorLevel% == 0 (
        git clone https://github.com/mhxy13867806343/py-process.git py-process-monitor
    ) else (
        :download_zip
        echo [INFO] Git 未安装，使用 PowerShell 下载...
        mkdir py-process-monitor
        cd py-process-monitor
        
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/mhxy13867806343/py-process/archive/main.zip' -OutFile 'main.zip'"
        
        if exist "main.zip" (
            powershell -Command "Expand-Archive -Path 'main.zip' -DestinationPath '.' -Force"
            
            REM 移动文件
            if exist "py-process-main" (
                xcopy "py-process-main\*" "." /E /H /Y
                rmdir /s /q "py-process-main"
                del "main.zip"
            )
        ) else (
            echo [ERROR] 项目下载失败
            pause
            exit /b 1
        )
    )
)

cd /d "%PROJECT_DIR%"
echo [SUCCESS] 项目下载完成: %PROJECT_DIR%

REM 安装依赖
echo [INFO] 正在安装项目依赖...

REM 升级 pip
%PIP_CMD% install --upgrade pip

REM 安装项目依赖
if exist "requirements.txt" (
    %PIP_CMD% install -r requirements.txt
)

REM 安装项目本身
%PIP_CMD% install -e .

echo [SUCCESS] 依赖安装完成

REM 创建启动脚本
echo [INFO] 创建启动脚本...

set LAUNCHER_DIR=%USERPROFILE%\AppData\Local\bin
if not exist "%LAUNCHER_DIR%" mkdir "%LAUNCHER_DIR%"

set LAUNCHER_PATH=%LAUNCHER_DIR%\process-monitor.bat

echo @echo off > "%LAUNCHER_PATH%"
echo cd /d "%PROJECT_DIR%" >> "%LAUNCHER_PATH%"
echo %PYTHON_CMD% -m process_monitor.cli >> "%LAUNCHER_PATH%"

echo [SUCCESS] 启动脚本创建完成: %LAUNCHER_PATH%

REM 添加到 PATH（需要管理员权限）
echo [INFO] 尝试添加到系统 PATH...
setx PATH "%PATH%;%LAUNCHER_DIR%" >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] 已添加到 PATH
) else (
    echo [WARNING] 无法自动添加到 PATH，请手动添加: %LAUNCHER_DIR%
)

REM 显示使用说明
echo.
echo [SUCCESS] 安装完成！
echo.
echo [INFO] 使用方法:
echo   1. 重新启动命令提示符
echo   2. 运行命令: process-monitor
echo   3. 或者直接运行: "%LAUNCHER_PATH%"
echo   4. 或者进入项目目录运行: cd "%PROJECT_DIR%" ^&^& %PYTHON_CMD% example.py
echo.
echo [INFO] 项目位置: %PROJECT_DIR%
echo [INFO] 启动脚本: %LAUNCHER_PATH%
echo.
echo [WARNING] 如果命令未找到，请重新启动命令提示符或手动添加到 PATH
echo.

echo 按任意键退出...
pause >nul