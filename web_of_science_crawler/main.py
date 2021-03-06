# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 14:55
# @Author  : Mike
# @File    : main
import argparse
from scrapy import cmdline
import json
import os
import glob
from rank.achievement import Achievement
from rank.dblparser import DBLParser
from rank.xlsparser import XLSParser


def main(args):
    university_dir = args.university_dir
    log_path = args.log_path
    article_pattern = '*_article.csv'

    for university in os.listdir(university_dir):
        print(f"开始爬取{university}的作者")
        for dblp_raw_dir in os.listdir(
                university_dir + '/' + university):
            dblp_raw_dir = university_dir + '/' + university + '/' + dblp_raw_dir
            dblp_raw_file_list = glob.glob(dblp_raw_dir + '/' + article_pattern)
            if dblp_raw_file_list:
                dblp_raw_file = dblp_raw_file_list[0]
            else:
                print(f"未在{dblp_raw_dir}文件夹内发现csv文件")
                continue

            d = DBLParser(dblp_raw_file)
            wos_input_file = dblp_raw_dir + '/wos_input.txt'
            d.save_for_spider(wos_input_file)

            xls_dir = dblp_raw_dir + '/xls'
            if os.path.exists(xls_dir):
                print(f"已存在{xls_dir}文件夹")
            else:
                os.mkdir(xls_dir)

            AdvancedQuerySpiderRunner(wos_input_file, xls_dir, output_format='saveToExcel', error_log_path=log_path + '/error.log')
            x = XLSParser(xls_dir, d.author_name)

            a = Achievement()
            a.load_dblp(d)
            a.load_wos(x)

            rank_json = a.get_rank_json()
            with open(log_path + d.author_name + '_achievement.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(rank_json, indent=4, ensure_ascii=False))


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
    ap = argparse.ArgumentParser(usage='-i: University Directory; -o: Output Directory')
    ap.add_argument('-i', '--input', help='University Directory', dest='university_dir', required=True)
    ap.add_argument('-o', '--output', help='Output Directory', dest='log_path', required=True)
    args = ap.parse_args()
    main(args)
