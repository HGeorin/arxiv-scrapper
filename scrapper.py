# 爬取时间区间[from_date, to_date)的论文信息

import os
import re
import logging
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

# log配置
logging.basicConfig(filename='./logs/cs-scrapper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 连接到启用认证的 MongoDB
username = 'vector4d'
pwd ='4dv999'
ip = 'e102.extrotec.com'
port = '32217'
client = MongoClient(
    f'mongodb://{username}:{pwd}@{ip}:{port}/?authSource=admin'
)

# 选择数据库和集合
db = client['arxiv']
collection = db['cs-paper']

# 获取第i轮的url，round = 0, 1, 2...
def get_base_url(round, from_date, to_date):
    
    start = round * 200
    return f"https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-computer_science=y&classification-physics_archives=all&classification-include_cross_list=include&date-year=&date-filter_by=date_range&date-from_date={from_date}&date-to_date={to_date}&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first&start={start}"

# 假设base_url是页面的URL
def fetch_papers(base_url):
    url = f"{base_url}"
    response = requests.get(url, timeout = 10 * 60)
    if response.status_code != 200:
        logging.error(f"Failed to fetch {url}")
        return None

    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 检查是否有找到论文
    if soup.find('h1', class_='title') and 'Sorry, your query returned no results' in soup.find('h1', class_='title').text:
        return -1
    
    # 找到所有包含论文信息的<li>元素
    papers = soup.find_all('li', class_='arxiv-result')
    
    all_papers_data = []

    # 遍历所有论文条目,每个字段都需要写一个对应的解析方法
    for paper in papers:
        paper_data = get_paper_data(paper)
        if paper_data is not None:
            all_papers_data.append(get_paper_data(paper))

    return all_papers_data

def get_paper_data(paper):
    paper_data = {}

    # **常规字段**
    # arxivId 用于后续下载PDF
    arxiv_link = paper.find('p', class_='list-title').find('a')['href']
    arxiv_id = arxiv_link.split('/')[-1]
    # 查询 MongoDB 中是否存在该 arxivId
    existing_paper = collection.find_one({'arxivId': arxiv_id})
    # 如果 arxivId 存在，跳过该paper
    if existing_paper is not None:
        return None
    paper_data['arxivId'] = arxiv_id
        
    # mainTheme, minorTheme 主副标签，存在多个副标签则用逗号连接
    tags = paper.find('div', class_='tags is-inline-block').find_all('span', class_='tag')
    themes = [tag.get_text() for tag in tags]  # 获取每个主题标签的文本内容
    paper_data['main_theme'] = themes[0] if themes else ''  # 第一个主题为 mainTheme
    paper_data['minor_theme'] = ', '.join(themes[1:]) if len(themes) > 1 else ''  # 剩余的主题为 minorTheme，多个主题用逗号分隔
    
    # title 论文标题
    title = paper.find('p', class_='title').get_text(strip=True)
    paper_data['title'] = title
    
    # authors 论文作者，存在多个作者时使用英文逗号连接
    authors = paper.find('p', class_='authors').find_all('a')
    author_names = [author.get_text(strip=True) for author in authors]
    paper_data['authors'] = ', '.join(author_names)  # 作者用逗号连接
    
    # abstract 论文摘要，选取完整摘要
    abstract = paper.find('span', class_='abstract-full').get_text(strip=True)
    paper_data['abstract'] = abstract
    
    # time相关字段
    # 获取<p>标签的文本内容
    time_info = paper.find('p', class_='is-size-7')
    submit_time = ''

    if time_info:
    # 使用get_text()来提取纯文本，strip去除前后的空格
        time_info_text = time_info.get_text(strip=True)
    else:
        time_info_text = ""  # 如果找不到p标签，设为空字符串

    # 确保time_info_text是一个字符串，并进行日期匹配
    if isinstance(time_info_text, str) and time_info_text:
    # 提取Submitted的日期（例如 "19 February, 2025"）
        submitted_match = re.search(r'Submitted\s*(\d{1,2})\s*(\w+),\s*(\d{4})', time_info_text)
    if submitted_match:
        day = submitted_match.group(1)
        month = submitted_match.group(2)
        year = submitted_match.group(3)
    
        # 创建完整的日期字符串
        submitted_date = f"{day} {month} {year}"
        submitted_date_obj = datetime.strptime(submitted_date, '%d %B %Y')
        submit_time = submitted_date_obj.strftime('%Y-%m-%d')
        paper_data['submitted_time'] = submit_time

    # 提取originally announced的日期（例如 "February 2025"）
    originally_announced_match = re.search(r'originally announced\s*(\w+\s*\d{4})', time_info_text)
    if originally_announced_match:
        announced_date = originally_announced_match.group(1)
        announced_date_obj = datetime.strptime(announced_date, '%B %Y')
        paper_data['announced_time'] = announced_date_obj.strftime('%Y-%m')
    else:
        logging.warning(f"time_info_text {time_info_text} is not a valid string or is empty.")

    # 获取所有评论字段
    comments_section = paper.find_all('p', class_='comments is-size-7')
    # 提取期刊参考信息
    journal_ref = None
    for comment in comments_section:
        # 检查是否包含 "Journal ref:"，然后提取期刊信息
        if 'Journal ref:' in comment.get_text():
            journal_ref = comment.get_text(strip=True).replace('Journal ref:', '').strip()
            break  # 找到期刊信息后跳出循环

        # 提取注释信息（如果有的话）
    comments = None
    for comment in comments_section:
        if 'Comments:' in comment.get_text() and 'Journal ref:' not in comment.get_text():
            comments = comment.get_text(strip=True).replace('Comments:', '').strip()
        
    paper_data['journal_ref'] = journal_ref
    paper_data['comments'] = comments
        
    # **自添加字段**
    # DownloadMark 标志位，检测是否已经下载，用于后续批量下载PDF
    paper_data['download_mark'] = 0
    # FilePath 文件存储路径，用于后续批量下载PDF并分类
    file_path = construct_file_path(submit_time, paper_data['main_theme'], paper_data['arxivId'], paper_data['title'])
    paper_data['file_path'] = file_path

    return paper_data

# 构造文件路径
def construct_file_path(submit_time, main_theme, arxiv_id, title):
    # 提取年、月、日
    year = submit_time[:4]
    month = submit_time[5:7]
    day = submit_time[8:10]

    # 替换title中的非法字符
    title = re.sub(r'[\\/:*?"<>|]', '__', title)

    # 构建文件路径
    file_path = os.path.join(main_theme, year, month, day, f"{arxiv_id}_{title}")
    file_path = file_path + '.pdf'

    return file_path

# 将数据存储到MongoDB的函数
def save_to_mongo(papers_data):
    if papers_data:
        # 使用 insert_many() 批量插入多个文档
        collection.insert_many(papers_data)
        logging.info(f"{len(papers_data)} papers saved to MongoDB")

# 主功能函数
def scrapper(from_date, to_date):
    # 从 round = 0 开始，直到找不到论文信息
    round = 0
    while(1):
        # !每次fetch_papers都会进行一次请求，故需要停顿防止被反爬虫制裁！
        try:
            papers_data = fetch_papers(get_base_url(round, from_date, to_date))
        except requests.exceptions.Timeout:
            time.sleep(10)
            logging.warning("request timeout, retrying")
            continue
        # 该天论文爬取完毕，结束任务
        if papers_data == -1:
            return
        save_to_mongo(papers_data)
        round += 1
        time.sleep(10)