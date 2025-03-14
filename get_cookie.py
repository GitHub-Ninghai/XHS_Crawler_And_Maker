# 获取登录cookie实例


from DrissionPage import SessionPage

page = SessionPage()
page.get('https://www.xiaohongshu.com')

for i in page.cookies(all_domains=True):
    print(i)