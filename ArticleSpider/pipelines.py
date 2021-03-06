# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')
    def process_item(self,item,spider):
        #ensure_ascii=False 保证
        lines = json.dumps(dict(item),ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item
    def spider_closed(self,spider):
        self.file.close()


class JsonExporterPipeline(object):
    # 调scrapy提供的json export 导出JSON文件
    def __init__(self):
        self.file = open('articleexport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1','root','root','article_spider',charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self,item,spider):
        insert_sql = '''
            insert into jobbole_article (url_object_id,url,title,tag) 
            VALUES (%s,%s,%s,%s)
        '''
        self.cursor.execute(insert_sql,(item['url_object_id'],item['url'],item['title'],item['tag']))
        self.conn.commit()

    def spider_closed(self,spider):
        self.conn.close()


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(item['url'])
        print(failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()

        cursor.execute(insert_sql, params)


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_img_url' in item:
            for ok , value in results:
                image_file_path = value['path']
                item['front_img_path'] = image_file_path
            return item
