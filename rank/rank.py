# -*- coding: utf-8 -*-
# @Time    : 2021/7/14 15:09
# @Author  : Mike
# @File    : rank
import csv
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


class Contribution:
    paper_title = ''
    paper_path = ''
    is_first_author = False
    is_corresponding_author = False


# 遍历output_dir下每个xls文件，识别第一作者/通讯作者
class XLSParser:
    title_contribution_dict = {}

    # contribution_path: 每一行表明该作者与一篇论文的关系，应包含：论文元信息（题目等），以及作者的贡献（一作/通讯/非一作非通讯/未知）
    def __init__(self, papers_dir: str, author_name: str, contribution_path: str):
        for xls_path in os.listdir(papers_dir):
            xls_data = pd.read_excel(papers_dir + '/' + xls_path)
            xls_title = xls_data['Article Title'][0]
            xls_first_author = xls_data['Author Full Names'][0].strip(';')
            xls_first_author = ''.join(list(filter(lambda c: str.isalpha(c), xls_first_author[0].lower())))

            def getCorrespondingAuthor(reprint_addresses: str) -> str:
                authors = reprint_addresses.split('corresponding author')
                if len(authors) == 1:
                    authors = reprint_addresses.split('Corresponding author')
                if len(authors) > 1:
                    return ''.join(list(filter(lambda c: str.isalpha(c), authors[0].lower())))
                else:
                    return ''

            xls_corresponding_author = getCorrespondingAuthor(xls_data['Reprint Addresses'][0])
            author_name = ''.join(list(filter(lambda c: str.isalpha(c), author_name.lower())))

            pc = Contribution()
            pc.paper_title = xls_title
            pc.paper_path = xls_path
            if author_name.startswith(xls_first_author):
                pc.is_first_author = True
            if author_name.startswith(xls_corresponding_author):
                pc.is_corresponding_author = True

            self.title_contribution_dict[xls_title] = pc

        if os.path.exists(contribution_path):
            with open(contribution_path, 'a', newline='') as contribution_file:
                csv_writer = csv.writer(contribution_file)
                for title, contribution in self.title_contribution_dict.items():
                    row = [author_name, title, contribution.paper_path, str(contribution.is_first_author),
                           str(contribution.is_corresponding_author)]
                    csv_writer.writerow(row)
        else:
            with open(contribution_path, 'w', newline='') as contribution_file:
                csv_writer = csv.writer(contribution_file)
                headers = ['author_name', 'paper_title', 'paper_path', 'is_first_author', 'is_corresponding_author']
                csv_writer.writerow(headers)
                for title, contribution in self.title_contribution_dict.items():
                    row = [author_name, title, contribution.paper_path, str(contribution.is_first_author),
                           str(contribution.is_corresponding_author)]
                    csv_writer.writerow(row)


# 识别为相应作者的，查表获取论文排名；识别不是相应作者的，丢弃；无法确定的，单独输出

class Ranker:
    def __init__(self, contribution_path: str, result_path: str):
        pass


if __name__ == '__main__':
    author_name = ['Khosla, Megha', 'Setty, Vinay', 'Anand, Avishek', 'Khosla, Megha']
    for an in author_name:
        x = XLSParser('../test/xls', an, '../test/contrib/' + an + '.csv')
        for k, v in x.title_contribution_dict.items():
            print(f'key: {k}')
            print(f'paper_path: {v.paper_path}')
            print(f'is_first_author: {v.is_first_author}')
            print(f'is_corresponding_author: {v.is_corresponding_author}')


def main():
    dblp_raw_file = '../test/北京交通大学_article.csv'
    wos_input_file = '../test/北京交通大学_article.txt'
    d = DBLParser(dblp_raw_file, wos_input_file)

    xls_dir = '../test/xls'
    error_log_path = wos_input_file + '.log'

    a = AdvancedQuerySpiderRunner(wos_input_file, xls_dir, output_format='saveToExcel', error_log_path=error_log_path)

    author_contribution_path = '../test/title_contribution_dict.txt'
    x = XLSParser(xls_dir, d.author_name, author_contribution_path)

    rank_path = '../test/rank.txt'
    r = Ranker(author_contribution_path, rank_path)
