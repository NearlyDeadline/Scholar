import re

import pandas as pd
import pypinyin
import requests
from bs4 import BeautifulSoup


##############################姓名转换#########################################
def name_trans():
    fileName = ['D:/大学副教授名单/北京交通大学',
                'D:/大学副教授名单/北京师范大学',
                'D:/大学副教授名单/吉林大学',
                'D:/大学副教授名单/东南大学',
                'D:/大学副教授名单/同济大学',
                'D:/大学副教授名单/电子科技大学',
                'D:/大学副教授名单/北京科技大学',
                ]
    for k in range(len(fileName)):
        df = pd.read_csv(str(fileName[k]) + '.csv', encoding='gbk')
        print(str(fileName[k]) + '.csv')
        print(df.head())

        pinyin_name = []
        first_pinyin = []
        pinyin_name1 = []
        ming_name = []
        xing_name = []
        for i in df['姓名']:
            result = pypinyin.pinyin(i, style=pypinyin.NORMAL)
            result_ = [i[0] for i in result]
            result2 = ''.join(result_[1:]).capitalize()+' '+result_[0].capitalize()
            result3 = ''.join([i[0].upper()for i in result_])
            result4 = ''.join(result_[1:]).capitalize()+'-'+result_[0].capitalize()
            result5 = ''.join(result_[1:]).capitalize()
            result6 = result_[0].capitalize()
            print(result2, i, sep='')
            pinyin_name.append(result2)
            first_pinyin.append(result3)
            pinyin_name1.append(result4)
            ming_name.append(result5)
            xing_name.append(result6)

        df['英文名'] = pinyin_name
        df['拼音首字母'] = first_pinyin
        df['连词符连接'] = pinyin_name1
        df['名'] = ming_name
        df['姓'] = xing_name
        df.to_csv(str(fileName[k]) + '_English.csv', encoding='gbk', sep=',', header=True, index=True)
        print(df.head())


#######################################姓名转换##########################################


####################################获取pid#########################################
def getPid(name_xing,name_ming):
    url = 'https://dblp.uni-trier.de/search/author?xauthor='+name_ming+'%20'+name_xing
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        # print(r.text)
        return r.text
    except:
        return ""

def fillUnivList(ulist, html, name_xing, name_ming):
    soup = BeautifulSoup(html, "html.parser")
    name = str(name_ming)+' '+str(name_xing)
    print(name)
    # 后面是编号的匹配
    pattern1 = re.compile(name+' '+r'[0-9]')
    # 精确匹配
    pattern2 = re.compile('^'+name+'$')
    for author in soup.findAll('author'):
        if re.match(pattern1, author.string):
            ulist.append([author.get_text(), author.attrs['pid'], author.attrs['urlpt']])
        if re.match(pattern2, author.string):
            ulist.append([author.get_text(), author.attrs['pid'], author.attrs['urlpt'], 'disambiguation'])



def printUnivList(ulist, num, filename):
    with open(filename+'_pid.csv', "w") as file:
        file.write(','.join(['姓名', 'pid', 'urlpt']))
        file.write('\n')
        for i in range(num):
            u = ulist[i]
            file.write(','.join(u))
            file.write('\n')


def get_pid_main():
    uinfo = []
    fileName = ['D:/大学副教授名单/北京交通大学',
                'D:/大学副教授名单/北京师范大学',
                'D:/大学副教授名单/吉林大学',
                'D:/大学副教授名单/东南大学',
                'D:/大学副教授名单/同济大学',
                'D:/大学副教授名单/电子科技大学',
                'D:/大学副教授名单/北京科技大学',
                ]
    for k in range(len(fileName)):
        df = pd.read_csv(str(fileName[k])+'_English.csv', encoding='gbk')
        for i in range(df.shape[0]):
            # 东南大学有个外国人
            if df.loc[i, '姓']:
                name_xing = df.loc[i, '姓']
            else:
                name_xing = ''
            if df.loc[i, '名']:
                name_ming = df.loc[i, '名']
            else:
                name_ming = ''
            html = getPid(name_xing, name_ming)
            fillUnivList(uinfo, html, name_xing, name_ming)
            printUnivList(uinfo, len(uinfo), fileName[k])

##########################################获取pid####################################


