# 获取登录cookie


from DrissionPage import WebPage, ChromiumOptions
import time
import json
import os
from datetime import datetime

class CookieManager:
    def __init__(self):
        self.cookies_dir = 'cookies'
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)

    def save_cookies(self):
        """获取并保存cookies"""
        # 创建ChromiumOptions实例，默认为非无头模式
        co = ChromiumOptions()
        
        # 创建WebPage实例，使用配置
        page = WebPage(chromium_options=co)
        
        try:
            # 清除所有cookie
            page.set.cookies.clear()
            
            # 访问小红书
            page.get('https://www.xiaohongshu.com')
            
            # 等待20秒让用户登录并生成所需cookie
            time.sleep(20)
            
            # 获取所有域名的cookie
            cookies = page.cookies(all_domains=True)
            
            # 生成文件名，包含时间戳
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{self.cookies_dir}/cookies_{timestamp}.json'
            
            # 保存cookies到文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            return cookies
        
        finally:
            # 确保浏览器被正确关闭
            page.quit()

    def get_latest_cookies(self):
        """获取最新的cookies"""
        try:
            cookie_files = [f for f in os.listdir(self.cookies_dir) if f.endswith('.json')]
            if not cookie_files:
                return None
            
            latest_file = max(cookie_files, 
                            key=lambda x: os.path.getctime(os.path.join(self.cookies_dir, x)))
            
            with open(os.path.join(self.cookies_dir, latest_file), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"获取cookies失败: {str(e)}")
            return None

# 保留原有的函数作为独立函数
def get_fresh_cookies():
    cookie_manager = CookieManager()
    return cookie_manager.save_cookies()

if __name__ == '__main__':
    cookies = get_fresh_cookies()