# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import json
import codecs  # 这个和open函数的区别在于可以避免文件的编码

# 自带的出存储格式,这里导入JSON的
from scrapy.exporters import JsonItemExporter

# 存入mysql
# import MySQLdb
# import MySQLdb.cursor


class JobbolespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 自定义JSON文件导出
    def __init__(self):

        self.file = codecs.open('Article.json','w',encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"  # ensure_ascii=False 存入显示中文
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        # 关闭文件
        self.file.close()


class MysqlPipeline(object):
    # 采用同步的机制，这个当爬取速度过快的时候，数据库存储会堵塞。要换另一种存法
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1','username','password','dbname',charser='utf-8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
            insert into jobbole_article(title,url,fav_num)
            VALUES (%s,%s,%s)
            
        '''
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['fav_num']))
        self.conn.commit()



from twisted.enterprise import adbapi
class MysqlTwistedPipeline(object):
    # 采用异步的机制存入MYSQL，用这个比上面的好
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
                        host = settings['MYSQL_HOST'],
                        db = settings['MYSQL_DBNAME'],
                        user = settings['MYSQL_USER'],
                        passwd = settings['MYSQL_PASSWORD'],
                        charset = 'utf-8',
                        cursorclass = MySQLdb.cursors.DictCursor,
                        use_unicode = True,
                    )

        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)


    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print failure


    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = '''
            insert into jobbole_article(title,url,fav_num)
            VALUES (%s,%s,%s)

        '''
        cursor.execute(insert_sql, (item['title'], item['url'], item['fav_num']))




# 自带的出存储格式,这里导入JSON的
from scrapy.exporters import JsonItemExporter
class JsonExportersPipeline(object):
    # 调用Scrapy 提供的json export 导出json文件
    def __init__(self):
        self.file = open('article_exporters.json','wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item






class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_path' in item:
            for ok,value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item