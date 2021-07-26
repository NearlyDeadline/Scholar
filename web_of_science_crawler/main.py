# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 14:55
# @Author  : Mike
# @File    : main
from scrapy import cmdline


class AdvancedQuerySpiderRunner:
    def __init__(self, query_path: str, output_dir, document_type="", output_format='fieldtagged',
                 error_log_path: str = 'error.log'):
        self.crawl(query_path, output_dir, document_type, output_format, error_log_path)

    def crawl(self, query_path: str, output_dir, document_type="", output_format='fieldtagged',
              error_log_path: str = 'error.log'):
        cmdline.execute(
            r'scrapy crawl AdvancedQuery -a output_dir={} -a output_format={}'.format(
                output_dir, output_format).split() +
            ['-a', 'query_path={}'.format(query_path),
             '-a', 'document_type={}'.format(document_type),
             '-a', 'error_log_path={}'.format(error_log_path)])


if __name__ == '__main__':
    import os
    a = os.getcwd()

    wos_input_file = '../test/北京交通大学/北京交通大学_BaopengZhang/wos_input.txt'
    xls_dir = '../test/北京交通大学/北京交通大学_BaopengZhang/xls'
    error_log_path = wos_input_file + '.log'
    AdvancedQuerySpiderRunner(wos_input_file, xls_dir, output_format='saveToExcel', error_log_path=error_log_path)
