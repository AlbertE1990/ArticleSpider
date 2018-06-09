# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time,json,os
from selenium import webdriver


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']
    User_Agent = "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    header = {
        "User-Agent": User_Agent
    }
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies/' + name + '.txt')

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+/.html'), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+\.html'), callback='parse_job', follow=True)
    )

    def get_local_cookie(self):
        '''
        从本地文件获取cookie
        :return:
        '''
        if os.path.isfile(self.cookie_path):
            with open(self.cookie_path,'r') as f :
                cookie_dict = json.load(f)
            return cookie_dict
        else:
            return False

    def update_local_cookie(self,cookie_dict):
        '''
        更新本地cookie
        :param cookie_dict: 获取到的最新cookie_dict
        :return:
        '''
        with open(self.cookie_path,'w') as f:
            json.dump(cookie_dict,f)

    def get_web_cookie(self):
        '''
        登录网址获取cookie
        :return:
        '''
        browser = webdriver.Chrome(executable_path='D:/chromedriver/chromedriver.exe')
        browser.get(url="https://www.lagou.com/")
        time.sleep(3)
        browser.find_element_by_css_selector('#changeCity_header .checkTips a.tab focus').click()
        time.sleep(3)
        Cookies = browser.get_cookies()
        browser.quit()
        with open('zhihu_cookies', 'w') as f:
            f.write(json.dumps(Cookies))
        cookie_dict = {}
        for cookie in Cookies:
            cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict

    def start_requests(self):
        # 从本地文件获取cookie
        cookie_dict = self.get_local_cookie()
        # 检验本地cookie是否能够登录
        if not cookie_dict:
            # 登录不成功重新用账号密码登录获取cookie
            cookie_dict = self.get_web_cookie()
            # 更新本地cookie
            self.update_local_cookie(cookie_dict)
        return [scrapy.Request(url=self.start_urls[0], headers=self.header, dont_filter=True, cookies=cookie_dict)]


    def parse_job(self, response):
        i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
