# 采集笔记数据模块

import csv
import os
import time
from datetime import datetime

class DataCollector:
    def __init__(self):
        # 确保data目录存在
        if not os.path.exists('data/notes'):
            os.makedirs('data/notes')
        # 获取当前日期
        now = datetime.now()
        formatted_date = now.strftime('%Y%m%d')


        self.csv_file = f'data/notes/xhs_python_notes_{formatted_date}.csv'

        
        # 定义CSV表头
        self.headers = [
            'title',          # 文章标题
            'author',         # 作者
            'content',        # 文章内容
            'edit_time',      # 编辑时间
            'likes',          # 点赞量
            'collects',       # 收藏量
            'comments',       # 评论量
            'collect_time',   # 采集时间
            'url'            # 文章URL
        ]
        
        # 如果文件不存在，创建文件并写入表头
        if not os.path.exists(self.csv_file):
            self._create_csv()

    def _create_csv(self):
        """创建CSV文件并写入表头"""
        with open(self.csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            print(f"创建数据文件：{self.csv_file}")

    def collect_article_data(self, page):
        """采集文章数据"""
        try:
            # 等待页面加载完成
            time.sleep(3)
            # 获取文章标题
            title = page.ele('xpath://*[@id="detail-title"]').text.strip()
            # 获取作者
            author = page.ele('xpath://*[@id="noteContainer"]/div[4]/div[1]/div/div[1]/a[2]/span').text.strip()
            
            
            
            # 获取文章内容
            content = page.ele('xpath://*[@id="detail-desc"]').text.strip()
            
            # 获取编辑时间
            edit_time = page.ele('xpath://*[@id="noteContainer"]/div[4]/div[2]/div[1]/div[3]/span[1]').text.strip()
            
            # 获取点赞量
            likes = page.ele('xpath://*[@id="noteContainer"]/div[4]/div[3]/div/div/div[1]/div[2]/div/div[1]/span[1]/span[2]').text.strip()
            
            # 获取收藏量
            collects = page.ele('xpath://*[@id="note-page-collect-board-guide"]/span').text.strip()
            
            # 获取评论量
            comments = page.ele('xpath://*[@id="noteContainer"]/div[4]/div[3]/div/div/div[1]/div[2]/div/div[1]/span[3]/span').text.strip()
            
            # 获取当前URL
            url = page.url
            
            # 获取采集时间
            collect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 检查是否已存在相同URL的数据
            if not self._is_url_exists(url):
                # 保存数据
                self._save_to_csv([title, author, content, edit_time, likes, collects, comments, collect_time, url])
                print(f"已采集文章：{title}")
                return True
            else:
                print(f"文章已存在，跳过：{title}")
                return False
            
        except Exception as e:
            print(f"采集数据时出错: {e}")
            return False

    def _is_url_exists(self, url):
        """检查URL是否已存在于CSV文件中"""
        try:
            if not os.path.exists(self.csv_file):
                return False
                
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过表头
                urls = [row[8] for row in reader if len(row) > 8]  # URL在第9列
                return url in urls
        except Exception:
            return False

    def _save_to_csv(self, data):
        """保存数据到CSV文件"""
        with open(self.csv_file, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data) 