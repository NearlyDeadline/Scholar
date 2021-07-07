import scrapy


class AdvancedquerySpider(scrapy.Spider):
    name = 'AdvancedQuery'
    allowed_domains = ['https://www.webofknowledge.com']
    start_urls = ['http://https://www.webofknowledge.com/']

    def parse(self, response):
        pass
