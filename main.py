# -*- coding:utf-8 -*-

# pycharm启动scrapy，启动debug模式

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy","crawl","jobbole"])