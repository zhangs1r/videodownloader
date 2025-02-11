import requests
import os
import json
import re
from urllib.parse import urlparse
import time

class VideoDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
        
    def extract_video_id(self, url):
        """从URL中提取视频ID"""
        pattern = r'BV\w{10}'
        match = re.search(pattern, url)
        if match:
            return match.group()
        return None
        
    def get_video_info(self, bvid):
        """获取视频信息"""
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        response = requests.get(api_url, headers=self.headers)
        return response.json()
        
    def get_video_url(self, bvid, cid):
        """获取视频下载地址"""
        api_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80"
        response = requests.get(api_url, headers=self.headers)
        data = response.json()
        if data['code'] != 0:
            raise Exception(f"获取下载地址失败: {data['message']}")
        return data['data']['durl'][0]['url']
        
    def get_collection_info(self, bvid):
        """获取合集信息"""
        video_info = self.get_video_info(bvid)
        if video_info['code'] != 0:
            raise Exception(f"获取视频信息失败: {video_info['message']}")
            
        data = video_info['data']
        if data['videos'] > 1:  # 是合集
            pages = data['pages']
            collection_title = data['title']
            return {
                'is_collection': True,
                'title': collection_title,
                'pages': pages
            }
        return {'is_collection': False}
    
    def download_with_progress(self, url, file_path, callback=None, max_retries=3):
        """带进度的文件下载"""
        for retry in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024 * 1024  # 1MB
                
                start_time = time.time()
                last_time = start_time
                downloaded = 0
                last_downloaded = 0
                
                with open(file_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        downloaded += len(data)
                        f.write(data)
                        
                        if callback:
                            current_time = time.time()
                            # 每0.5秒更新一次速度
                            if current_time - last_time >= 0.5:
                                speed = (downloaded - last_downloaded) / (current_time - last_time) / (1024 * 1024)  # MB/s
                                progress = (downloaded / total_size) * 100
                                callback({
                                    'progress': progress,
                                    'total_size': total_size / (1024 * 1024),  # MB
                                    'downloaded_size': downloaded / (1024 * 1024),  # MB
                                    'speed': speed,
                                    'retry_count': retry
                                })
                                last_time = current_time
                                last_downloaded = downloaded
                
                # 验证文件大小
                if os.path.getsize(file_path) == total_size:
                    return True  # 下载成功
                else:
                    raise Exception("文件大小不匹配，可能下载不完整")
                
            except Exception as e:
                if retry < max_retries - 1:  # 如果还有重试次数
                    if callback:
                        callback({
                            'progress': 0,
                            'total_size': total_size / (1024 * 1024) if 'total_size' in locals() else 0,
                            'downloaded_size': 0,
                            'speed': 0,
                            'retry_count': retry + 1,
                            'error': str(e)
                        })
                    print(f"下载失败，正在进行第{retry + 1}次重试: {str(e)}")
                    time.sleep(2)  # 等待2秒后重试
                    continue
                else:
                    raise  # 重试次数用完，抛出异常
        
        return False
    
    def download_single_video(self, bvid, cid, title, save_path, callback=None, max_retries=3):
        """下载单个视频"""
        try:
            # 清理文件名
            clean_title = title.replace('\\', '-').replace('/', '-')
            video_url = self.get_video_url(bvid, cid)
            file_path = os.path.join(save_path, f"{clean_title}.mp4")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            success = self.download_with_progress(video_url, file_path, callback, max_retries)
            if success:
                return file_path
            else:
                raise Exception("下载失败，已达到最大重试次数")
        except Exception as e:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)  # 删除不完整的文件
                except:
                    pass
            raise
    
    def download_video(self, url, callback=None):
        """下载视频（支持合集）"""
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("无效的视频链接")
        
        # 获取视频/合集信息
        collection_info = self.get_collection_info(video_id)
        
        # 创建基本下载目录
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
        # 返回下载信息供UI使用
        return {
            'is_collection': collection_info['is_collection'],
            'info': collection_info
        }
    
    def download_collection(self, video_id, collection_info, callback=None):
        """下载整个合集"""
        # 使用更完整的文件名清理方法
        def clean_path(name):
            # 基础清理，处理最基本的非法字符
            invalid_chars = {
                '\\': '-', '/': '-', ':': '-', '*': '-', 
                '?': '-', '"': '-', '<': '-', '>': '-', 
                '|': '-', '\n': ' ', '\r': ' ', '\t': ' ',
                '《': '(', '》': ')', '【': '[', '】': ']',
                '（': '(', '）': ')', '、': '-', '，': ',',
                '。': '.', '！': '!', '？': '?', '：': '-'
            }
            for char, replacement in invalid_chars.items():
                name = name.replace(char, replacement)
            # 移除连续的特殊字符和空格
            while '  ' in name:
                name = name.replace('  ', ' ')
            while '--' in name:
                name = name.replace('--', '-')
            return name.strip(' .-')

        try:
            # 清理合集标题
            clean_collection_title = clean_path(collection_info['title'])
            if not clean_collection_title:
                clean_collection_title = "未命名合集"
            
            folder_name = os.path.join('downloads', clean_collection_title)
            
            # 确保路径长度不超过系统限制
            if len(folder_name) > 200:
                folder_name = folder_name[:200]
            
            # 创建目录，使用exist_ok=True避免竞争条件
            try:
                os.makedirs(folder_name, exist_ok=True)
            except Exception as e:
                raise Exception(f"创建目录失败 '{folder_name}': {str(e)}")
            
            total_videos = len(collection_info['pages'])
            failed_videos = []
            retry_count = {}  # 记录每个视频的重试次数
            
            for index, page in enumerate(collection_info['pages'], 1):
                try:
                    # 清理视频标题
                    clean_title = clean_path(page['part'])
                    if not clean_title:
                        clean_title = f"视频{index}"
                    
                    # 添加序号前缀，确保文件名唯一
                    file_name = f"{index:02d}-{clean_title}.mp4"
                    file_path = os.path.join(folder_name, file_name)
                    
                    # 确保单个视频的完整路径不超过系统限制
                    if len(file_path) > 255:  # Windows的MAX_PATH限制
                        base_path = os.path.dirname(file_path)
                        ext = os.path.splitext(file_name)[1]
                        new_name = f"{index:02d}-视频{index}{ext}"
                        file_path = os.path.join(base_path, new_name)
                    
                    if callback:
                        callback('new_video', {
                            'title': page['part'],
                            'status': '下载中',
                            'path': file_path
                        })
                    
                    max_retries = 3
                    for retry in range(max_retries):
                        try:
                            self.download_single_video(
                                video_id,
                                page['cid'],
                                f"{index:02d}-{clean_title}",
                                folder_name,
                                lambda p: callback('progress', p) if callback else None
                            )
                            
                            # 通知UI更新视频状态为完成
                            if callback:
                                callback('video_complete', {
                                    'title': page['part'],
                                    'status': '完成',
                                    'path': file_path,
                                    'progress': '100%'
                                })
                            break  # 下载成功，跳出重试循环
                            
                        except Exception as e:
                            retry_count[page['part']] = retry + 1
                            if retry < max_retries - 1:
                                if callback:
                                    callback('retry', {
                                        'title': page['part'],
                                        'retry_count': retry + 1,
                                        'error': str(e)
                                    })
                                print(f"下载失败，正在进行第{retry + 1}次重试: {page['part']} - {str(e)}")
                                time.sleep(2)  # 等待2秒后重试
                                continue
                            else:
                                print(f"下载失败: {page['part']} - {str(e)}")
                                failed_videos.append(page['part'])
                                if callback:
                                    callback('video_failed', {
                                        'title': page['part'],
                                        'error': str(e)
                                    })
                except Exception as e:
                    print(f"处理视频失败: {page['part']} - {str(e)}")
                    failed_videos.append(page['part'])
                    continue
            
            return {
                'success': len(collection_info['pages']) - len(failed_videos),
                'failed': failed_videos,
                'retry_info': retry_count
            }
        except Exception as e:
            raise Exception(f"处理合集失败: {str(e)}") 