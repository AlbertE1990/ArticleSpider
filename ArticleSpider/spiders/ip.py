# -*- coding: utf-8 -*-
import scrapy


class IpSpider(scrapy.Spider):
    name = 'ip'
    allowed_domains = ['www.baidu.com']
    start_urls = ['https://www.baidu.com']

    def parse(self, response):

        print(response)
        pass
