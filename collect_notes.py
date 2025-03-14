# 笔记容器遍历方法模块

from collect_data import DataCollector
import time


class NotesCollector:
    def __init__(self):
        self.collected_count = 0
        
    def collect_notes(self, page):
        """遍历并采集笔记"""
        try:
            while self.collected_count < 20:
                # 每次循环重新获取笔记容器和笔记项
                feeds_container = page.ele('.feeds-container')
                if not feeds_container:
                    print("未找到笔记容器")
                    return False
                
                # 获取所有笔记项
                note_items = page.eles('.note-item')
                if not note_items:
                    print("未找到笔记项")
                    return False
                    
                # 遍历当前可见的笔记项
                for i, note in enumerate(note_items):
                    if self.collected_count >= 20:
                        print("已达到20篇笔记上限")
                        return True
                        
                    try:
                        # 每次重新获取最新的笔记元素
                        current_notes = page.eles('.note-item')
                        if i >= len(current_notes):
                            break
                            
                        current_note = current_notes[i]
                        # 点击笔记
                        current_note.click()
                        time.sleep(2)  # 等待笔记加载
                        
                        # 采集笔记数据
                        collector = DataCollector()
                        if collector.collect_article_data(page):
                            self.collected_count += 1
                            print(f"已采集第{self.collected_count}篇笔记")
                        
                        # 返回列表页
                        page.back()
                        time.sleep(2)  # 增加等待时间，确保页面完全加载
                        
                    except Exception as e:
                        print(f"采集单个笔记时出错: {e}")
                        # 确保返回列表页
                        if page.url != 'https://www.xiaohongshu.com':
                            page.back()
                            time.sleep(2)
                        continue
                
                # 如果还没采集够20篇，滚动加载更多
                if self.collected_count < 20:
                    page.actions.scroll(delta_y=1000)
                    time.sleep(2)  # 等待新内容加载
            
            return True
            
        except Exception as e:
            print(f"遍历采集笔记出错: {e}")
            return False 