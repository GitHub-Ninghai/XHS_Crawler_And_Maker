# 主程序集成模块

from DrissionPage import WebPage, ChromiumOptions
import json
import os
import time
from collect_data import DataCollector
from collect_comments import CommentCollector
from collect_notes import NotesCollector


class XHSCrawler:
    def __init__(self, port=None):
        # 创建浏览器选项实例
        co = ChromiumOptions()
        # 设置无头模式
        # co = ChromiumOptions().headless()
        # 设置初始窗口大小
        co.set_argument('--window-size', '800,600')

        # 如果指定了端口，则设置端口
        if port:
            co.set_port(port)

        # 创建浏览器实例
        self.page = WebPage(chromium_options=co)
        # 创建采集器实例
        self.comment_collector = CommentCollector()
        self.notes_collector = NotesCollector()

        # 添加新的属性来存储采集数量限制
        self.max_notes = 20  # 默认值
        self.max_comments = 20  # 默认值
        self.cookie_path = None  # 添加cookie路径属性

    # 添加新的方法来设置采集数量
    def set_limits(self, max_notes=20, max_comments=20):
        """设置采集数量限制"""
        self.max_notes = max_notes
        self.max_comments = max_comments
        print(f"设置采集限制：每个关键词{max_notes}篇笔记，每篇笔记{max_comments}条评论")

    def set_cookie_path(self, cookie_path):
        """设置cookie文件路径"""
        self.cookie_path = cookie_path

    def load_cookies(self):
        """加载指定的cookies文件"""
        try:
            if not self.cookie_path:
                # 如果没有指定cookie路径，使用默认的cookies目录
                cookies_dir = 'cookies'
                if not os.path.exists(cookies_dir):
                    raise FileNotFoundError("cookies目录不存在")

                cookie_files = [f for f in os.listdir(cookies_dir) if f.endswith('.json')]
                if not cookie_files:
                    raise FileNotFoundError("没有找到cookies文件")

                latest_file = max(cookie_files,
                                  key=lambda x: os.path.getctime(os.path.join(cookies_dir, x)))
                cookie_path = os.path.join(cookies_dir, latest_file)
            else:
                cookie_path = self.cookie_path

            # 读取cookies
            with open(cookie_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            print(f"加载cookies失败: {e}")
            return None

    def login(self):
        """使用cookies登录小红书"""
        try:
            # 先访问小红书
            self.page.get('https://www.xiaohongshu.com')
            time.sleep(2)

            # 加载并设置cookies
            cookies = self.load_cookies()
            self.page.set.cookies(cookies)
            print("已添加cookies")

            # 刷新页面使cookies生效
            self.page.refresh()
            time.sleep(5)
            return True

        except Exception as e:
            print(f"登录失败: {e}")
            return False

    def search_and_filter(self, keyword='python'):
        """搜索关键词并筛选"""
        try:
            # 定位搜索框并输入内容
            search_input = self.page.ele('#search-input')
            search_input.input(f'{keyword}\n')
            time.sleep(1)

            # 定位filter区域，执行鼠标悬浮
            filter_area = self.page.ele('.filter')
            filter_area.hover()
            time.sleep(1)

            # 点击"最热"选项
            hot_tab = self.page.ele('xpath:/html/body/div[5]/div/li[3]/span')
            if hot_tab:
                hot_tab.click()
                print("已点击最热选项")
                time.sleep(2)
                return True
            else:
                print("未找到最热选项")
                return False

        except Exception as e:
            print(f"搜索筛选失败: {e}")
            return False

    def collect_note_and_comments(self, note_element):
        """采集单篇笔记及其评论"""
        try:
            # 增加点击前的等待时间
            time.sleep(2)
            note_element.click()
            time.sleep(2)  # 增加点击后的等待时间

            collector = DataCollector()
            if collector.collect_article_data(self.page):
                self.comment_collector.processed_comments.clear()

                comment_count = 0
                no_new_comments_count = 0

                while comment_count < self.max_comments:
                    time.sleep(1)  # 每次循环前等待
                    comments_container = self.page.ele('.comments-el')
                    if not comments_container:
                        print("未找到评论容器")
                        return False

                    # 获取滚动前的评论元素数量
                    current_comments = self.page.eles('.comment-item')
                    previous_count = len(current_comments) if current_comments else 0

                    # 滚动加载更多评论
                    self.page.actions.scroll(delta_y=900)  # 使用较小的滚动步长
                    time.sleep(1.5)  # 等待新内容加载

                    # 获取滚动后的评论元素数量
                    new_comments = self.page.eles('.comment-item')
                    new_count = len(new_comments) if new_comments else 0

                    # 检查是否有新评论元素加载
                    if new_count <= previous_count:
                        no_new_comments_count += 1
                        print(f"连续{no_new_comments_count}次未发现新评论元素")
                    else:
                        no_new_comments_count = 0

                    # 采集当前可见的评论
                    if self.comment_collector.collect_comments(self.page):
                        comment_count = len(self.comment_collector.processed_comments)
                        print(f"当前已采集{comment_count}条评论")

                    # 如果连续3次没有新评论元素，则退出
                    if no_new_comments_count >= 3:
                        print("已无法加载更多评论")
                        break

                    # 如果还没有任何评论且已尝试3次，则退出
                    if comment_count == 0 and no_new_comments_count >= 3:
                        print("该笔记可能没有评论")
                        break

                    # 如果已达到目标评论数，退出循环
                    if comment_count >= self.max_comments:
                        break

                print(f"笔记评论采集完成，共采集{comment_count}条评论")
                return True

            return False

        except Exception as e:
            print(f"采集笔记和评论时出错: {e}")
            return False
        finally:
            time.sleep(1)  # 返回前等待
            self.page.back()
            time.sleep(2)  # 增加返回后的等待时间

    def collect_all_notes(self):
        """遍历采集笔记和评论"""
        try:
            collected_count = 0
            no_new_notes_count = 0
            processed_indexes = set()  # 记录已处理的笔记索引

            while collected_count < self.max_notes:
                time.sleep(1.5)  # 每次循环前等待

                # 获取当前可见的笔记
                note_items = self.page.eles('.note-item')
                current_notes_count = len(note_items) if note_items else 0

                if not note_items:
                    print("未找到笔记项")
                    if no_new_notes_count >= 2:
                        break
                    no_new_notes_count += 1
                    time.sleep(2)  # 未找到笔记时等待更长时间
                    continue

                # 遍历当前可见的所有笔记
                for i in range(current_notes_count):
                    if collected_count >= self.max_notes:
                        print(f"已达到{self.max_notes}篇笔记上限")
                        return True

                    # 跳过已处理的笔记
                    if i in processed_indexes:
                        continue

                    try:
                        time.sleep(1)  # 处理每个笔记前等待

                        # 重新获取最新的笔记列表和当前要处理的笔记
                        current_notes = self.page.eles('.note-item')
                        if i >= len(current_notes):
                            break

                        current_note = current_notes[i]
                        if self.collect_note_and_comments(current_note):
                            collected_count += 1
                            processed_indexes.add(i)  # 记录已处理的索引
                            print(f"已采集第{collected_count}篇笔记及其评论")
                            no_new_notes_count = 0
                            time.sleep(2)  # 成功采集后等待

                    except Exception as e:
                        print(f"处理单个笔记时出错: {e}")
                        time.sleep(3)  # 出错后等待更长时间
                        continue

                # 如果当前页面的笔记都处理完了，继续滚动加载更多
                if len(processed_indexes) >= current_notes_count:
                    # 滚动加载更多笔记
                    self.page.actions.scroll(delta_y=2300)
                    time.sleep(3)  # 增加滚动后的等待时间

                    # 获取滚动后的笔记数量
                    new_notes = self.page.eles('.note-item')
                    if len(new_notes) <= current_notes_count:
                        no_new_notes_count += 1
                        if no_new_notes_count >= 2:
                            print("已无法加载更多笔记")
                            break
                    else:
                        no_new_notes_count = 0

            return True

        except Exception as e:
            print(f"遍历采集笔记出错: {e}")
            return False

    def close(self):
        """关闭浏览器"""
        if hasattr(self, 'page'):
            self.page.quit()


def main():
    crawler = XHSCrawler()
    try:
        if crawler.login() and \
                crawler.search_and_filter() and \
                crawler.collect_all_notes():
            print("所有数据采集完成")
        else:
            print("数据采集过程中出现错误")
    finally:
        input("按回车键退出...")
        crawler.close()


if __name__ == '__main__':
    main()
