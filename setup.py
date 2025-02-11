from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "requests", "tkinter", "ttkbootstrap", "PIL"],
    "includes": ["tkinter", "ttkbootstrap"],
    "include_files": ["README.md", "LICENSE"],
    "excludes": []
}

setup(
    name="Bilibili视频下载器",
    version="1.0.0",
    description="B站视频下载工具",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "video_downloader_ui.py",
        base="Win32GUI",
        target_name="Bilibili视频下载器.exe",
        icon="icon.ico"  # 如果有图标的话
    )]
) 