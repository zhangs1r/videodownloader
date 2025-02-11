import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import requests
from PIL import Image, ImageTk
import os
from video_downloader import VideoDownloader
from tkinter import messagebox

class VideoDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bilibili视频下载器")
        self.root.geometry("800x600")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # 顶部搜索区域
        self.search_frame = ttk.LabelFrame(self.main_frame, text="视频链接", padding=5)
        self.search_frame.pack(fill=X, padx=5, pady=5)
        
        self.url_entry = ttk.Entry(self.search_frame)
        self.url_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        self.download_btn = ttk.Button(self.search_frame, text="开始下载", 
                                     command=self.start_download)
        self.download_btn.pack(side=LEFT, padx=5)
        
        # 中部进度显示区域
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="下载进度", padding=5)
        self.progress_frame.pack(fill=X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=100, mode='determinate')
        self.progress_bar.pack(fill=X, padx=5, pady=5)
        
        self.status_label = ttk.Label(self.progress_frame, text="等待下载...")
        self.status_label.pack(padx=5)
        
        # 底部下载列表区域
        self.list_frame = ttk.LabelFrame(self.main_frame, text="下载列表", padding=5)
        self.list_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # 创建自动关机选项
        self.shutdown_var = tk.BooleanVar()
        self.shutdown_check = ttk.Checkbutton(self.main_frame, 
                                            text="下载完成后自动关机",
                                            variable=self.shutdown_var)
        self.shutdown_check.pack(pady=5)
        
        self.downloader = VideoDownloader()
        
        # 修改下载列表的创建
        self.download_list = ttk.Treeview(
            self.list_frame, 
            columns=("标题", "进度", "状态", "保存路径"), 
            show="headings"
        )
        self.download_list.heading("标题", text="视频标题")
        self.download_list.heading("进度", text="下载进度")
        self.download_list.heading("状态", text="状态")
        self.download_list.heading("保存路径", text="保存路径")
        
        # 设置列宽
        self.download_list.column("标题", width=250)
        self.download_list.column("进度", width=200)
        self.download_list.column("状态", width=100)
        self.download_list.column("保存路径", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.download_list.yview)
        self.download_list.configure(yscrollcommand=scrollbar.set)
        
        self.download_list.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 添加一个字典来跟踪下载项
        self.download_items = {}
        
    def clean_filename(self, filename):
        """清理文件名，移除或替换非法字符"""
        # Windows文件系统中的非法字符和其他需要处理的特殊字符
        invalid_chars = {
            '\\': '-', '/': '-', ':': '-', '*': '-', 
            '?': '-', '"': '-', '<': '-', '>': '-', 
            '|': '-', '\n': ' ', '\r': ' ', '\t': ' ',
            '《': '(', '》': ')', '【': '[', '】': ']',
            '（': '(', '）': ')', '、': '-', '，': ',',
            '。': '.', '！': '!', '？': '?', '：': '-',
            '；': ';', '"': '"', '"': '"', ''': "'",
            ''': "'", '「': '[', '」': ']', '『': '[',
            '』': ']', '〈': '<', '〉': '>', '…': '-',
            '—': '-', '～': '~', '·': '-', '￥': '$',
            '％': '%', '＃': '#', '＆': '&', '＊': '*',
            '＋': '+', '－': '-', '／': '/', '＝': '=',
            '＠': '@', '＼': '\\', '＾': '^', '｜': '|',
            '～': '~'
        }
        
        # 替换所有特殊字符
        for char, replacement in invalid_chars.items():
            filename = filename.replace(char, replacement)
        
        # 移除连续的空格和特殊字符
        while '  ' in filename:
            filename = filename.replace('  ', ' ')
        while '--' in filename:
            filename = filename.replace('--', '-')
        
        # 移除首尾空格、点和特殊字符
        filename = filename.strip(' .-')
        
        # 如果文件名为空，使用默认名称
        if not filename:
            filename = "video"
        
        # 限制文件名长度（Windows最大路径长度限制）
        if len(filename) > 200:
            # 保留扩展名
            name, ext = os.path.splitext(filename)
            filename = name[:196] + ext if ext else name[:200]
        
        return filename
        
    def update_progress(self, data):
        """更新进度条和状态标签"""
        progress = data['progress']
        speed = data.get('speed', 0)
        downloaded_size = data.get('downloaded_size', 0)
        total_size = data.get('total_size', 0)
        
        self.progress_bar["value"] = progress
        self.status_label["text"] = (
            f"下载进度: {progress:.1f}% "
            f"({downloaded_size:.1f}MB/{total_size:.1f}MB) "
            f"- {speed:.1f}MB/s"
        )
        self.root.update_idletasks()
        
    def update_status(self, text):
        """更新状态标签"""
        self.status_label["text"] = text
        self.root.update_idletasks()
        
    def update_download_progress(self, title, data):
        """更新下载列表中的进度"""
        if title in self.download_items:
            item_id = self.download_items[title]
            current_values = list(self.download_list.item(item_id)['values'])
            progress = data['progress']
            downloaded_size = data.get('downloaded_size', 0)
            total_size = data.get('total_size', 0)
            speed = data.get('speed', 0)
            
            current_values[1] = (
                f"{progress:.1f}% "
                f"({downloaded_size:.1f}MB/{total_size:.1f}MB) "
                f"- {speed:.1f}MB/s"
            )
            current_values[2] = "下载中"
            self.download_list.item(item_id, values=current_values)
            self.download_list.see(item_id)

    def add_download_record(self, title, status="等待中", save_path="", progress="0%"):
        """添加或更新下载记录"""
        if title in self.download_items:
            item_id = self.download_items[title]
            current_values = list(self.download_list.item(item_id)['values'])
            # 只更新需要更新的值
            if progress != "0%":
                current_values[1] = progress
            if status != "等待中":
                current_values[2] = status
            if save_path != "":
                current_values[3] = save_path
            self.download_list.item(item_id, values=current_values)
        else:
            item_id = self.download_list.insert("", "end", values=(title, progress, status, save_path))
            self.download_items[title] = item_id
        self.download_list.see(item_id)

    def download_callback(self, type, data):
        """下载回调函数"""
        if type == 'progress':
            self.update_progress(data)
            # 更新当前下载项的进度
            if hasattr(self, 'current_download_title'):
                if 'retry_count' in data and data['retry_count'] > 0:
                    self.update_status(f"第{data['retry_count']}次重试下载中...")
                self.update_download_progress(self.current_download_title, data)
        elif type == 'retry':
            # 显示重试信息
            self.update_status(f"下载失败，正在进行第{data['retry_count']}次重试...")
            self.add_download_record(
                data['title'],
                f"重试 ({data['retry_count']}/3)",
                "",
                "0%"
            )
        elif type == 'status':
            self.update_status(data)
        elif type == 'new_video':
            # 添加新的视频下载记录
            self.current_download_title = data['title']
            self.add_download_record(
                data['title'],
                data['status'],
                data['path']
            )
        elif type == 'video_complete':
            # 更新视频下载完成状态
            self.add_download_record(
                data['title'],
                data['status'],
                data['path'],
                data['progress']
            )
        elif type == 'video_failed':
            # 更新视频下载失败状态
            self.add_download_record(
                data['title'],
                "失败",
                "N/A",
                "0%"
            )

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            return
            
        # 创建新线程进行下载
        download_thread = threading.Thread(target=self.download_video, args=(url,))
        download_thread.daemon = True
        download_thread.start()
        
    def download_video(self, url):
        """实际的下载处理函数"""
        try:
            self.update_status("正在获取视频信息...")
            self.download_btn["state"] = "disabled"
            
            # 确保下载目录存在
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            
            # 获取视频信息
            result = self.downloader.download_video(url)
            
            if result['is_collection']:
                collection_info = result['info']
                total_videos = len(collection_info['pages'])
                collection_title = self.clean_filename(collection_info['title'])
                
                # 创建合集目录
                folder_path = os.path.join('downloads', collection_title)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                self.add_download_record(
                    f"合集：{collection_title}",
                    "下载中",
                    folder_path
                )
                
                answer = messagebox.askyesno(
                    "发现合集",
                    f"该视频属于合集《{collection_title}》\n"
                    f"共有 {total_videos} 个视频\n"
                    "是否下载整个合集？"
                )
                
                if answer:
                    video_id = self.downloader.extract_video_id(url)
                    # 清理每个视频的文件名
                    for page in collection_info['pages']:
                        page['part'] = self.clean_filename(page['part'])
                    result = self.downloader.download_collection(
                        video_id,
                        collection_info,
                        self.download_callback
                    )
                    
                    # 更新合集下载状态
                    status = "完成"
                    if result['failed']:
                        status = f"部分完成 (失败: {len(result['failed'])}个)"
                    self.add_download_record(
                        f"合集：{collection_title}",
                        status,
                        folder_path,
                        "100%"
                    )
                else:
                    # 删除合集记录，只下载单个视频
                    self.download_list.delete(self.download_items[f"合集：{collection_title}"])
                    del self.download_items[f"合集：{collection_title}"]
                    
                    video_info = collection_info['pages'][0]
                    clean_title = self.clean_filename(video_info['part'])
                    save_path = os.path.join('downloads', f"{clean_title}.mp4")
                    self.current_download_title = clean_title
                    
                    # 添加单个视频记录
                    self.add_download_record(
                        clean_title,  # 使用清理后的标题
                        "下载中",
                        save_path
                    )
                    
                    self.downloader.download_single_video(
                        self.downloader.extract_video_id(url),
                        video_info['cid'],
                        clean_title,  # 使用清理后的标题
                        'downloads',
                        lambda p: self.download_callback('progress', p)
                    )
                    
                    # 更新状态为完成
                    self.add_download_record(
                        clean_title,  # 使用清理后的标题
                        "完成",
                        save_path,
                        "100%"
                    )
            else:
                video_id = self.downloader.extract_video_id(url)
                video_info = self.downloader.get_video_info(video_id)['data']
                clean_title = self.clean_filename(video_info['title'])
                save_path = os.path.join('downloads', f"{clean_title}.mp4")
                self.current_download_title = clean_title
                
                # 添加下载记录
                self.add_download_record(
                    clean_title,  # 使用清理后的标题
                    "下载中",
                    save_path
                )
                
                self.downloader.download_single_video(
                    video_id,
                    video_info['cid'],
                    clean_title,  # 使用清理后的标题
                    'downloads',
                    lambda p: self.download_callback('progress', p)
                )
                
                # 更新状态为完成
                self.add_download_record(
                    clean_title,  # 使用清理后的标题
                    "完成",
                    save_path,
                    "100%"
                )
            
            self.update_status("下载完成！")
            messagebox.showinfo("完成", "视频下载完成！")
            
            if self.shutdown_var.get():
                os.system("shutdown /s /t 60")
                messagebox.showwarning("自动关机", "系统将在60秒后关机，取消请运行 'shutdown /a'")
        
        except ValueError as e:
            self.handle_error(str(e), url)
        except Exception as e:
            self.handle_error(f"下载失败: {str(e)}", 
                             self.current_download_title if hasattr(self, 'current_download_title') else None)
        finally:
            self.download_btn["state"] = "normal"
            self.progress_bar["value"] = 0

    def handle_error(self, error_msg, title=None):
        """统一处理错误"""
        # 提取更有用的错误信息
        if "创建目录失败" in error_msg:
            error_msg = f"无法创建下载目录，请检查:\n1. 文件夹名称是否包含特殊字符\n2. 是否有写入权限\n3. 路径是否过长\n\n详细错误: {error_msg}"
        elif "文件名或目录名太长" in error_msg:
            error_msg = "文件名或路径过长，请尝试使用更短的文件名"
        
        messagebox.showerror("错误", error_msg)
        if title:
            self.add_download_record(title, "失败", "N/A", "0%")
        self.update_status(f"错误: {error_msg}")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = VideoDownloaderUI(root)
    root.mainloop() 