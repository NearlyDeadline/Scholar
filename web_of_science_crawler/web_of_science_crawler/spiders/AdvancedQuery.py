# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 10:43
# @Author  : Mike
# @File    : AdvancedQuery.py
import scrapy


class AdvancedQuerySpider(scrapy.Spider):
    name = 'AdvancedQuery'
    allowed_domains = ['https://www.webofknowledge.com']
    start_urls = ['http://https://www.webofknowledge.com/']

    def parse(self, response):
        pass