from cx_Freeze import setup, Executable
import sys

# 依赖项
build_exe_options = {
    "packages": [
        "os", 
        "requests", 
        "tkinter", 
        "ttkbootstrap", 
        "PIL",
        "json",
        "re",
        "threading",
        "urllib"
    ],
    "includes": [
        "tkinter",
        "tkinter.ttk",
        "ttkbootstrap",
        "PIL._tkinter_finder"
    ],
    "include_files": [
        # 添加其他需要的资源文件
        "README.md",
        "LICENSE"
    ],
    "excludes": [],
    # 添加必要的 DLL 文件
    "include_msvcr": True
}

# 目标文件
target = Executable(
    script="video_downloader_ui.py",  # 主程序文件
    base="Win32GUI" if sys.platform == "win32" else None,  # 使用 GUI 基础
    target_name="Bilibili视频下载器.exe",  # 生成的exe文件名
    icon="icon.ico" if sys.platform == "win32" else None,  # 如果有图标的话
)

setup(
    name="Bilibili视频下载器",
    version="1.0.0",
    description="B站视频下载工具",
    options={"build_exe": build_exe_options},
    executables=[target]
) 