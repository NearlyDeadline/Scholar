# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 14:55
# @Author  : Mike
# @File    : main
from scrapy import cmdline


def crawl(query_path: str, output_dir, document_type="", output_format='fieldtagged',
          error_log_path: str = 'error.log'):
    cmdline.execute(
        r'scrapy crawl AdvancedQuery -a output_dir={} -a output_format={}'.format(
            output_dir, output_format).split() +
        ['-a', 'query_path={}'.format(query_path),
         '-a', 'document_type={}'.format(document_type),
         '-a', 'error_log_path={}'.format(error_log_path)])


# 如果想在其他文件中调用爬虫，将本文件内容复制过去就可以
if __name__ == '__main__':
    crawl(query_path="E:/PythonProjects/PaperCrawler/test/errortest.txt",
          output_dir='E:/PythonProjects/PaperCrawler/test/output',
          output_format='saveToExcel'
          )
