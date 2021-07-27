# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 15:09
# @Author  : Mike
# @File    : get_rank_json
from dblparser import DBLParser
from xlsparser import XLSParser
from achievement import Achievement
import json
import os

if __name__ == '__main__':
    dblp_raw_file = '../test/北京交通大学/北京交通大学_BaopengZhang/BaopengZhang_article.csv'
    dblp_raw_dir = os.path.dirname(dblp_raw_file)
    d = DBLParser(dblp_raw_file)

    wos_input_file = dblp_raw_dir + '/wos_input.txt'
    d.save_for_spider(wos_input_file)

    xls_dir = dblp_raw_dir + '/xls'

    x = XLSParser(xls_dir, d.author_name)
    a = Achievement()
    a.load_dblp(d)
    a.load_wos(x)
    rank_json = a.get_rank_json()
    with open(dblp_raw_dir + 'achievement.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(rank_json, indent=4, ensure_ascii=False))
