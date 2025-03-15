import pandas as pd
import requests
from datetime import datetime
import os


class DeepSeekProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.system_prompt = """你是一个小红书文案创作专家，精通各类爆款文案创作，熟悉平台规则。你的风格活泼时尚，善于运用emoji和网络热词。请根据要求完成以下任务：
1. 结合标题和内容分析核心亮点
2. 提取标题关键词用于文案创作
3. 生成符合平台调性的文案
4. 列出3条发布注意事项
要求：
- 标题特性需体现在文案中
- 使用口语化中文
- 适当添加相关emoji
- 分点清晰排版"""

    def _call_api(self, user_prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"API调用失败: {str(e)}")
            return None

    def process_data(self, file_path, user_query):
        try:
            # 读取数据（增强兼容性）
            df = pd.read_csv(
                file_path,
                encoding='utf-8-sig',
                sep=',',
                on_bad_lines='warn',
                engine='python'
            ).fillna('')

            # 验证字段存在
            required_columns = ['title', 'content', 'collect_time']
            if not set(required_columns).issubset(df.columns):
                missing = set(required_columns) - set(df.columns)
                raise ValueError(f"CSV文件缺少必要字段: {', '.join(missing)}")

            # 调试：显示实际数据
            print("\n[调试] 前3行原始数据：")
            print(df[['title', 'content', 'collect_time']].head(3))

            # 正确解析日期
            if "月" in user_query and "日" in user_query:
                # 使用正则表达式提取准确日期
                import re
                date_match = re.search(r'(\d{1,2})月(\d{1,2})日', user_query)
                if date_match:
                    target_month = int(date_match.group(1))
                    target_day = int(date_match.group(2))
                    print(f"[调试] 解析到目标日期：{target_month}月{target_day}日")

                    # 构建日期匹配模式（兼容2025/3/15和2025/03/15格式）
                    date_pattern1 = f"{target_month}-{target_day}"
                    date_pattern2 = f"{target_month:02d}/{target_day:02d}"

                    # 过滤数据
                    df = df[df['collect_time'].str.contains(f'({date_pattern1}|{date_pattern2})')]
                    print(f"[调试] 过滤后数据量：{len(df)}条")
                else:
                    print("⚠️ 未检测到有效日期格式，将处理全部数据")

            # 构建样本数据（增强容错）
            def format_sample(row):
                try:
                    title = str(row['title']).strip() or "无标题"
                    content = str(row['content']).strip()[:150] or "无内容"
                    return f"📌 标题：{title}\n📝 内容：{content}..."
                except Exception as e:
                    print(f"⚠️ 数据格式化异常: {str(e)}")
                    return ""

            samples = [s for s in df.head(3).apply(format_sample, axis=1) if s]
            if not samples:
                raise ValueError("没有找到有效数据，可能原因：\n1. 日期过滤无匹配\n2. 数据字段为空\n3. 文件编码错误")

            content_samples = "\n\n".join(samples)

            # 构建提示词
            user_prompt = f"{user_query}\n\n参考数据（标题+内容）：\n{content_samples}"

            # 显示提示词预览
            print("\n" + "=" * 60)
            print("📝 完整提示词预览：")
            print("=" * 60)
            print(f"【用户指令】\n{user_query}\n")
            print(f"【参考数据】\n{content_samples}")
            print("=" * 60 + "\n")

            return self._call_api(user_prompt)

        except Exception as e:
            print(f"数据处理失败: {str(e)}")
            return None


def save_and_show_result(result, output_dir="./data/results"):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"result_{timestamp}.txt")

    # 保存结果
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result)

    # 终端输出
    print("\n" + "=" * 50)
    print("✅ 生成结果已保存至:", os.path.abspath(filename))
    print("=" * 50 + "\n")
    print(result)
    print("\n" + "=" * 50)


# 使用示例
if __name__ == "__main__":
    processor = DeepSeekProcessor(api_key="sk-a5457b7547314c93b76801027067cd49")

    # 执行处理
    result = processor.process_data(
        "./data/notes/xhs_python_notes.csv",
        "分析3月15日的文章内容，总结一下都有哪些主题供我参考，并随机选择一个已获取的标题中的主题生成新的创作内容。要求结合你参考的主题和文案进行语法、思维等方面的重塑，要求比原文更吸引人。"
    )

    # 处理结果
    if result:
        save_and_show_result(result)
    else:
        print("生成失败，请检查错误信息")