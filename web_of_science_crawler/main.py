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
from rank.achievement import Achievement, get_index_paper_title, Contribution
from rank.xlsparser import XLSParser
import json

configure_logging()
runner = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def main(args):
    input_dir = args.input_dir
    log_path = args.log_path
    wos_crawler = args.wos_crawler
    article_pattern = '*_article.csv'

    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler(log_path + "/main_log.txt")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    for dblp_raw_dir in os.listdir(input_dir):
        dblp_raw_dir = input_dir + '/' + dblp_raw_dir
        dblp_raw_file_list = glob.glob(dblp_raw_dir + '/' + article_pattern)
        if dblp_raw_file_list:
            dblp_raw_file = dblp_raw_file_list[0]  # 只选择第一个
        else:
            logger.warning(f"未在{dblp_raw_dir}文件夹内发现csv文件")
            continue
        try:
            d = DBLParser(dblp_raw_file)
        except UnicodeError:
            logger.error(f'Found Chinese Character in ({dblp_raw_dir})\n')
            continue
        except IndexError:
            logger.error(f'Found Nothing in ({dblp_raw_dir})\n')
            continue
        except BaseException:
            logger.error(f'Found Unknown Error in ({dblp_raw_dir})\n')
            continue

        ac = Achievement(d.author_name)
        ac.load_dblp(d)

        if wos_crawler == 1:
            wos_input_file = dblp_raw_dir + '/wos_input.txt'
            d.save_for_spider(wos_input_file)

            xls_dir = dblp_raw_dir + '/xls'
            if os.path.exists(xls_dir):
                logger.warning(f'已在{dblp_raw_dir}建立xls文件夹')
            else:
                os.mkdir(xls_dir)
            wos_spider_kwargs = {
                'output_dir': xls_dir,
                'document_type': "",
                'output_format': 'saveToExcel',
                'query_path': wos_input_file,
                'error_log_path': log_path
            }
            x = XLSParser(xls_dir, d.author_name)
            try:
                yield runner.crawl('AdvancedQuery', kwargs=wos_spider_kwargs)
            except SystemExit:
                logger.error(f'{dblp_raw_dir}发生了Web of Science爬虫错误，请检查该文件夹内爬虫日志文件')
            finally:
                ac.load_wos(x)

        rank_json = ac.get_rank_json()
        with open(log_path + '/' + d.author_name + '_achievement.json', 'w', encoding='utf-8') as rj:
            rj.write(json.dumps(rank_json, indent=4, ensure_ascii=False))

    if wos_crawler == 1:
        reactor.stop()


ap = argparse.ArgumentParser(usage='-i: Input Directory; -o: Output Directory')
ap.add_argument('-i', '--input', help='Input Directory', dest='input_dir', required=True)
ap.add_argument('-o', '--output', help='Output Directory', dest='log_path', required=True)
ap.add_argument('-w', '--wos_crawler', help='Enable Web of Science Crawler if 1, disable if 0', dest='wos_crawler', type=int, choices=range(0, 2), default=0)
args = ap.parse_args()
main(args)
if args.wos_crawler == 1:
    reactor.run()  # the script will block here until the last crawl call is finished
