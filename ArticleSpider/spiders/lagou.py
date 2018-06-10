# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time,json,os
from selenium import webdriver
from items import LagouJobItem,LagouJobItemLoader
from utils.common import get_md5
from datetime import datetime
from settings import SQL_DATETIME_FORMAT


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
        Rule(LinkExtractor(allow=r'gongsi/j\d+/.html'), callback='', follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+\.html'), callback='', follow=True)
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
        qg = browser.find_element_by_css_selector('#changeCityBox > p.checkTips > a')
        print(qg)
        browser.find_element_by_css_selector('#changeCityBox > p.checkTips > a').click()
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
        return [scrapy.Request(url=self.start_urls[0],headers=self.header,dont_filter=True, cookies=cookie_dict)]


    def parse_job(self, response):
        item_loader = LagouJobItemLoader(item = LagouJobItem(),response=response)

        item_loader.add_css('title','.job-name::attr("title")')
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('salary', '.job_request .salary::text')
        item_loader.add_css('job_city', '.job_request > p:nth-child(1) > span:nth-child(2)::text')
        item_loader.add_css('work_years', '.job_request > p:nth-child(1) > span:nth-child(3)::text')
        item_loader.add_css('degree_need', '.job_request > p:nth-child(1) > span:nth-child(4)::text')
        item_loader.add_css('job_type', '.job_request > p:nth-child(1) > span:nth-child(5)::text')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('tags', '.position-label .labels::text')
        item_loader.add_css('job_advantage', '.job-advantage p::text')
        item_loader.add_css('job_desc', '.job_bt div')
        item_loader.add_css('job_addr', '.work_addr')
        item_loader.add_css('company_name', '.b2::attr("alt")')
        item_loader.add_css('company_url', '#job_company dt a::attr("href")')
        item_loader.add_value('crawl_time', datetime.now().strftime(SQL_DATETIME_FORMAT))
        job_item = item_loader.load_item()
        return job_item







