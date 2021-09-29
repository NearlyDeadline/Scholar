# -*- coding: utf-8 -*-
# @Time    : 2021/7/24 11:40
# @Author  : Mike
# @File    : Achievement
import json
from enum import Enum
import pandas as pd
from .dblparser import DBLParser
from .xlsparser import XLSParser
import os
from multidict import CIMultiDict


class Contribution(Enum):
    PAPER_AUTHOR = 0
    FIRST_AUTHOR = 10
    CORRESPONDING_AUTHOR = 20


def get_index(text: str) -> str:
    return ''.join(list(filter(lambda c: str.isalpha(c), text.lower())))


class Achievement:
    def __init__(self, author_name):
        self.paper_table = pd.DataFrame(
            columns=('paper_title', 'pub_year', 'contribution', 'author_count', 'venue', 'kind'))
        self.author_name = author_name

    def add_paper(self, paper_title: str, pub_year: str, contribution: Contribution, author_count: int = 0, venue: str = '', kind: str = ''):
        index_paper_title = get_index(paper_title)
        self.paper_table.loc[index_paper_title] = [paper_title, pub_year, contribution.name, author_count, venue, kind]
        
    def delete_paper(self, paper_title: str):
        index_paper_title = get_index(paper_title)
        if index_paper_title not in self.paper_table.index:
            print(f"Can not found paper {paper_title}")
            return
        self.paper_table.drop([index_paper_title], inplace=True)

    def set_column_value(self, paper_title: str, column_name: str, value: str):
        if column_name not in self.paper_table.columns:
            print(f'{column_name} is not a column name.')
            return
        index_paper_title = get_index(paper_title)
        if index_paper_title not in self.paper_table.index:
            print(f'{paper_title} does not exist in paper table.')
            return
        self.paper_table.loc[get_index(paper_title), column_name] = value

    def load_dblp(self, dp: DBLParser):
        """
        :return: 初始化paper_table
        """
        for row in dp.data.itertuples():
            paper_title = row[3]
            pub_year = str(row[4])
            contribution = Contribution.FIRST_AUTHOR if row[8] == 'True' else Contribution.PAPER_AUTHOR
            author_count = int(row[7])
            venue = row[6]
            if row[5].startswith('<journal>'):
                kind = 'journal'
            elif row[5].startswith('<crossref>'):
                kind = 'crossref'
            else:
                kind = ''
            self.add_paper(paper_title, pub_year, contribution, author_count, venue, kind)

    def load_wos(self, xp: XLSParser):
        """
        :return: 在DBLP的基础上完善contribution
        """
        def get_corresponding_author(reprint_addresses: str) -> str:
            ra = reprint_addresses.split('(corresponding author)')
            if len(ra) == 1:
                ra = reprint_addresses.split('(Corresponding author)')
            if len(ra) > 1:
                return ra[0].replace(' ', '')
            else:
                return ''

        for xls in os.listdir(xp.xls_dir):
            xls_data = pd.read_excel(xp.xls_dir + '/' + xls)
            xls_title = xls_data['Article Title'][0]
            index_paper_title = get_index(xls_title)
            if index_paper_title not in self.paper_table.index:
                print("未找到dblp数据，请检查web of science论文题目与dblp论文题目是否一致")
            else:
                dblp_first_name, dblp_last_name = xp.dblp_author_name.split(' ')  # ('Baopeng', 'Zhang')
                xls_full_name_list = xls_data['Author Full Names'][0].replace(' ', '').split(';')
                author_index = 0  # index为该作者在Author Full Name列里的序号
                for xls_full_name in xls_full_name_list:
                    xls_first_name, xls_last_name = xls_full_name.split(',')
                    if xls_first_name == dblp_first_name and xls_last_name == dblp_last_name:
                        break
                    if xls_first_name == dblp_last_name and xls_last_name == dblp_first_name:  # 根据Web of Science格式更改dblp的First Name与Last Name的顺序
                        dblp_first_name, dblp_last_name = xls_last_name, xls_first_name
                        break
                    author_index += 1

                short_name = xls_data['Authors'][0].replace(' ', '').split(';')[author_index]  # 'Zhang,BP'
                xls_corresponding_author = get_corresponding_author(xls_data['Reprint Addresses'][0])

                current_contribution = self.paper_table.loc[index_paper_title, 'contribution']
                if author_index == 0 and current_contribution == Contribution.PAPER_AUTHOR.name:
                    c = Contribution.FIRST_AUTHOR.name
                    self.set_column_value(xls_title, 'contribution', c)
                elif short_name == xls_corresponding_author and current_contribution == Contribution.PAPER_AUTHOR.name:
                    c = Contribution.CORRESPONDING_AUTHOR.name
                    self.set_column_value(xls_title, 'contribution', c)

                self.set_column_value(xls_title, 'venue', xls_title)

    def get_rank_json(self):
        """
        (1)期刊：JCR和CCF内都有信息

        (2)会议：JCR没有信息，只从CCF表提取
        """

        def get_ccf_rank_dict(venue_: str, year: str) -> dict:
            """
            :param year 年份
            :param venue_可能有两种情况：

            (1)会议：DBLP文件里提取的简称，需要与ccf.csv的“DBLP简称”或“CCF简称”列对应

            (2)期刊：XLS文件的Source Title列，需要与ccf.csv的“全称”列对应。这里需无视大小写

            由于无法区分两种情况的值，所以依次搜索两列，凡可得到结果的情况就作为结果
            """
            if int(year) >= 2019:
                year = '2019'
            else:
                year = '2015'
            ccf_data = pd.read_csv(f'rank/ccf_{year}.csv', header=0, index_col=[0])
            ccf_data.fillna('', inplace=True)

            if venue_ in ccf_data.index:  # 全称，直接访问索引
                target_row = ccf_data.loc[venue_]
                ccf_rank_dict = {
                    'CCF Abbr': target_row['CCF简称'],
                    'Venue Full Name': target_row['全称'],
                    'Field': target_row['领域'],
                    'Rank': target_row['评级']
                }
                return ccf_rank_dict

            # 会议，依次搜索“DBLP简称”，“CCF简称”两列。这里不是访问索引，因此需要访问第0个元素
            target_row = ccf_data.loc[ccf_data['DBLP简称'] == venue_]
            if target_row.empty:
                target_row = ccf_data.loc[ccf_data['CCF简称'] == venue_.upper()]
                if target_row.empty:
                    return {}

            ccf_rank_dict = {
                'CCF Abbr': target_row['CCF简称'][0],
                'Venue Full Name': target_row['全称'][0],
                'Field': target_row['领域'][0],
                'Rank': target_row['评级'][0]
            }
            return ccf_rank_dict

        def get_jcr_rank_dict(venue_: str, year: str) -> dict:
            """
            :param venue_只有一种情况：期刊。直接查表即可
            :param year 年份，'2015'-'2020'之间的值
            """
            if int(year) >= 2020:
                year = '2020'
            elif int(year) < 2015:
                year = '2015'
            jcr_rank_dict = {}
            if not pd.isna(venue_):
                jcr = json.load(open(f'rank/jcr_{year}.json'))
                jcr = CIMultiDict(jcr)
                if jcr.get(venue_):
                    jcr_rank_dict = jcr.get(venue_)
            return jcr_rank_dict

        def get_cas_rank_dict(venue_:str, year: str) -> dict:
            """
            :param venue_只有一种情况：期刊。直接查表即可
            :param year 年份，'2015'-'2019'之间的值
            """
            if int(year) >= 2019:
                year = '2019'
            elif int(year) < 2015:
                year = '2015'
            cas_rank_dict = {}
            if not pd.isna(venue_):
                cas = json.load(open(f'rank/cas_{year}.json'))
                cas = CIMultiDict(cas)
                if cas.get(venue_):
                    cas_rank_dict = cas.get(venue_)
            return cas_rank_dict

        result = {}
        result['Author Name'] = self.author_name
        result['Achievements'] = []
        for row in self.paper_table.itertuples():
            ac = {
                'Paper Title': row[1],
                'Contribution': row[3],
                'Author Count': row[4],
                'Venue': row[5],
                '汤森路透分区': {},
                '中科院分区': {},
                'CCF': {}
            }
            venue = row[5]
            pub_year = row[2]
            kind = row[6]

            jcr_rank_dict = get_jcr_rank_dict(venue, pub_year)
            if jcr_rank_dict:
                ac['汤森路透分区'] = jcr_rank_dict

            cas_rank_dict = get_cas_rank_dict(venue, pub_year)
            if cas_rank_dict:
                ac['中科院分区'] = cas_rank_dict

            if (jcr_rank_dict or cas_rank_dict) and kind == 'journal':
                ac['Venue'] = {'Journal': venue}

            ccf_rank_dict = get_ccf_rank_dict(get_index(venue), pub_year)
            if ccf_rank_dict:
                ac['CCF'] = ccf_rank_dict

            if ccf_rank_dict and kind == 'crossref':
                ac['Venue'] = {'Conference': venue}

            result['Achievements'].append(ac)

        return result

    def save_csv(self, output_dir: str):
        self.paper_table.to_csv(output_dir + '/_achievement.csv')
