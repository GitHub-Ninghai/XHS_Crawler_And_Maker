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

    def create_ui(self):
        """创建小红书风格Gradio界面"""
        custom_theme = gr.themes.Default(
            primary_hue="pink",
            secondary_hue="rose",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Poppins"), "Arial", "sans-serif"]
        ).set(
            button_primary_background_fill="linear-gradient(90deg, #ff385c 0%, #ff5483 100%)",
            button_primary_text_color="#ffffff",
        )

        with gr.Blocks(title="🍠 小红书数据精灵", theme=custom_theme) as interface:
            gr.Markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="color: #ff385c; font-size: 2.5em; margin: 0;">
                    🍠 小红书数据精灵
                </h1>
                <p style="color: #666; margin-top: 8px;">
                    ✨ 你的智能采集小助手 | 安全稳定 | 简单易用 ✨
                </p>
            </div>
            """)

            with gr.Tabs(selected="tab_config"):
                with gr.Tab("🔑 Cookie管理", id="tab_cookie"):
                    with gr.Group():
                        gr.Markdown("""
                        <div style="padding: 16px 0;">
                            <h3 style="margin: 0 0 12px 0;">📌 操作指南：</h3>
                            <ol style="color: #666; margin: 0;">
                                <li>点击下方登录按钮自动打开浏览器</li>
                                <li>完成小红书账号登录</li>
                                <li>返回本程序查看Cookie状态</li>
                            </ol>
                        </div>
                        """)

                        with gr.Row():
                            login_btn = gr.Button(
                                "🚀 一键登录获取Cookie",
                                variant="primary",
                                scale=2
                            )
                            check_btn = gr.Button(
                                "🔄 立即检查状态",
                                variant="secondary"
                            )

                        cookie_status = gr.Textbox(
                            label="🔍 当前Cookie状态",
                            interactive=False,
                            elem_classes="status-box"
                        )

                    login_btn.click(self.start_login, outputs=cookie_status)
                    check_btn.click(
                        lambda: self.check_cookie_status()[0],
                        outputs=cookie_status
                    )

                with gr.Tab("⚙️ 采集配置", id="tab_config"):
                    with gr.Group():
                        gr.Markdown("""
                        <div style="padding: 16px 0;">
                            <h3 style="margin: 0 0 12px 0;">🎯 采集目标设置：</h3>
                        </div>
                        """)

                        with gr.Row():
                            notes_count = gr.Number(
                                value=20,
                                label="📒 采集笔记数量",
                                minimum=1,
                                maximum=100,
                                elem_classes="numeric-input"
                            )
                            comments_count = gr.Number(
                                value=20,
                                label="💬 每篇评论数量",
                                minimum=1,
                                maximum=100,
                                elem_classes="numeric-input"
                            )

                    with gr.Group():
                        with gr.Row():
                            keyword_input = gr.Textbox(
                                label="🔎 输入关键词",
                                placeholder="请输入要采集的关键词...",
                                scale=4
                            )
                            with gr.Column(scale=1):
                                add_btn = gr.Button("✅ 确认设置", size="sm")
                                clear_btn = gr.Button("🧹 清空关键词", size="sm")

                        keyword_display = gr.Textbox(
                            label="📌 当前关键词",
                            interactive=False,
                            elem_classes="highlight-box"
                        )

                    with gr.Group():
                        status_output = gr.Textbox(
                            label="📢 系统消息",
                            interactive=False,
                            elem_classes="status-box"
                        )

                        with gr.Row():
                            start_btn = gr.Button(
                                "🚀 开始采集",
                                variant="primary",
                                scale=2
                            )
                            stop_btn = gr.Button(
                                "⏹️ 紧急停止",
                                variant="secondary",
                                scale=1
                            )

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
                        lambda: "🛑 采集已停止！",
                        outputs=status_output
                    )

                with gr.Tab("🤖 AI数据二创", id="tab_ai"):
                    with gr.Group():
                        gr.Markdown("""
                        <div style="padding: 16px 0;">
                            <h3 style="margin: 0 0 12px 0;">🎨 智能二创功能</h3>
                            <p style="color: #666;">使用大语言模型对采集数据进行智能处理</p>
                        </div>
                        """)

                        with gr.Row():
                            with gr.Column(scale=2):
                                file_input = gr.File(
                                    label="📁 选择数据文件",
                                    file_types=[".json"],
                                    type="filepath"
                                )
                                model_selector = gr.Dropdown(
                                    label="🛠️ 选择模型",
                                    choices=["GPT-4o", "Claude-3", "ERNIE-4.0"],
                                    value="GPT-4o"
                                )

                            with gr.Column(scale=3):
                                with gr.Tabs():
                                    with gr.Tab("📝 预设模板"):
                                        template_select = gr.Dropdown(
                                            label="选择处理模板",
                                            choices=[
                                                "自动生成摘要",
                                                "评论情感分析",
                                                "标题优化建议",
                                                "内容创意改写"
                                            ],
                                            interactive=True
                                        )
                                    with gr.Tab("✨ 自定义指令"):
                                        custom_prompt = gr.Textbox(
                                            label="输入自定义指令",
                                            placeholder="例：请分析这些笔记的主要内容并生成5个热门话题",
                                            lines=4,
                                            max_lines=8
                                        )

                        with gr.Row():
                            process_btn = gr.Button(
                                "🚀 开始智能处理",
                                variant="primary",
                                scale=2
                            )
                            stop_ai_btn = gr.Button(
                                "⏹️ 停止处理",
                                variant="secondary",
                                scale=1
                            )

                        with gr.Row():
                            output_area = gr.Textbox(
                                label="📋 处理结果",
                                interactive=True,
                                lines=8,
                                max_lines=15,
                                elem_classes="result-box"
                            )

                        gr.Markdown("""
                        <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <h4 style="margin: 0 0 10px 0;">💡 使用提示：</h4>
                            <ul style="margin: 0; color: #666;">
                                <li>支持JSON格式的采集数据文件</li>
                                <li>首次使用建议先尝试预设模板</li>
                                <li>自定义指令请使用明确的要求格式</li>
                            </ul>
                        </div>
                        """)

                with gr.Tab("📚 使用指南", id="tab_help"):
                    gr.Markdown("""
                    <div style="padding: 20px; background: #fff5f7; border-radius: 12px;">
                        <h2 style="color: #ff385c;">🌸 使用小贴士</h2>

                        <div style="margin: 16px 0; padding: 16px; background: white; border-radius: 8px;">
                            <h3>📌 准备阶段</h3>
                            <ol>
                                <li>点击 <span style="color: #ff385c;">🔑 Cookie管理</span> 完成登录</li>
                                <li>确保状态显示 <span style="color: #00c853;">✅ Cookie有效</span></li>
                            </ol>
                        </div>

                        <div style="margin: 16px 0; padding: 16px; background: white; border-radius: 8px;">
                            <h3>⚙️ 配置阶段</h3>
                            <ul>
                                <li>📝 设置合理的采集数量（建议初次使用不超过20）</li>
                                <li>🔍 关键词建议使用精准搜索词</li>
                                <li>🧹 更换关键词前记得先清空当前设置</li>
                            </ul>
                        </div>
                    </div>
                    """)

            interface.css = """
            .status-box {
                background: #fff5f7 !important;
                border: 2px solid #ffdce4 !important;
                border-radius: 10px !important;
                padding: 16px !important;
            }
            .highlight-box {
                background: #fff0f3 !important;
                border: 2px dashed #ff385c !important;
            }
            .numeric-input input {
                font-weight: 600 !important;
                color: #ff385c !important;
            }
            .result-box {
                background: #f8f9fa !important;
                border: 2px solid #e0e0e0 !important;
                border-radius: 12px !important;
                padding: 20px !important;
                margin-top: 15px;
            }
            .dark .result-box {
                background: #2d2d2d !important;
                border-color: #404040 !important;
            }
            .template-tab {
                border-bottom: 2px solid #ff385c !important;
            }
            button#🚀_一键登录获取Cookie {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }
            """

            return interface


def main():
    crawler_web = XHSCrawlerWeb()
    interface = crawler_web.create_ui()
    interface.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,  # 设置端口
        share=True  # 生成公共链接
    )


if __name__ == "__main__":
    main()