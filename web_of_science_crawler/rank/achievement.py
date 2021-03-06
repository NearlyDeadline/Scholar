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
    UNKNOWN = 0
    FIRST_AUTHOR = 10
    CORRESPONDING_AUTHOR = 20


def get_index_paper_title(paper_title: str) -> str:
    return ''.join(list(filter(lambda c: str.isalpha(c), paper_title.lower())))


class Achievement:
    def __init__(self):
        self.data = pd.DataFrame(
            columns=('paper_title', 'contribution', 'dblp_author_name', 'xls_path'))
        self.ccf_rank = pd.DataFrame(columns=['ccf_key'])
        self.jcr_rank = pd.DataFrame(columns=['jcr_key'])

    __dblp_journal_start_pattern = '<journal>'
    __dblp_conference_start_pattern = '<crossref>'

    def load_dblp(self, dp: DBLParser):
        def get_venue_name(kind: str) -> str:
            result = ''
            if kind.startswith(self.__dblp_journal_start_pattern):
                # result = kind[len(self.__dblp_journal_start_pattern):].split('<')[0]
                pass  # 不再需要期刊的名字
            elif kind.startswith(self.__dblp_conference_start_pattern):
                result = kind[len(self.__dblp_conference_start_pattern):].split('<')[0].split('/')[1]
            else:
                pass
            return result

        contribution = Contribution.UNKNOWN.name
        author_name = dp.author_name
        xls_path = ''
        jcr_key = ''
        for row in dp.data.itertuples():
            paper_title = row[3]
            index_paper_title = get_index_paper_title(paper_title)
            self.data.loc[index_paper_title] = [paper_title, contribution, author_name, xls_path]
            ccf_key = get_venue_name(row[5])
            self.ccf_rank.loc[index_paper_title] = [ccf_key]
            self.jcr_rank.loc[index_paper_title] = [jcr_key]

    def load_wos(self, xp: XLSParser):
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
            index_paper_title = get_index_paper_title(xls_title)
            if index_paper_title not in self.data.index:
                print("未找到dblp数据，请检查web of science论文题目与dblp论文题目是否一致")
            else:
                dblp_fn, dblp_ln = xp.dblp_author_name.split(' ')  # ('Baopeng', 'Zhang')
                xls_full_name_list = xls_data['Author Full Names'][0].replace(' ', '').split(';')
                author_index = 0  # index为该作者在Author Full Name列里的序号
                for xls_full_name in xls_full_name_list:
                    xls_fn, xls_ln = xls_full_name.split(',')
                    if xls_fn == dblp_fn and xls_ln == dblp_ln:
                        break
                    if xls_fn == dblp_ln and xls_ln == dblp_fn:  # 根据Web of Science格式更改dblp的First Name与Last Name的顺序
                        dblp_fn, dblp_ln = xls_ln, xls_fn
                        break
                    author_index += 1

                short_name = xls_data['Authors'][0].replace(' ', '').split(';')[author_index]  # 'Zhang,BP'
                xls_corresponding_author = get_corresponding_author(xls_data['Reprint Addresses'][0])

                current_contribution = self.data.loc[index_paper_title, 'contribution']
                if author_index == 0 and current_contribution == Contribution.UNKNOWN.name:
                    c = Contribution.FIRST_AUTHOR.name
                    self.data.loc[index_paper_title, 'contribution'] = c
                elif short_name == xls_corresponding_author and current_contribution == Contribution.UNKNOWN.name:
                    c = Contribution.CORRESPONDING_AUTHOR.name
                    self.data.loc[index_paper_title, 'contribution'] = c
                self.data.loc[index_paper_title, 'xls_path'] = xp.xls_dir + '/' + xls

                self.jcr_rank.loc[index_paper_title] = [xls_data['Source Title'][0]]

    def get_rank_json(self):
        """
        (1)期刊：JCR和CCF内都有信息，且均用jcr_key

        (2)会议：JCR没有信息，只从CCF表提取，使用ccf_key
        """

        def get_ccf_rank_dict(ccf_key_: str) -> dict:
            """
            :param ccf_key_可能有两种情况：

            (1)会议：DBLP文件里提取的简称，需要与ccf.csv的“DBLP简称”或“CCF简称”列对应

            (2)期刊：XLS文件的Source Title列，需要与ccf.csv的“全称”列对应。这里需无视大小写

            由于无法区分两种情况的值，所以依次搜索两列，凡可得到结果的情况就作为结果
            """
            ccf_data = pd.read_csv('ccf.csv', header=0, index_col=[0])
            ccf_data.fillna('', inplace=True)

            if ccf_key_ in ccf_data.index:  # 期刊，直接访问索引
                target_row = ccf_data.loc[ccf_key_]
                ccf_rank_dict = {
                    'CCF Abbr': target_row['CCF简称'],
                    'Venue Full Name': target_row['全称'],
                    'Field': target_row['领域'],
                    'Rank': target_row['评级']
                }
                return ccf_rank_dict

            # 会议，依次搜索“DBLP简称”，“CCF简称”两列。这里不是访问索引，因此需要访问第0个元素
            target_row = ccf_data.loc[ccf_data['DBLP简称'] == ccf_key_]
            if target_row.empty:
                target_row = ccf_data.loc[ccf_data['CCF简称'] == ccf_key_.upper()]
                if target_row.empty:
                    print(f"无法在CCF表中查到该文献的发表刊物: {ccf_key_}")
                    return {}

            ccf_rank_dict = {
                'CCF Abbr': target_row['CCF简称'][0],
                'Venue Full Name': target_row['全称'][0],
                'Field': target_row['领域'][0],
                'Rank': target_row['评级'][0]
            }
            return ccf_rank_dict

        def get_jcr_rank_dict(jcr_key_: str) -> dict:
            """
            :param jcr_key_只有一种情况：期刊。直接查表即可
            """
            jcr_rank_dict = {}
            if not pd.isna(jcr_key_):
                jcr = json.load(open('jcr.json'))
                jcr = CIMultiDict(jcr)
                if jcr.get(jcr_key_):
                    jcr_rank_dict = jcr.get(jcr_key_)
            return jcr_rank_dict

        result = {}
        if not self.data.empty:
            result['Author Name'] = self.data['dblp_author_name'][0]
            result['Achievements'] = []
            for row in self.data.itertuples():
                ac = {
                    'Paper Title': row[1],
                    'Contribution': row[2],
                    'Venue': '',
                    'JCR': {},
                    'CCF': {}
                }
                jcr_key = self.jcr_rank.loc[row[0]]['jcr_key']
                if jcr_key:  # 先查一下JCR信息。对于Web of Science收录的期刊论文，应当一直进入本if判断语句
                    ac['JCR'] = get_jcr_rank_dict(jcr_key)
                    ac['Venue'] = {'Journal': jcr_key}
                    ac['CCF'] = get_ccf_rank_dict(get_index_paper_title(jcr_key))
                if not ac['JCR']:  # JCR没有有用的信息。既有可能是会议论文，jcr_key为空；又有可能是上述jcr_key查表过程没有有用信息
                    ccf_key = self.ccf_rank.loc[row[0]]['ccf_key']
                    ac['Venue'] = {'Conference': ccf_key}
                    ac['CCF'] = get_ccf_rank_dict(ccf_key)
                result['Achievements'].append(ac)

        return result

    def save_csv(self, output_dir: str):
        self.data.to_csv(output_dir + '/_achievement.csv')
        self.ccf_rank.to_csv(output_dir + '/_ccf.csv')
        self.jcr_rank.to_csv(output_dir + '/_jcr.csv')
