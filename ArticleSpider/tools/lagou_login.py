import time
from selenium import webdriver
import json
import os
from settings import CHROMEDRIVER_PATH

class LagouLogin(object):

    cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies/' + 'lagou.txt')

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
        browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
        browser.get(url="https://www.lagou.com/")
        time.sleep(3)
        qg = browser.find_element_by_css_selector('#changeCityBox > p.checkTips > a')
        print('用chormedrive选择了全国站')
        browser.find_element_by_css_selector('#changeCityBox > p.checkTips > a').click()
        time.sleep(3)
        Cookies = browser.get_cookies()
        browser.quit()
        cookie_dict = {}
        for cookie in Cookies:
            cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict

    def get_cookie(self):
        cookie_dict = self.get_local_cookie()
        if cookie_dict:
            return cookie_dict
        else:
            cookie_dict = self.get_web_cookie()
            self.update_local_cookie(cookie_dict)
            return cookie_dict

if __name__ == '__main__':
    lagou = LagouLogin()
    cookie = lagou.get_cookie()
    print(cookie)