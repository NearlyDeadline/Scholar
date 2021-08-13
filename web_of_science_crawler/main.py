# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 14:55
# @Author  : Mike
# @File    : main
import argparse
import glob
import os
from rank.dblparser import DBLParser
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
import logging

configure_logging()
runner = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def main(args):
    university_dir = args.university_dir
    log_path = args.log_path
    article_pattern = '*_article.csv'
    for university in os.listdir(university_dir):
        logging.info(f"开始爬取{university}的作者")
        for dblp_raw_dir in os.listdir(university_dir + '/' + university):
            logging.info(f'开始爬取{dblp_raw_dir}')
            dblp_raw_full_dir = university_dir + '/' + university + '/' + dblp_raw_dir
            dblp_raw_file_list = glob.glob(dblp_raw_full_dir + '/' + article_pattern)
            if dblp_raw_file_list:
                dblp_raw_file = dblp_raw_file_list[0]
            else:
                logging.info(f"未在{dblp_raw_full_dir}文件夹内发现csv文件")
                continue

            try:
                d = DBLParser(dblp_raw_file)
            except UnicodeError:
                with open("./unicode_error.log", 'a') as ue:
                    ue.write(f'Found Chinese Character in ({dblp_raw_full_dir})\n')
                continue
            except IndexError:
                with open("./unicode_error.log", 'a') as ue:
                    ue.write(f'Found Nothing in ({dblp_raw_full_dir})\n')
                continue
            except BaseException:
                with open("./unicode_error.log", 'a') as ue:
                    ue.write(f'Found Unknown Error in ({dblp_raw_full_dir})\n')
                continue
            wos_input_file = dblp_raw_full_dir + '/wos_input.txt'
            d.save_for_spider(wos_input_file)
            logging.info('DBLP文件解析完毕，已生成爬虫输入')

            xls_dir = dblp_raw_full_dir + '/xls'
            if os.path.exists(xls_dir):
                print(f"已存在{xls_dir}文件夹")
                continue
            else:
                os.mkdir(xls_dir)
            kwargs = {
                'output_dir': xls_dir,
                'document_type': "",
                'output_format': 'saveToExcel',
                'query_path': wos_input_file,
                'error_log_path': log_path + '/error.log'
            }
            yield runner.crawl('AdvancedQuery', kwargs=kwargs)
            logging.info('已创建web of science爬虫')
    reactor.stop()


ap = argparse.ArgumentParser(usage='-i: University Directory; -o: Output Directory')
ap.add_argument('-i', '--input', help='University Directory', dest='university_dir', required=True)
ap.add_argument('-o', '--output', help='Output Directory', dest='log_path', required=True)
args = ap.parse_args()
main(args)
reactor.run()  # the script will block here until the last crawl call is finished
