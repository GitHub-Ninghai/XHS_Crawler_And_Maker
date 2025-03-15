# 采集工具 gradio前端界面
import gradio as gr
import json
import os
from copy_cookie import CookieManager
from star_xhs import XHSCrawler
import webbrowser
from datetime import datetime
import time
from deepseek import DeepSeekProcessor

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
        self.deepseek_processor = None

    def ai_data_process(self, file_path, model, template, custom_prompt):
        try:
            # 参数验证
            if not file_path:
                return "⚠️ 请先选择数据文件"
            if not os.path.exists(file_path):
                return "⚠️ 文件不存在，请重新选择"

            # 模型初始化
            if model == "DeepSeek":
                if not self.deepseek_processor:
                    # 改为从界面输入获取API密钥
                    api_key = os.getenv("DEEPSEEK_API_KEY")
                    if not api_key:
                        return "⚠️ 请先设置DEEPSEEK_API_KEY环境变量"

                    self.deepseek_processor = DeepSeekProcessor(api_key)

                # 构建提示词（优化模板提示）
                preset_prompts = {
                    "自动生成摘要": "请用简洁的小红书风格总结以下内容，列出3个使用💡emoji标注的核心要点",
                    "评论情感分析": "分析以下评论的情感倾向，使用😊/😐/😟表情进行分类，并给出改进建议",
                    "标题优化建议": "用小红书热门标题风格分析以下标题，提供5个带🔥符号的改进方案",
                    "内容创意改写": "将以下内容改写成3种不同的小红书风格（种草体、测评体、教程体）",
                    "小红书文案生成": self.deepseek_processor.system_prompt  # 直接使用系统预设
                }

                final_prompt = custom_prompt if custom_prompt.strip() else preset_prompts.get(template, "")
                if not final_prompt:
                    return "⚠️ 请选择或输入有效的处理指令"

                # 执行处理并保存结果
                result = self.deepseek_processor.process_data(file_path, final_prompt)

                # 自动保存结果
                if result:
                    output_dir = "E:/projects/xhs_maker/data/results"
                    os.makedirs(output_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(output_dir, f"result_{timestamp}.txt")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(result)
                    return f"✅ 处理成功！结果已保存至：{filename}\n\n{result}"

                return "生成失败，请检查输入数据"
            else:
                return "⚠️ 暂不支持该模型"
        except Exception as e:
            return f"处理失败: {str(e)}"

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
                                value=5,
                                label="📒 采集笔记数量",
                                minimum=1,
                                maximum=100,
                                elem_classes="numeric-input"
                            )
                            comments_count = gr.Number(
                                value=5,
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
                    # 标题区域
                    gr.Markdown("""
                    <div style="padding: 16px 0 8px;">
                        <h3 style="margin: 0; color: #2d3748;">🎨 智能二创功能</h3>
                        <p style="color: #718096; font-size:0.9em">使用大语言模型对采集数据进行智能处理</p>
                    </div>
                    """)

                    with gr.Group():
                        # 输入区域
                        with gr.Row(equal_height=False):
                            # 左侧控制面板
                            with gr.Column(scale=2):
                                # API密钥输入
                                api_key_input = gr.Textbox(
                                    label="🔑 DeepSeek API密钥",
                                    type="password",
                                    placeholder="请输入API密钥",
                                    info="从DeepSeek控制台获取",
                                    interactive=True
                                )

                                # 文件选择
                                file_input = gr.File(
                                    label="📁 选择数据文件",
                                    file_types=[".csv"],
                                    type="filepath",
                                    height=80
                                )

                                # 模型选择
                                model_selector = gr.Dropdown(
                                    label="🛠️ 选择模型",
                                    choices=["GPT-4o", "Claude-3", "ERNIE-4.0", "DeepSeek"],
                                    value="DeepSeek",
                                    interactive=True
                                )

                                # 模板选择标签页
                                with gr.Tabs(selected=0) as template_tabs:
                                    with gr.Tab("📝 预设模板", id="preset"):
                                        template_select = gr.Dropdown(
                                            label="选择处理模板",
                                            choices=[
                                                "自动生成摘要",
                                                "评论情感分析",
                                                "标题优化建议",
                                                "内容创意改写",
                                                "小红书文案生成"
                                            ],
                                            value="小红书文案生成",
                                            interactive=True
                                        )

                                    with gr.Tab("✨ 自定义指令", id="custom"):
                                        custom_prompt = gr.Textbox(
                                            label="输入自定义指令",
                                            placeholder="例：请分析这些笔记的主要内容并生成5个热门话题",
                                            lines=4,
                                            max_lines=8,
                                            show_label=True
                                        )

                            # 右侧输出区域
                            with gr.Column(scale=3):
                                output_area = gr.Textbox(
                                    label="📋 处理结果",
                                    interactive=True,
                                    lines=15,
                                    max_lines=20,
                                    elem_classes="result-box"
                                )
                                with gr.Row():
                                    gr.Button(
                                        "📋 复制结果",
                                        size="sm"
                                    ).click(
                                        lambda x: x,
                                        inputs=output_area
                                    )
                                    gr.Button(
                                        "📂 打开结果目录",
                                        size="sm"
                                    ).click(
                                        lambda: os.startfile("./data/results"),
                                        queue=False
                                    )

                        # 操作按钮
                        with gr.Row(variant="panel"):
                            process_btn = gr.Button(
                                "🚀 开始智能处理",
                                variant="primary",
                                scale=2,
                                size="sm"
                            )
                            stop_ai_btn = gr.Button(
                                "⏹️ 停止处理",
                                variant="secondary",
                                scale=1,
                                size="sm"
                            )

                    # 使用提示
                    gr.Markdown("""
                    <div style="margin:20px 0; padding:15px; background:#f8fafc; border-radius:8px;">
                        <h4 style="margin:0 0 12px 0; color:#2d3748; font-size:0.95em">💡 使用提示：</h4>
                        <ul style="margin:0; color:#4a5568; font-size:0.9em">
                            <li>首次使用需先输入DeepSeek API密钥</li>
                            <li>支持CSV格式的采集数据文件（建议文件小于10MB）</li>
                            <li>自定义指令请使用明确的要求格式，如："请分析...并生成..."</li>
                            <li>处理结果会自动保存在/data/results目录</li>
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
            # 事件绑定
            api_key_input.change(
                lambda x: os.environ.update({"DEEPSEEK_API_KEY": x}),
                inputs=api_key_input,
                queue=False
            )

            process_btn.click(
                lambda: gr.Info("开始处理，请稍候..."),
                queue=False
            ).then(
                self.ai_data_process,
                inputs=[file_input, model_selector, template_select, custom_prompt],
                outputs=output_area
            )

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