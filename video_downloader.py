import requests
import os
import json
import re
from urllib.parse import urlparse

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
    
    def download_single_video(self, bvid, cid, title, save_path, callback=None):
        """下载单个视频"""
        video_url = self.get_video_url(bvid, cid)
        file_path = os.path.join(save_path, f"{title}.mp4")
        self.download_with_progress(video_url, file_path, callback)
        return file_path
    
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
        folder_name = os.path.join('downloads', collection_info['title'])
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        total_videos = len(collection_info['pages'])
        for index, page in enumerate(collection_info['pages'], 1):
            if callback:
                callback('status', f"正在下载 ({index}/{total_videos}): {page['part']}")
            
            try:
                self.download_single_video(
                    video_id,
                    page['cid'],
                    f"{index:02d}-{page['part']}",
                    folder_name,
                    lambda p: callback('progress', p) if callback else None
                )
            except Exception as e:
                print(f"下载失败: {page['part']} - {str(e)}")
                continue
        
    def download_with_progress(self, url, file_path, callback=None):
        """带进度的文件下载"""
        response = requests.get(url, headers=self.headers, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1KB
        
        with open(file_path, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(block_size):
                downloaded += len(data)
                f.write(data)
                if callback:
                    progress = (downloaded / total_size) * 100
                    callback(progress) 