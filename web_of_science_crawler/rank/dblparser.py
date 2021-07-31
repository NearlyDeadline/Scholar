# -*- coding: utf-8 -*-
# @Time    : 2021/7/24 11:36
# @Author  : Mike
# @File    : DBLParser
import pandas as pd
import string


class DBLParser:
    author_name = ''

    def __init__(self, csv_path: str):
        """
        :param csv_path: DBLP的csv文件
        """
        with open(csv_path) as csv_file:
            self.data = pd.read_csv(csv_file)
            self.author_name = self.data['name'][0].rstrip(string.digits).rstrip(string.punctuation)

    def save_for_spider(self, query_path):
        """
        :param query_path: 用于Web of Science爬虫的输入文件，每一行为该作者的一篇论文的题目
        """
        with open(query_path, 'w') as query_file:
            title_list = []
            for title in self.data['title']:
                title_list.append(title)
            for i in range(0, len(title_list)):
                query_file.write(title_list[i] + '\n')
