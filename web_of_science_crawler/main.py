# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 14:55
# @Author  : Mike
# @File    : main
from scrapy import cmdline


def crawl(query_file_path: str, output_dir, document_type="", output_format='fieldtagged'):
    cmdline.execute(
        r'scrapy crawl AdvancedQuery -a output_dir={} -a output_format={}'.format(
            output_dir, output_format).split() +
        ['-a', 'query_file_path={}'.format(query_file_path), '-a', 'document_type={}'.format(document_type)])

# 如果想在其他文件中调用爬虫，将本文件内容复制过去就可以
if __name__ == '__main__':
    crawl(query_file_path="E:/PythonProjects/PaperCrawler/test/errortest.txt",
          output_dir='E:/PythonProjects/PaperCrawler/test/output'
          , output_format='saveToExcel'
          )
