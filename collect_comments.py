# 采集用户评论数据模块

import csv
import os
import time
from datetime import datetime

class CommentCollector:
    def __init__(self):
        # 确保data/user目录存在
        if not os.path.exists('data/user'):
            os.makedirs('data/user')
        
        # 使用固定的CSV文件名
        self.csv_file = 'data/user/xhs_comments.csv'
        
        # 定义CSV表头
        self.headers = [
            'user_id',       # 评论用户ID
            'comment_text',  # 评论内容
            'comment_time',  # 评论时间
            'collect_time',  # 数据采集时间
            'article_url'    # 评论所属文章URL
        ]
        
        # 添加processed_comments作为类属性
        self.processed_comments = set()
        
        # 如果文件不存在，创建文件并写入表头
        if not os.path.exists(self.csv_file):
            self._create_csv()

    def _create_csv(self):
        """创建CSV文件并写入表头"""
        with open(self.csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            print(f"创建评论数据文件：{self.csv_file}")

    def collect_comments(self, page):
        """采集评论数据"""
        try:
            # 定位评论区域
            comments = page.eles('.parent-comment')
            if not comments:
                print("未找到评论")
                return False
            
            comment_count = len(self.processed_comments)  # 使用类属性
            article_url = page.url  # 获取当前文章URL
            
            # 处理当前可见的评论
            for comment in comments:
                try:
                    comment_text = comment.ele('.note-text').text.strip()
                    
                    # 生成评论唯一标识（评论内容+文章URL）
                    comment_id = f"{comment_text}_{article_url}"
                    if comment_id in self.processed_comments:  # 使用类属性
                        continue
                    
                    # 获取评论用户ID
                    user_id = comment.ele('xpath:.//div[2]/div[1]/div[1]/a').text.strip()
                    # 获取评论时间
                    comment_time = comment.ele('.date').text.strip()
                    
                    # 获取当前时间作为采集时间
                    collect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 保存数据
                    self._save_to_csv([user_id, comment_text, comment_time, collect_time, article_url])
                    
                    self.processed_comments.add(comment_id)  # 使用类属性
                    comment_count += 1
                    print(f"已采集第{comment_count}条评论")
                    
                except Exception as e:
                    print(f"处理评论时出错: {e}")
                    continue
            
            # 如果已经采集到20条或更多，返回True
            if comment_count >= 20:
                print(f"评论采集完成，共采集{comment_count}条评论")
                return True
            
            # 如果还没采集够20条，返回False继续滚动
            return False
            
        except Exception as e:
            print(f"采集评论数据时出错: {e}")
            return False

    def _is_comment_exists(self, comment_text, article_url):
        """检查评论是否已存在于CSV文件中"""
        try:
            if not os.path.exists(self.csv_file):
                return False
                
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过表头
                for row in reader:
                    if len(row) >= 5 and row[1] == comment_text and row[4] == article_url:
                        return True
            return False
        except Exception:
            return False

    def _save_to_csv(self, data):
        """保存数据到CSV文件"""
        with open(self.csv_file, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data) 