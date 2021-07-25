# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 15:09
# @Author  : Mike
# @File    : get_rank_json
from web_of_science_crawler.main import AdvancedQuerySpiderRunner
import DBLParser
import XLSParser
import Achievement


def main():
    dblp_raw_file = '../test/北京交通大学_article.csv'
    d = DBLParser(dblp_raw_file)

    wos_input_file = '../test/北京交通大学_article.txt'
    d.save_for_spider(wos_input_file)
    xls_dir = '../test/xls'
    error_log_path = wos_input_file + '.log'
    AdvancedQuerySpiderRunner(wos_input_file, xls_dir, output_format='saveToExcel', error_log_path=error_log_path)
    x = XLSParser(xls_dir, d.author_name)

    a = Achievement()
    a.dblp(d)
    a.wos(x)
    rank_json = a.get_rank_json()

    achi_csv_path = '../test/contrib/' + d.author_name + '.csv'
    a.save_as_csv(achi_csv_path)
