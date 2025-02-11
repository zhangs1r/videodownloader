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
        
        # 添加下载列表
        self.download_list = ttk.Treeview(self.list_frame, columns=("标题", "进度", "状态"), show="headings")
        self.download_list.heading("标题", text="视频标题")
        self.download_list.heading("进度", text="下载进度")
        self.download_list.heading("状态", text="状态")
        self.download_list.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
    def update_progress(self, progress):
        """更新进度条和状态标签"""
        self.progress_bar["value"] = progress
        self.status_label["text"] = f"下载进度: {progress:.1f}%"
        self.root.update_idletasks()
        
    def update_status(self, text):
        """更新状态标签"""
        self.status_label["text"] = text
        self.root.update_idletasks()
        
    def download_callback(self, type, data):
        """下载回调函数"""
        if type == 'progress':
            self.update_progress(data)
        elif type == 'status':
            self.update_status(data)
    
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
            
            # 获取视频信息
            result = self.downloader.download_video(url)
            
            if result['is_collection']:
                # 是合集，询问是否下载整个合集
                collection_info = result['info']
                total_videos = len(collection_info['pages'])
                answer = messagebox.askyesno(
                    "发现合集",
                    f"该视频属于合集《{collection_info['title']}》\n"
                    f"共有 {total_videos} 个视频\n"
                    "是否下载整个合集？"
                )
                
                if answer:
                    # 下载整个合集
                    video_id = self.downloader.extract_video_id(url)
                    self.downloader.download_collection(
                        video_id,
                        collection_info,
                        self.download_callback
                    )
                else:
                    # 只下载当前视频
                    video_info = collection_info['pages'][0]  # 获取当前分P信息
                    self.downloader.download_single_video(
                        self.downloader.extract_video_id(url),
                        video_info['cid'],
                        video_info['part'],
                        'downloads',
                        lambda p: self.download_callback('progress', p)
                    )
            else:
                # 单个视频，直接下载
                video_id = self.downloader.extract_video_id(url)
                video_info = self.downloader.get_video_info(video_id)['data']
                self.downloader.download_single_video(
                    video_id,
                    video_info['cid'],
                    video_info['title'],
                    'downloads',
                    lambda p: self.download_callback('progress', p)
                )
            
            # 下载完成后的处理
            self.update_status("下载完成！")
            messagebox.showinfo("完成", "视频下载完成！")
            
            # 如果选择了自动关机
            if self.shutdown_var.get():
                os.system("shutdown /s /t 60")
                messagebox.showwarning("自动关机", "系统将在60秒后关机，取消请运行 'shutdown /a'")
        
        except ValueError as e:
            messagebox.showerror("错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"下载失败: {str(e)}")
        finally:
            self.download_btn["state"] = "normal"
            self.progress_bar["value"] = 0

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = VideoDownloaderUI(root)
    root.mainloop() 