# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
import json
import os
import requests
import re
from urllib import parse
from scrapy.item import Item
from scrapy.loader import ItemLoader
from items import ZhihuQuestionItem,ZhihuAnswerItme

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    User_Agent = "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    header = {
        "User-Agent": User_Agent
    }
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies/'+name+'.txt')
    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"


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
        browser.get(url="https://www.zhihu.com/signin")
        time.sleep(3)
        browser.find_element_by_css_selector('.SignFlow-accountInput input').send_keys('')
        time.sleep(1)
        browser.find_element_by_css_selector('.SignFlow-password input').send_keys('')
        time.sleep(1)
        browser.find_element_by_css_selector('.SignFlow-submitButton ').click()
        time.sleep(1)
        Cookies = browser.get_cookies()
        with open('zhihu_cookies', 'w') as f:
            f.write(json.dumps(Cookies))
        cookie_dict = {}
        for cookie in Cookies:
            cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict

    #检查是否登录成功
    # def is_login(self,):
    #     url = 'https://www.zhihu.com/inbox'
    #     cookie_dict = self.get_local_cookie()
    #     # respons = scrapy.Request(url=self.start_urls[0],headers=self.header,dont_filter=True,cookies=cookie_dict)
    #     res = requests.get(url=url,headers=self.header,cookies=cookie_dict,allow_redirects=False)
    #     if res.status_code == 200:
    #         return True

    #检查本地cookie是否有用#
    #检查本地cookie是否有用

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

    def start_requests(self):
        #从本地文件获取cookie
        cookie_dict = self.get_local_cookie()
        #检验本地cookie是否能够登录
        if not self.check_local_cookie():
            #登录不成功重新用账号密码登录获取cookie
            cookie_dict = self.get_web_cookie()
            #更新本地cookie
            self.update_local_cookie(cookie_dict)
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



