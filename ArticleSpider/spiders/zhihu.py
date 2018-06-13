# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
import json
import os
import requests
import re
from urllib import parse
from scrapy.loader import ItemLoader
from items import ZhihuQuestionItem,ZhihuAnswerItme
from settings import USER_AGENT
from tools.zhihu_login import ZhihuLogin

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    header = {
        "User-Agent": USER_AGENT
    }
    #在此spider下面进行自定义设置
    custom_settings = {
        'COOKIES_ENABLED' : True
    }

    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"


    def start_requests(self):
        zhihulogin = ZhihuLogin()
        cookie_dict = zhihulogin.get_cookie()
        return [scrapy.Request(url=self.start_urls[0],headers=self.header,dont_filter=True,cookies=cookie_dict)]

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)

        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, headers=self.header,meta={'question_id':int(question_id)},callback=self.parse_question)
            else:
                pass
                # 如果不是question页面则直接进一步跟踪
                #yield scrapy.Request(url, headers=self.header, callback=self.parse)

    def parse_question(self, response):
        question_id = response.meta.get('question_id')
        item_loader = ItemLoader(item=ZhihuQuestionItem(),response=response)
        item_loader.add_css('title','h1.QuestionHeader-title::text')
        item_loader.add_css('content','.QuestionHeader-detail')
        item_loader.add_value('url',response.url)
        item_loader.add_value('zhihu_id', question_id)
        item_loader.add_css('answer_num','.List-headerText span::text')
        item_loader.add_css('comments_num','.QuestionHeaderActions .QuestionHeader-Comment button::text')
        item_loader.add_css('watch_user_num','.NumberBoard-itemValue::text')
        item_loader.add_css('topics','.QuestionHeader-topics .Popover div::text')
        question_item = item_loader.load_item()
        yield scrapy.Request(url=self.start_answer_url.format(question_id,20,0),headers=self.header,callback=self.parse_answer)
        yield question_item

    def parse_answer(self,response):
        #处理json格式的answer
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        totals = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItme()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author'].get('id')
            answer_item['content'] = answer['content']
            answer_item['parise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            yield answer_item
        if not is_end:
            yield scrapy.Request(url=next_url,headers=self.header,callback=self.parse_answer)



