from selenium import  webdriver
import os
import time
import json
from settings import CHROMEDRIVER_PATH,USER_AGENT
import requests


class ZhihuLogin(object):

    cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies/' +  'zhihu.txt')
    header = {
        "User-Agent": USER_AGENT
    }

    def get_local_cookie(self):
        '''
        从本地文件获取cookie
        :return:
        '''
        if os.path.isfile(self.cookie_path):
            with open(self.cookie_path, 'r') as f:
                cookie_dict = json.load(f)
            return cookie_dict
        else:
            return False

    def update_local_cookie(self, cookie_dict):
        '''
        更新本地cookie
        :param cookie_dict: 获取到的最新cookie_dict
        :return:
        '''
        with open(self.cookie_path, 'w') as f:
            json.dump(cookie_dict, f)

    def get_web_cookie(self):
        '''
        登录网址获取cookie
        :return:
        '''
        chrome_options = webdriver.ChromeOptions()
        # 启用无界面模式
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=chrome_options)
        browser.get(url="https://www.zhihu.com/signin")
        time.sleep(3)
        browser.find_element_by_css_selector('.SignFlow-accountInput input').send_keys('')
        time.sleep(1)
        browser.find_element_by_css_selector('.SignFlow-password input').send_keys('')
        time.sleep(1)
        browser.find_element_by_css_selector('.SignFlow-submitButton ').click()
        time.sleep(1)
        Cookies = browser.get_cookies()
        cookie_dict = {}
        for cookie in Cookies:
            cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict

    def check_local_cookie(self):
        '''
        检查本地cookie是否有用
        :return:
        '''
        url = 'https://www.zhihu.com/inbox'
        cookie_dict = self.get_local_cookie()
        if not cookie_dict:
            return False
        # respons = scrapy.Request(url=self.start_urls[0],headers=self.header,dont_filter=True,cookies=cookie_dict)
        res = requests.get(url=url, headers=self.header, cookies=cookie_dict, allow_redirects=False)
        print(res.status_code)
        if res.status_code == 200:
            return True

    def get_cookie(self):
        # 检验本地cookie是否能够登录
        if not self.check_local_cookie():
            # 登录不成功重新用账号密码登录获取cookie
            cookie_dict = self.get_web_cookie()
            # 更新本地cookie
            self.update_local_cookie(cookie_dict)
            return cookie_dict
        else:
            return self.get_local_cookie()
