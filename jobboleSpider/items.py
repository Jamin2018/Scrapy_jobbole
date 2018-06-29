# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 传入的值进一步处理
from scrapy.loader.processors import MapCompose, TakeFirst

import datetime


class JobbolespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 传入的值进一步处理
def add_jobbole(value):
    return value + '-jobbole'


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return value


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor = MapCompose(lambda x:x+'-jamin',add_jobbole),  # 传入的值进一步处理,可以多次处理
        output_processor = TakeFirst()   # 默认值的列表，设置这个只取第一个,可以统一设置，不需要每个字段都设置，这里没搞
    )

    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)  # 传入的值进一步处理,可以多次处理
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_num = scrapy.Field()
    fav_num= scrapy.Field()
    comments_num= scrapy.Field()
    content= scrapy.Field()