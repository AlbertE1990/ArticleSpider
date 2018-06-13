# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import os
from items import LagouJobItem,LagouJobItemLoader
from utils.common import get_md5
from datetime import datetime
from settings import SQL_DATETIME_FORMAT,USER_AGENT
from tools.lagou_login import LagouLogin


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']
    header = {
        "User-Agent": USER_AGENT
    }

    #在此spider下面进行自定义设置
    custom_settings = {
        'COOKIES_ENABLED': True
    }

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), callback='', follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+/.html'), callback='', follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+\.html'), callback='parse_job', follow=True)
    )



    def start_requests(self):
        lagoulogin = LagouLogin()
        cookie_dict = lagoulogin.get_cookie()
        return [scrapy.Request(url=self.start_urls[0],headers=self.header,dont_filter=True,cookies=cookie_dict)]


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
        print('parse job 函数返回：',job_item)
        return job_item







