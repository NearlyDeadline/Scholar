# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 14:55
# @Author  : Mike
# @File    : main
from scrapy import cmdline


class AdvancedQuerySpiderRunner:
    def __init__(self, query_path: str, output_dir, document_type="", output_format='fieldtagged',
                 error_log_path: str = 'error.log'):
        self.crawl(query_path, output_dir, document_type, output_format, error_log_path)

    @staticmethod
    def crawl(query_path: str, output_dir, document_type="", output_format='fieldtagged',
              error_log_path: str = 'error.log'):
        cmdline.execute(
            r'scrapy crawl AdvancedQuery -a output_dir={} -a output_format={}'.format(
                output_dir, output_format).split() +
            ['-a', 'query_path={}'.format(query_path),
             '-a', 'document_type={}'.format(document_type),
             '-a', 'error_log_path={}'.format(error_log_path)])
