# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader
from datetime import datetime
from utils.common import get_nums
from settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


#字符串转日期函数
def date_conver(value):
    try:
        value = value.replace('·','').strip()
        date_time = datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        date_time = datetime(1970,1,1)
    return date_time


#标签处理
class ProcessTag(object):

    def __call__(self, values):
        tag_list = set(values)
        tags = ','.join([tag for tag in set(tag_list) if not '评论' in tag])
        return tags


#返回元输出值，不别默认的outputprocessor影响
def return_value(value):
    return value


#去掉斜杠
def remove_splash(value):
    return value.replace('/','')


class ArticleItemLoader(ItemLoader):
    #自定义itemLoader
    default_output_processor = TakeFirst()


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor = MapCompose(date_conver)
    )
    praise_num = scrapy.Field(
        input_processor = MapCompose(int)
    )
    fav_num = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comment_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    front_img_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )
    front_img_path = scrapy.Field()
    url_object_id = scrapy.Field()
    tag = scrapy.Field(
        output_processor = ProcessTag()
    )
    content = scrapy.Field()
    url = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into jobbole_article (url_object_id,url,title,tag) 
            VALUES (%s,%s,%s,%s)
        '''
        params = (self['url_object_id'], self['url'], self['title'], self['tag'])
        return insert_sql,params


class ZhihuQuestionItem(scrapy.Item):
    #知乎问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time =  scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                    insert into zhihu_question (zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time,crawl_update_time) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content) ,answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num),click_num=VALUES(click_num),crawl_update_time=VALUES(crawl_update_time)
                '''

        zhihu_id = int(self['zhihu_id'][0])
        topics = ','.join(self['topics'])
        url = self['url'][0]
        title = self['title'][0]
        content = self['content'][0]
        answer_num = get_nums(self['answer_num'][0])
        comments_num = get_nums(self['comments_num'][0])
        watch_user_num = get_nums(self['watch_user_num'][0])
        click_num = get_nums(self['watch_user_num'][1])
        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)
        crawl_update_time = datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time,crawl_update_time)
        return insert_sql,params


class ZhihuAnswerItme(scrapy.Item):
    #知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time =  scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                    insert into zhihu_answer (zhihu_id,url,question_id,content,parise_num,comments_num,create_time,update_time,crawl_time,crawl_update_time) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content),parise_num=VALUES(parise_num),comments_num=VALUES(comments_num),update_time=VALUES(update_time),crawl_update_time=VALUES(crawl_update_time)
                '''
        zhihu_id = self['zhihu_id']
        url = self['url']
        question_id = self['question_id']
        content = self['content']
        parise_num = self['parise_num'],
        comments_num = self['comments_num']
        create_time = datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)
        crawl_update_time = datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id,url,question_id,content,parise_num,comments_num,create_time,update_time,crawl_time,crawl_update_time)
        return insert_sql,params

#处理工作地址
def hadle_job_addr(value):
    return value.replace("\n","").replace(' ','').replace('查看地图','')

#处理发布时间
def handle_publish_time(value):
    return value.replace('  发布于拉勾网','')


class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,hadle_job_addr)
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                       insert into lagou_job (title,url,url_object_id,salary,work_years,degree_need,job_type,job_city,publish_time,job_advantage,job_desc,job_addr,company_name,company_url,tags,crawl_time) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   '''

        params = (self['title'],self['url'],self['url_object_id'],self['salary'],self['work_years'],self['degree_need'],self['job_type'],self['job_city'],self['publish_time'],self['job_advantage'],self['job_desc'],self['job_addr'],self['company_name'],self['company_url'],self['tags'],self['crawl_time'])
        return insert_sql, params


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


if __name__ == '__main__':
    pass







