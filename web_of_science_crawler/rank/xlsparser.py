# -*- coding: utf-8 -*-
# @Time    : 2021/7/25 14:03
# @Author  : Mike
# @File    : XLSParser

class XLSParser:
    def __init__(self, xls_dir: str, author_name: str):
        self.xls_dir = xls_dir
        self.dblp_author_name = author_name
