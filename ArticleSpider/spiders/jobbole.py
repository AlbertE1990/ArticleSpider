# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_urls = response.css("#archive .post-thumb a::attr(href)").extract()
        for post_url in post_urls:
            post_url = parse.urljoin(response.url,post_url)
            yield Request(url=post_url,callback=self.parse_detail)

        next_url = response.css(".next.page-numbers::attr(href)").extract_first('')
        if next_url:
            next_url = parse.urljoin(response.url,)
            yield Request(url=next_url, callback=self.parse)


    def parse_detail(self, response):
        title = response.xpath('//*[@id="post-89137"]/div[1]/h1/text()').extract()[0]
        create_date = response.xpath('//*[@id="post-89137"]/div[2]/p/text()').extract()[0].replace('·','').strip()
        praise_num = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        fav_num = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        match_re = re.match(".*(\d+).*",fav_num)
        if match_re:
            fav_num = match_re.group(1)
        comment_num =response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        match_re = re.match(".*(\d+).*", comment_num)
        if match_re:
            comment_num = match_re.group(1)
        pass

