# Bilibili视频下载器

一个基于Python的B站视频下载工具，支持单个视频和视频合集的下载，具有现代化的图形界面。

## 功能特点

- 📺 支持下载单个视频和视频合集
- 🎯 自动创建以合集名称命名的文件夹
- 📊 实时显示下载进度、速度和文件大小
- 🔄 下载失败自动重试（最多3次）
- 💻 自动关机选项
- 🌙 深色主题界面
- 📝 下载历史记录
- ⚡ 多线程下载
- 🧹 自动处理文件名中的非法字符

## 运行环境

- Python 3.6+
- Windows/Linux/MacOS

## 依赖安装

```bash
pip install requests pillow ttkbootstrap
```

## 使用方法

1. 运行程序：
```bash
python video_downloader_ui.py
```

2. 在输入框中粘贴B站视频链接，支持以下格式：
   - 单个视频：`https://www.bilibili.com/video/BVxxxxxx`
   - 合集视频：`https://www.bilibili.com/video/BVxxxxxx?p=1`

3. 点击"开始下载"按钮开始下载
   - 如果是合集视频，会询问是否下载整个合集
   - 可以选择只下载当前视频或整个合集

4. 可选功能：
   - 勾选"下载完成后自动关机"选项可在下载完成后自动关机
   - 下载失败会自动重试，最多重试3次

## 界面说明

- 顶部搜索栏：输入视频链接
- 中部进度区：
  - 显示当前下载进度百分比
  - 显示已下载/总文件大小（MB）
  - 显示实时下载速度（MB/s）
- 底部列表区：
  - 显示所有下载任务
  - 包含视频标题、下载进度、状态和保存路径
  - 支持滚动查看历史记录

## 文件说明

- `video_downloader_ui.py`: 主程序，包含GUI界面
- `video_downloader.py`: 核心下载功能模块
- `setup.py`: 打包配置文件
- `.gitignore`: Git忽略配置文件
- `LICENSE`: MIT许可证文件

## 下载路径

- 单个视频：保存在 `downloads` 目录下
- 视频合集：自动创建以合集标题命名的文件夹，所有分P视频下载到该文件夹中

## 注意事项

1. 下载速度受网络环境影响
2. 请确保磁盘有足够的存储空间
3. 自动关机功能需要系统权限
4. 建议使用稳定的网络连接
5. 遵守B站用户协议，合理使用下载功能

## 错误处理

1. 下载失败自动重试
   - 程序会自动重试最多3次
   - 每次重试间隔2秒
   - 显示当前重试次数和原因

2. 文件名处理
   - 自动处理文件名中的非法字符
   - 自动处理中文标点符号
   - 限制文件名最大长度

3. 下载状态显示
   - 显示详细的错误信息
   - 在下载列表中标记失败状态
   - 记录失败原因

## 版本历史

### v1.0.0 (2024-03)
- 初始版本发布
- 实现基本下载功能
- 添加图形界面
- 支持进度显示和速度显示
- 添加下载历史记录
- 实现自动重试机制
- 添加文件名处理功能
- 支持自动关机选项

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License

## 致谢

- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap)
- [requests](https://github.com/psf/requests)
- [bilibili](https://www.bilibili.com)

## 便携版使用说明

### 方法一：直接使用打包版

1. 下载发布页面的`Bilibili视频下载器.zip`
2. 解压到任意位置
3. 双击运行`Bilibili视频下载器.exe`

注意事项：
- 首次运行可能被杀毒软件拦截，请允许运行
- 建议将程序放在非系统目录下（如D盘）
- 确保解压目录有写入权限

### 方法二：自行打包

1. 安装打包工具：
```bash
pip install cx_Freeze
```

2. 运行打包命令：
```bash
python setup.py build
```

3. 在build目录下找到生成的exe文件

### 运行环境要求

- Windows 7/8/10/11
- 不需要安装Python
- 需要管理员权限（用于自动关机功能）

### 下载地址

#### 最新版本 v1.0.0

- Windows 64位: [Bilibili视频下载器-v1.0.0-win64.zip](https://github.com/your-repo/releases/download/v1.0.0/Bilibili视频下载器-v1.0.0-win64.zip)
- Windows 32位: [Bilibili视频下载器-v1.0.0-win32.zip](https://github.com/your-repo/releases/download/v1.0.0/Bilibili视频下载器-v1.0.0-win32.zip)

### 文件说明

发布包包含：
- Bilibili视频下载器.exe (主程序)
- README.md (使用说明)
- LICENSE (许可证)
- lib/ (依赖库)

### 快速开始

1. 下载对应系统版本的zip包
2. 解压到任意位置（建议英文路径）
3. 双击运行`Bilibili视频下载器.exe`
4. 粘贴视频链接并点击下载

### 常见问题

1. 提示"丢失DLL"
   - 确保解压完整
   - 尝试安装VC运行库

2. 无法运行程序
   - 检查是否被杀毒软件拦截
   - 以管理员身份运行

3. 下载路径问题
   - 默认下载到程序所在目录
   - 确保目录有写入权限