######################################找人#################################
def getXml(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print('ssss')
        return ""

# noteList:学校信息
# urlList:详细信息里的url
# articleList:保存论文信息
# conList：保存会议信息
# school:学校名称
# inforList：个人信息，姓名，pid
def findExactInfo(noteList, inforList, html, school):
    soup = BeautifulSoup(html, "html.parser")
    dblpperson = soup.find('dblpperson')
    name = dblpperson.attrs['name']
    pid = dblpperson.attrs['pid']
    person = soup.find('person')
    if person:
        if person.find('note'):
            # 不是消歧页面
            print('非消歧')
            note = person.find('note')
            if note.string.find(str(school)) != -1:
                # 匹配学校
                print('学校匹配')
                inforList.append([name, pid])
                noteList.append([note.string])
            else:
                print('学校不匹配')
        else:
            # 消歧页面
            print('消歧')
            inforList.append([name, pid])
            noteList.append([])


def printExactInfo(noteList, inforList, num, filename):
    with open(filename+'_infor.csv', "w") as file:
        file.write(','.join(['name', 'pid', 'school', 'url']))
        file.write('\n')
        for i in range(num):
            r = inforList[i]
            n = noteList[i]
            file.write(','.join(r))
            file.write(',')
            file.write(','.join(n))
            file.write('\n')


def find_person_main():
    uinfo = []
    fileName = ['D:/大学副教授名单/北京交通大学',
                'D:/大学副教授名单/北京师范大学',
                'D:/大学副教授名单/吉林大学',
                'D:/大学副教授名单/东南大学',
                'D:/大学副教授名单/同济大学',
                'D:/大学副教授名单/电子科技大学',
                'D:/大学副教授名单/北京科技大学',
                ]
    schoolName = ['Beijing Jiaotong University', 'Beijing Normal University', 'Jilin University',
                  'Southeast University', 'Tongji University', 'University of Electronic Science and Technology of China',
                  'University of Science and Technology Beijing']
    noteList = []
    urlList = []
    articleList = []
    conList = []
    inforList = []
    df_1 = pd.read_csv('D:/大学副教授名单/北京交通大学_pid.csv', encoding='gbk')
    for m in range(df_1.shape[0]-1, -1, -1):
        # 这里需要逆序，因为消歧页面在待消歧之前
        print(df_1.iloc[m, 0])
        url = 'https://dblp.uni-trier.de/pid/'+df_1.iloc[m, 0]+'.xml'
        html = getXml(url)
        findExactInfo(noteList, inforList, html, 'Beijing Jiaotong University')
        printExactInfo(noteList, inforList, len(inforList), 'D:/大学副教授名单/北京交通大学')
    print('sssssssss')
    print('\n')
    print('\n')
    print('\n')

########################################找人##########################################


#######################################找论文####################################
'''
def getXml(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print('ssss')
        return ""

'''
# articleList:保存论文信息
# conList：保存会议信息
# school:学校名称
# inforList：个人信息，姓名，pid

def findArticle(articleList, conList, html, inforList):
    soup = BeautifulSoup(html, "html.parser")
    dblpperson = soup.find('dblpperson')
    name = dblpperson.attrs['name']
    pid = dblpperson.attrs['pid']
    person = soup.find('person')
    # 保存姓名
    inforList.append([name, pid])
    print(inforList)
    if person:
        if soup.findAll('article'):
            # 有论文
            print('jjjj')
            articles = soup.findAll('article')
            for article in articles:
                title_a = article.find('title')
                year_a = article.find('year')
                journal_a = article.find('journal')
                ee_a = article.find('ee')
                articleList.append([title_a, year_a, journal_a, ee_a])
        if soup.find('inproceedings'):
            # 有会议
            print('ggggg')
            inproceedings = soup.findAll('inproceedings')
            for inproceeding in inproceedings:
                title_c = inproceeding.find('title')
                year_c = inproceeding.find('year')
                crossref_c = inproceeding.find('crossref')
                ee_c = inproceeding.find('ee')
                conList.append([title_c, year_c, crossref_c, ee_c])


def printArticle(articleList, conList, inforList, num_a, num_c, filename):
    with open(filename+'_article.csv', "w", encoding='utf-8') as file:
        file.write(','.join(['name', 'pid', 'title', 'year', 'kind', 'ee']))
        file.write('\n')
        print(inforList[0])
        for i in range(num_a):
            file.write(','.join(inforList[0]))
            print(inforList[0])
            file.write(',')
            a = articleList[i]
            file.write(','.join('%s' %id for id in a))
            file.write('\n')
        for j in range(num_c):
            file.write(','.join(inforList[0]))
            print(inforList[0])
            file.write(',')
            c = conList[j]
            file.write(','.join('%s' %id for id in c))
            file.write('\n')
    file.close()



def find_article_main():
    uinfo = []
    fileName = ['D:/大学副教授名单/北京交通大学',
                'D:/大学副教授名单/北京师范大学',
                'D:/大学副教授名单/吉林大学',
                'D:/大学副教授名单/东南大学',
                'D:/大学副教授名单/同济大学',
                'D:/大学副教授名单/电子科技大学',
                'D:/大学副教授名单/北京科技大学',
                ]
    schoolName = ['Beijing Jiaotong University', 'Beijing Normal University', 'Jilin University',
                  'Southeast University', 'Tongji University', 'University of Electronic Science and Technology of China',
                  'University of Science and Technology Beijing']
    noteList = []
    urlList = []
    articleList = []
    conList = []
    inforList = []
    df_1 = pd.read_csv('D:/大学副教授名单/北京交通大学_infor.csv', encoding='gbk', error_bad_lines=False)
    '''
    for m in range(df_1.shape[0]):
        url = 'https://dblp.uni-trier.de/pid/'+df_1.iloc[m, 1]+'.xml'
        html = getXml(url)
        findArticle(articleList, conList, html, inforList)
        # articleList, conList, html, inforList
        print('kkkkkk')
        print(inforList[0])
        printArticle(articleList, conList, inforList, len(articleList), len(conList), 'D:/大学副教授名单/北京交通大学')
        # articleList, conList, inforList, num, filename
        inforList = []
    print('sssssssss')
    '''
    url = 'https://dblp.uni-trier.de/pid/'+df_1.iloc[0, 1]+'.xml'
    html = getXml(url)
    findArticle(articleList, conList, html, inforList)
    # articleList, conList, html, inforList
    print('kkkkkk')
    print(inforList[0])
    printArticle(articleList, conList, inforList, len(articleList), len(conList), 'D:/大学副教授名单/北京交通大学')
    # articleList, conList, inforList, num, filename
    inforList = []
    url = 'https://dblp.uni-trier.de/pid/'+df_1.iloc[1, 1]+'.xml'
    html = getXml(url)
    findArticle(articleList, conList, html, inforList)
    # articleList, conList, html, inforList
    print('kkkkkk')
    print(inforList[0])
    printArticle(articleList, conList, inforList, len(articleList), len(conList), 'D:/大学副教授名单/北京交通大学')
    # articleList, conList, inforList, num, filename
    inforList = []
    print('\n')
    print('\n')
    print('\n')

###################################################找人##########################################

def main():
    name_trans()
    get_pid_main()
    find_article_main()
    find_article_main()



