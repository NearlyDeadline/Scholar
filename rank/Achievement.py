# -*- coding: utf-8 -*-
# @Time    : 2021/7/24 11:40
# @Author  : Mike
# @File    : Achievement
import json
from enum import Enum
import pandas as pd
import DBLParser
import XLSParser
import os


class Contribution(Enum):
    UNKNOWN = 0
    FIRST_AUTHOR = 10
    CORRESPONDING_AUTHOR = 20


def get_index_paper_title(paper_title):
    return ''.join(list(filter(lambda c: str.isalpha(c), paper_title.lower())))


class Achievement:
    def __init__(self):
        self.data = pd.DataFrame(
            columns=('index_paper_title', 'paper_title', 'contribution', 'author_name', 'xls_path'))
        self.data.set_index(['index_paper_title', 'paper_title'])

        self.ccf_rank = pd.DataFrame(columns=('index_paper_title', 'ccf_key'))
        self.ccf_rank.set_index('index_paper_title')

        self.jcr_rank = pd.DataFrame(columns=('index_paper_title', 'jcr_key'))
        self.jcr_rank.set_index('index_paper_title')

    __dblp_journal_start_pattern = '<journal>'
    __dblp_conference_start_pattern = '<crossref>'

    def dblp(self, dblparser: DBLParser.DBLParser):
        def get_venue_name(kind: str) -> str:
            result = ''
            if kind.startswith(self.__dblp_journal_start_pattern):
                result = kind[len(self.__dblp_journal_start_pattern):].split('<')[0]
            elif kind.startswith(self.__dblp_conference_start_pattern):
                result = kind[len(self.__dblp_conference_start_pattern):].split('<')[0].split('/')[1]
            else:
                pass
            return result

        self.data['paper_title'] = dblparser.data['title']
        self.data['index_paper_title'] = [s.strip('.') for s in self.data['paper_title']]
        self.data['contribution'] = [Contribution.UNKNOWN.name for i in range(0, self.data.shape[0])]
        self.data['author_name'] = [dblparser.author_name for i in range(0, self.data.shape[0])]
        self.data['xls_path'] = ['' for i in range(0, self.data.shape[0])]

        self.ccf_rank['index_paper_title'] = self.data['index_paper_title']
        self.ccf_rank['ccf_key'] = [get_venue_name(v) for v in dblparser.data['kind']]

        self.jcr_rank['index_paper_title'] = self.data['index_paper_title']

    def wos(self, xlsparser: XLSParser.XLSParser):
        def get_corresponding_author(reprint_addresses: str) -> str:
            authors = reprint_addresses.split('corresponding author')
            if len(authors) == 1:
                authors = reprint_addresses.split('Corresponding author')
            if len(authors) > 1:
                return ''.join(list(filter(lambda ch: str.isalpha(ch), authors[0].lower())))
            else:
                return ''

        for xls in os.listdir(xlsparser.xls_dir):
            xls_data = pd.read_excel(xlsparser.xls_dir + '/' + xls)
            xls_title = xls_data['Article Title'][0]
            index_paper_title = get_index_paper_title(xls_title)
            row = self.data.loc[self.data['index_paper_title'] == index_paper_title]
            if row.empty:
                print("未找到dblp数据，请检查web of science论文题目与dblp论文题目是否一致")
            else:
                xls_first_author = ''.join(
                    list(filter(lambda ch: str.isalpha(ch), xls_data['Author Full Names'][0].strip(';')[0].lower())))
                xls_corresponding_author = get_corresponding_author(xls_data['Reprint Addresses'][0])
                author_name = ''.join(list(filter(lambda ch: str.isalpha(ch), xlsparser.author_name.lower())))

                current_contribution = row.iloc[0]['contribution']
                if author_name.startswith(xls_first_author) and current_contribution == Contribution.UNKNOWN.name:
                    c = Contribution.FIRST_AUTHOR.name
                    row.iloc[0]['contribution'] = c
                elif author_name.startswith(
                        xls_corresponding_author) and current_contribution == Contribution.UNKNOWN.name:
                    c = Contribution.CORRESPONDING_AUTHOR.name
                    row.iloc[0]['contribution'] = c
                row.iloc[0]['xls_path'] = xlsparser.xls_dir + '/' + xls

                self.jcr_rank.loc[index_paper_title] = [index_paper_title, xls_data['Source Title'][0]]

    def get_rank_json(self):
        jcr = json.load('jcr.json')
        ccf = pd.read_csv('ccf.csv')
        result = {}
        if not self.data.empty:
            result['Author Name'] = self.data['author_name'][0]
            result['Achievements'] = []
            for row in self.data.itertuples():
                ac = {}
                ac['Paper Title'] = row[1]
                ac['Contribution'] = row[2]
                # ac['JCR'] = 查self.jcr_rank表获取jcr_key，进入jcr.json查找
                # ac['CCF'] = 查self.ccf_rank表获取ccf_key，进入ccf.csv查找
                result['Achievements'].append(ac)

        return json.dumps(result)

    def save_csv(self, output_path: str):
        pass  # 将self.data输出到output_path里
