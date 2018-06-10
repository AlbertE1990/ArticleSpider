# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse
from items import JobboleArticleItem,ArticleItemLoader
from utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_nodes = response.css("#archive .post-thumb a")

        for post_node in post_nodes:
            img_url = post_node.css("img::attr(src)").extract_first('')
            post_url = post_node.css("::attr(href)").extract_first('')
            post_url = parse.urljoin(response.url,post_url)
            yield Request(url=post_url,meta={"front_img_url":img_url},callback=self.parse_detail)

        next_url = response.css(".next.page-numbers::attr(href)").extract_first('')
        if next_url:
            next_url = parse.urljoin(response.url,next_url)
            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        article_item = JobboleArticleItem()

        # title = response.css('div.entry-header > h1::text').extract_first()
        # create_date = response.css('.entry-meta-hide-on-mobile::text').extract_first().replace('·','').strip()
        # praise_num = response.css('.post-adds .vote-post-up h10::text').extract_first(0)
        front_img_url = response.meta.get('front_img_url','')
        #
        # fav_num_info = response.css('.post-adds .bookmark-btn::text').extract_first()
        # fav_num_re = re.match(".*(\d+).*", fav_num_info)
        # if fav_num_re:
        #     fav_num = fav_num_re.group(1)
        # else:
        #     fav_num = 0
        # comment_num_info = response.css('a[href="#article-comment"] span::text').extract_first()
        # comment_num_re = re.findall("\d+",comment_num_info)
        # if comment_num_re:
        #     comment_num = comment_num_re[0]
        # else:
        #     comment_num = 0
        #
        # tag_list = response.css('.entry-meta .entry-meta-hide-on-mobile a::text').extract()
        # tags = ','.join([tag for tag in set(tag_list) if not tag.strip().endswith('评论')])
        # content = response.css('.entry').extract_first()
        #
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['url'] = response.url
        # article_item['title'] = title
        # try:
        #     create_date = datetime.strptime(create_date,'%Y/%m/%d').date()
        # except Exception as e:
        #     create_date = datetime.now()
        # article_item['create_date'] = create_date
        # article_item['praise_num'] = praise_num
        # article_item['fav_num'] = fav_num
        # article_item['comment_num'] = comment_num
        # article_item['front_img_url'] = [front_img_url]
        # article_item['tags'] = tags
        # article_item['content'] = content

        #通过item loader价值item
        item_loader = ArticleItemLoader(item=JobboleArticleItem(),response=response)
        item_loader.add_css('title','div.entry-header > h1::text')
        item_loader.add_css('create_date','.entry-meta-hide-on-mobile::text')
        item_loader.add_css('praise_num','.post-adds .vote-post-up h10::text')
        item_loader.add_css('fav_num','.post-adds .bookmark-btn::text')#re
        item_loader.add_css('comment_num','a[href="#article-comment"] span::text')#re
        item_loader.add_css('tag','.entry-meta .entry-meta-hide-on-mobile a::text')#处理函数
        item_loader.add_css('content','.entry')
        item_loader.add_value('front_img_url',[front_img_url])
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id',get_md5(response.url))

        article_item = item_loader.load_item()

        yield article_item
