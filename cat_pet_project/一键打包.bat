@echo off
chcp 65001 >nul
title 加菲猫桌宠 - 一键打包工具

echo ========================================
echo   🐱 加菲猫桌面宠物 - 一键打包
echo ========================================
echo.

:: 检查Python
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python！
    echo 请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ 检测到 Python 环境
python --version
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 安装依赖
echo 📦 安装依赖库...
pip install pillow pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ❌ 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo 🖼️  预处理图片（自动抠图）...
python preprocess_images.py
if errorlevel 1 (
    echo ⚠️  图片预处理出现问题，继续打包...
)

echo.
echo 🔨 开始打包 EXE 文件...
echo.

:: 清理旧的打包文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "加菲猫桌宠.spec" del /q "加菲猫桌宠.spec"

:: 使用PyInstaller打包
pyinstaller --noconfirm --onefile --windowed ^
    --name "加菲猫桌宠" ^
    --add-data "assets;assets" ^
    cat_pet.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ 打包完成！
echo ========================================
echo.
echo 📂 EXE 文件位置: dist\加菲猫桌宠.exe
echo 🐱 双击即可运行，无需安装 Python
echo.
echo 💡 使用说明:
echo    - 左键拖动：移动猫咪位置
echo    - 左键点击：触发互动动画
echo    - 滚轮滚动：调整猫咪大小
echo    - 右键点击：打开功能菜单
echo.
echo 🎨 如果抠图效果不好，可以用在线工具手动抠图
echo    然后替换 assets 文件夹里的图片重新打包
echo.

:: 询问是否打开输出目录
set /p open="是否打开输出文件夹？(Y/N): "
if /i "%open%"=="Y" (
    explorer dist
)

pause
