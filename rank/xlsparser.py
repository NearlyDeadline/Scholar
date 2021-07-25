# -*- coding: utf-8 -*-
# @Time    : 2021/7/25 14:03
# @Author  : Mike
# @File    : XLSParser

class XLSParser:
    def __init__(self, xls_dir: str, author_name: str):
        self.xls_dir = xls_dir
        self.author_name = author_name

        # for xls_path in os.listdir(xls_dir):
        #     xls_data = pd.read_excel(xls_dir + '/' + xls_path)
        #     xls_title = xls_data['Article Title'][0]
        #     xls_first_author = xls_data['Author Full Names'][0].strip(';')
        #     xls_first_author = ''.join(list(filter(lambda c: str.isalpha(c), xls_first_author[0].lower())))
        #
        #     def getCorrespondingAuthor(reprint_addresses: str) -> str:
        #         authors = reprint_addresses.split('corresponding author')
        #         if len(authors) == 1:
        #             authors = reprint_addresses.split('Corresponding author')
        #         if len(authors) > 1:
        #             return ''.join(list(filter(lambda c: str.isalpha(c), authors[0].lower())))
        #         else:
        #             return ''
        #
        #     xls_corresponding_author = getCorrespondingAuthor(xls_data['Reprint Addresses'][0])
        #     author_name = ''.join(list(filter(lambda c: str.isalpha(c), author_name.lower())))

        # if os.path.exists(contribution_path):
        #     with open(contribution_path, 'a', newline='') as contribution_file:
        #         csv_writer = csv.writer(contribution_file)
        #         for title, contribution in self.title_contribution_dict.items():
        #             row = [author_name, title, contribution.paper_path, str(contribution.is_first_author),
        #                    str(contribution.is_corresponding_author)]
        #             csv_writer.writerow(row)
        # else:
        #     with open(contribution_path, 'w', newline='') as contribution_file:
        #         csv_writer = csv.writer(contribution_file)
        #         headers = ['author_name', 'paper_title', 'paper_path', 'is_first_author', 'is_corresponding_author']
        #         csv_writer.writerow(headers)
        #         for title, contribution in self.title_contribution_dict.items():
        #             row = [author_name, title, contribution.paper_path, str(contribution.is_first_author),
        #                    str(contribution.is_corresponding_author)]
        #             csv_writer.writerow(row)
