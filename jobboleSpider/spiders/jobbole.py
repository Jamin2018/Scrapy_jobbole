# -*- coding: utf-8 -*-
import scrapy
import urlparse
from jobboleSpider import items
from jobboleSpider.utils.common import get_md5
import datetime

# 更方便的解析数据
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # １.获取文章列表页中的文章url并交给解析函数进行具体字段的解析
        # 2.获取下一页的URL并交给Scrapy下载


        # １.获取文章列表页中的文章url并交给解析函数进行具体字段的解析
        # contents = response.xpath("//*[contains(@class,'floated-thumb')]")
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")

        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first('')
            post_url = post_node.css('::attr(href)').extract_first('')

            # 这个很重要 urlparse.urljoin(response.url, image_url)  没有域名拼接域名，有域名不作为
            yield scrapy.Request(url=urlparse.urljoin(response.url, post_url),meta={'front_image_url':urlparse.urljoin(response.url, image_url)},callback=self.parse_detail)


        next_page = scrapy.Selector(response).re(u'<a class="next page-numbers" href="(\S*)">下一页 »</a>')
        print next_page
        if next_page:
            yield scrapy.Request(url=next_page[0], callback=self.parse)


    def parse_detail(self, response):
        article_item = items.JobBoleArticleItem()


        # 提取文章的详情页面字段
        front_image_url = response.meta.get('front_image_url','')   # 文章封面图

        title = response.xpath('//*[@class="entry-header"]/h1/text()').extract()[0]
        create_date = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()').extract()[0]
        try:
            praise_num = response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract()[0]
        except:
            praise_num = 0
        try:
            import re
            fav_num = int(re.match(r".*(\d+).*",response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0]).group(1))
        except:
            fav_num = 0
        try:
            import re
            comments_num = int(re.match(r".*(\d+).*",response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]).group(1))
        except:
            comments_num = 0

        content = response.xpath('.//div[@class="entry"]').extract()[0]

        article_item['title'] = title
        try:
            create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()


        article_item['create_date'] = create_date
        article_item['url'] = response.url
        article_item['url_object_id'] = get_md5(response.url)
        article_item['front_image_url'] = [front_image_url]   # 图片保持格式要是数组，后续下载的时候需要数组
        # front_image_path 这个图片路径在管道pipeline中已经保持了
        article_item['praise_num'] = praise_num
        article_item['fav_num'] = fav_num
        article_item['comments_num'] = comments_num
        article_item['content'] = content


        # 通过ItemLoader加载item,后续存进数据库在过滤值也可以。
        item_Loader = ItemLoader(item=items.JobBoleArticleItem(), response=response)
        item_Loader.add_css('title','.entry-header h1::text')
        item_Loader.add_value('url', response.url)
        item_Loader.add_value('url_object_id', get_md5(response.url))
        item_Loader.add_xpath('create_date', '//*[@class="entry-meta-hide-on-mobile"]/text()')
        item_Loader.add_value('front_image_url', [front_image_url])
        item_Loader.add_xpath('praise_num', '//span[contains(@class,"vote-post-up")]/h10/text()')
        item_Loader.add_xpath('fav_num', '//span[contains(@class,"bookmark-btn")]/text()')
        item_Loader.add_xpath('comments_num', '//a[@href="#article-comment"]/span/text()')
        item_Loader.add_xpath('content', './/div[@class="entry"]')
        # item_Loader.add_css()
        # item_Loader.add_xpath()
        # item_Loader.add_value()
        article_item = item_Loader.load_item()

        yield article_item


