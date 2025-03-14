# 采集工具 gradio前端界面


import gradio as gr
import json
import os
from copy_cookie import CookieManager
from star_xhs import XHSCrawler
import webbrowser
from datetime import datetime
import time

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    raise FileNotFoundError(f"未找到 Edge 浏览器可执行文件: {edge_path}")

    # 注册浏览器
webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
class XHSCrawlerWeb:
    def __init__(self):
        self.keyword = None  # 改为单个关键词
        self.cookie_manager = CookieManager()
        self.crawler = None

    def check_cookie_status(self):
        """检查Cookie状态"""
        try:
            cookies_dir = 'cookies'
            if not os.path.exists(cookies_dir):
                return "未找到Cookie目录", "#ff0000"

            cookie_files = [f for f in os.listdir(cookies_dir) if f.endswith('.json')]
            if not cookie_files:
                return "未找到Cookie文件", "#ff0000"

            latest_file = max(cookie_files,
                              key=lambda x: os.path.getctime(os.path.join(cookies_dir, x)))
            cookie_time = datetime.fromtimestamp(
                os.path.getctime(os.path.join(cookies_dir, latest_file)))

            return f"Cookie有效 (更新时间: {cookie_time.strftime('%Y-%m-%d %H:%M')})", "#00ff00"

        except Exception as e:
            return f"检查Cookie出错: {str(e)}", "#ff0000"

    def start_login(self):
        """启动登录流程"""
        try:

            # 打开小红书登录页面
            print("正在打开小红书登录页面...")
            webbrowser.get('edge').open('https://www.xiaohongshu.com')
            time.sleep(10)  # 等待浏览器打开

            # 保存 Cookie（确保 cookie_manager 已正确初始化）
            print("正在保存Cookie...")
            if not hasattr(self, 'cookie_manager'):
                raise AttributeError("cookie_manager 未初始化")
            self.cookie_manager.save_cookies()

            # 检查 Cookie 状态
            status, color = self.check_cookie_status()
            print(f"Cookie状态: {status}")

            return f"登录成功! {status}"
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return f"登录失败: {str(e)}"

    def add_keyword(self, keyword):
        """设置关键词"""
        keyword = keyword.strip()
        if not keyword:
            return "", "请输入关键词"
        
        self.keyword = keyword
        return keyword, f"已设置关键词: {keyword}"

    def clear_keyword(self):
        """清空关键词"""
        self.keyword = None
        return "", "已清空关键词"

    def start_crawler(self, notes_count, comments_count, keyword):
        """启动爬虫"""
        try:
            # 检查参数
            if not keyword.strip():
                return "请先添加关键词"
            
            notes_count = int(notes_count)
            comments_count = int(comments_count)
            
            if notes_count <= 0 or comments_count <= 0:
                return "采集数量必须大于0"

            # 创建爬虫实例
            self.crawler = XHSCrawler()
            self.crawler.set_limits(notes_count, comments_count)
            
            # 登录
            if not self.crawler.login():
                return "登录失败，请检查Cookie"
            
            # 开始采集
            print(f"开始采集关键词: {keyword}")
            if self.crawler.search_and_filter(keyword):
                if self.crawler.collect_all_notes():
                    print(f"关键词 {keyword} 采集完成")
                else:
                    print(f"采集关键词 {keyword} 的笔记时出错")
            
            # 完成后关闭浏览器
            self.crawler.close()
            return "采集任务已完成"
            
        except ValueError:
            return "请输入有效的数字"
        except Exception as e:
            if self.crawler:
                self.crawler.close()
            return f"启动采集失败: {str(e)}"

    def visualize_data(self):
        """创建数据可视化界面"""
        try:
            import data_visualization as dv
            
            # 确保可视化目录存在
            os.makedirs('data/visualization', exist_ok=True)
            
            # 获取基础统计信息
            stats = dv.analyze_data('data/user/xhs_comments.csv')
            
            # 生成各类图表
            location_data, location_chart = dv.create_location_chart('data/user/xhs_comments.csv')
            time_chart = dv.create_time_chart('data/user/xhs_comments.csv')
            user_chart = dv.create_user_activity_chart('data/user/xhs_comments.csv')
            
            # 返回四个独立的值，对应四个输出组件
            stats_text = f"总评论数: {stats['total_comments']}\n" \
                        f"独立用户数: {stats['unique_users']}\n" \
                        f"时间范围: {stats['time_range']['start']} 至 {stats['time_range']['end']}"
            
            return [
                stats_text,           # 对应 stats_output
                location_chart,       # 对应 location_chart
                time_chart,          # 对应 time_chart
                user_chart           # 对应 user_chart
            ]
            
        except Exception as e:
            # 发生错误时也要返回四个值
            error_message = f"数据分析失败: {str(e)}"
            return [error_message, None, None, None]

    def create_ui(self):
        """创建Gradio界面"""
        with gr.Blocks(title="小红书数据采集工具", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 小红书数据采集工具")
            
            with gr.Tab("Cookie管理"):
                with gr.Row():
                    login_btn = gr.Button("登录获取Cookie", variant="primary")
                    check_btn = gr.Button("检查Cookie状态")
                cookie_status = gr.Textbox(label="Cookie状态", interactive=False)
                
                login_btn.click(self.start_login, outputs=cookie_status)
                check_btn.click(
                    lambda: self.check_cookie_status()[0], 
                    outputs=cookie_status
                )
            
            with gr.Tab("采集配置"):
                with gr.Row():
                    notes_count = gr.Number(
                        value=20, 
                        label="采集笔记数量", 
                        minimum=1, 
                        maximum=100
                    )
                    comments_count = gr.Number(
                        value=20, 
                        label="每篇笔记采集评论数量", 
                        minimum=1, 
                        maximum=100
                    )
                
                with gr.Row():
                    keyword_input = gr.Textbox(
                        label="输入关键词", 
                        placeholder="请输入要采集的关键词"
                    )
                    add_btn = gr.Button("设置关键词")
                    clear_btn = gr.Button("清空关键词")
                
                keyword_display = gr.Textbox(
                    label="当前关键词", 
                    interactive=False
                )
                
                status_output = gr.Textbox(
                    label="状态信息", 
                    interactive=False
                )
                
                with gr.Row():
                    start_btn = gr.Button("开始采集", variant="primary")
                    stop_btn = gr.Button("停止采集", variant="secondary")
                
                # 绑定事件
                add_btn.click(
                    self.add_keyword,
                    inputs=[keyword_input],
                    outputs=[keyword_display, status_output]
                )
                
                clear_btn.click(
                    self.clear_keyword,
                    outputs=[keyword_display, status_output]
                )
                
                start_btn.click(
                    self.start_crawler,
                    inputs=[notes_count, comments_count, keyword_display],
                    outputs=status_output
                )
                
                stop_btn.click(
                    lambda: "采集已停止",
                    outputs=status_output
                )
            
            # 添加数据可视化标签页
            with gr.Tab("数据可视化"):
                with gr.Row():
                    visualize_btn = gr.Button("生成数据分析报告", variant="primary")
                
                with gr.Row():
                    stats_output = gr.Textbox(
                        label="基础统计信息",
                        interactive=False,
                        lines=4
                    )
                
                with gr.Row():
                    location_chart = gr.Image(
                        label="地区分布",
                        show_label=True
                    )
                    time_chart = gr.Image(
                        label="时间分布",
                        show_label=True
                    )
                
                with gr.Row():
                    user_chart = gr.Image(
                        label="用户活跃度",
                        show_label=True
                    )
                
                # 绑定可视化事件
                visualize_btn.click(
                    self.visualize_data,
                    outputs=[
                        stats_output,
                        location_chart,
                        time_chart,
                        user_chart
                    ]
                )
            
            # 添加使用说明标签
            with gr.Tab("使用说明"):
                gr.Markdown("""
                ## 使用步骤
                1. 首先在"Cookie管理"标签页完成登录并获取Cookie
                2. 在"采集配置"标签页设置采集参数：
                   - 设置要采集的笔记数量
                   - 设置每篇笔记要采集的评论数量
                3. 输入并设置要采集的关键词
                4. 点击"开始采集"启动采集任务
                
                ## 注意事项
                - 请确保Cookie有效再开始采集
                - 采集数量建议不要设置过大
                - 每个Cookie只能采集一个关键词
                - 采集过程中可以随时停止
                """)
        
        return interface

def main():
    crawler_web = XHSCrawlerWeb()
    interface = crawler_web.create_ui()
    interface.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,       # 设置端口
        share=True              # 生成公共链接
    )

if __name__ == "__main__":
    main()