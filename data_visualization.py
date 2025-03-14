# 评论数据可视化分析模块


import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
import seaborn as sns

def extract_location(text):
    """提取评论中的地区信息"""
    # 匹配格式如"02-24山东"或"2024-11-17"中的地区名称
    location_pattern = r'(?:\d{2}-\d{2}|[\d-]+)([^\d,]+)$'
    match = re.search(location_pattern, str(text))
    if match and match.group(1).strip():
        location = match.group(1).strip()
        # 过滤掉非地区信息
        if len(location) <= 4 and not any(char in location for char in ',.。，'):
            return location
    return None

def analyze_data(csv_file):
    """分析评论数据"""
    df = pd.read_csv(csv_file)
    
    # 转换时间格式
    df['comment_time'] = pd.to_datetime(df['comment_time'], format='%Y-%m-%d', errors='coerce')
    
    results = {
        'total_comments': len(df),
        'unique_users': df['user_id'].nunique(),
        'time_range': {
            'start': df['comment_time'].min().strftime('%Y-%m-%d'),
            'end': df['comment_time'].max().strftime('%Y-%m-%d')
        }
    }
    
    return results

def create_location_chart(csv_file):
    """创建地区分布饼图"""
    df = pd.read_csv(csv_file)
    
    # 从评论文本和时间中提取地区信息
    locations = []
    for idx, row in df.iterrows():
        # 先从评论文本中查找
        loc = extract_location(row['comment_text'])
        if not loc:
            # 如果评论文本中没有，尝试从comment_time中查找
            loc = extract_location(row['comment_time'])
        if loc:
            locations.append(loc)
    
    if not locations:
        return "未找到地区信息", None
        
    # 统计地区分布
    location_counts = pd.Series(locations).value_counts()
    location_percentages = location_counts / len(locations) * 100
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False     # 用来正常显示负号
    
    # 创建饼图
    plt.figure(figsize=(12, 8))
    patches, texts, autotexts = plt.pie(
        location_percentages, 
        labels=location_percentages.index,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        wedgeprops=dict(width=0.5)  # 设置环形图的宽度
    )
    
    # 设置标签文字大小
    plt.setp(autotexts, size=8, weight="bold")
    plt.setp(texts, size=10)
    
    # 添加标题
    plt.title('评论地区分布', pad=20, size=14, weight='bold')
    
    # 添加图例
    plt.legend(
        patches,
        location_percentages.index,
        title="地区",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    chart_path = 'data/visualization/location_distribution.png'
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return location_percentages.to_dict(), chart_path

def create_time_chart(csv_file):
    """创建评论时间分布图"""
    df = pd.read_csv(csv_file)
    df['comment_time'] = pd.to_datetime(df['comment_time'], format='%Y-%m-%d', errors='coerce')
    
    plt.figure(figsize=(12, 6))
    df['comment_time'].value_counts().sort_index().plot(kind='line')
    plt.title('评论时间分布')
    plt.xlabel('日期')
    plt.ylabel('评论数量')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    chart_path = 'data/visualization/time_distribution.png'
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path

def create_user_activity_chart(csv_file):
    """创建用户活跃度图表"""
    df = pd.read_csv(csv_file)
    user_activity = df['user_id'].value_counts()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=user_activity.head(10).index, y=user_activity.head(10).values)
    plt.title('Top 10 活跃用户')
    plt.xlabel('用户ID')
    plt.ylabel('评论数量')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    chart_path = 'data/visualization/user_activity.png'
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path

if __name__ == "__main__":
    # 确保输出目录存在
    import os
    os.makedirs('data/visualization', exist_ok=True)
    
    # 分析数据
    result = analyze_data('data/user/xhs_comments.csv')
    if result is not None:
        print("\n数据分析结果:")
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")

    # 创建地区分布图
    location_percentages, chart_path = create_location_chart('data/user/xhs_comments.csv')
    if location_percentages:
        print("\n地区分布统计:")
        for location, percentage in location_percentages.items():
            print(f"{location}: {percentage:.1f}%")

    # 创建评论时间分布图
    time_chart_path = create_time_chart('data/user/xhs_comments.csv')
    if time_chart_path:
        print("\n评论时间分布:")
        print(f"时间范围: {time_chart_path}")

    # 创建用户活跃度图表
    user_activity_chart_path = create_user_activity_chart('data/user/xhs_comments.csv')
    if user_activity_chart_path:
        print("\n用户活跃度:")
        print(f"活跃度图表保存路径: {user_activity_chart_path}") 