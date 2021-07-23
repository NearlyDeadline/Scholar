# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 15:09
# @Author  : Mike
# @File    : rank
import pandas as pd
import string
import os
from web_of_science_crawler.main import AdvancedQuerySpiderRunner


class DBLParser:
    __journal_start_pattern = '<journal>'
    __conference_start_pattern = '<crossref>'
    title_list = []
    author_name = ''

    def __init__(self, csv_path: str, query_path: str):
        """

        :param csv_path: DBLP的csv文件
        :param query_path: 用于Web of Science爬虫的输入文件，每一行为该作者的一篇论文的题目
        """
        with open(csv_path) as csv_file:
            self.data = pd.read_csv(csv_file)

            for title in self.data['title']:
                self.title_list.append(title)

            self.author_name = self.data['name'][0].rstrip(string.digits).strip(' ')

            # for kind in self.data['kind']:
            #     if kind.startswith(self.__journal_start_pattern):
            #         journal_name = kind[len(self.__journal_start_pattern):].split('<')[0]
            #         print(f"journal: {journal_name}")
            #     elif kind.startswith(self.__conference_start_pattern):
            #         conf_name = kind[len(self.__conference_start_pattern):].split(('<'))[0].split('/')[1]
            #         print(f"conference: {conf_name}")
            #     else:
            #         print("nothing")

        with open(query_path, 'w') as query_file:
            query_file.write(self.title_list[0])
            for i in range(1, len(self.title_list)):
                query_file.write('\n' + self.title_list[i])


# 遍历output_dir下每个xls文件，识别第一作者/通讯作者
class XLSParser:
    # contribution_path: 每一行表明该作者与一篇论文的关系，应包含：论文元信息（题目等），以及作者的贡献（一作/通讯/非一作非通讯/未知）
    def __init__(self, papers_dir: str, author_name: str, contribution_path: str):
        pass


# 识别为相应作者的，查表获取论文排名；识别不是相应作者的，丢弃；无法确定的，单独输出

class Ranker:
    def __init__(self, contribution_path: str, result_path: str):
        pass


if __name__ == '__main__':
    dblp_raw_file = '../test/北京交通大学_article.csv'
    wos_input_file = '../test/北京交通大学_article.txt'
    d = DBLParser(dblp_raw_file, wos_input_file)

    xls_dir = '../test/xls'
    error_log_path = wos_input_file + '.log'

    a = AdvancedQuerySpiderRunner(wos_input_file, xls_dir, output_format='saveToExcel', error_log_path=error_log_path)

    author_contribution_path = '../test/contribution.txt'
    x = XLSParser(xls_dir, d.author_name, author_contribution_path)

    rank_path = '../test/rank.txt'
    r = Ranker(author_contribution_path, rank_path)
