import os
import requests
import time
# import tqdm
import logging
from pymongo import MongoClient

logging.basicConfig(filename='./logs/downloader.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 连接 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["arxiv"] 
collection = db["cs-paper"]

# 查询需要下载的论文
papers = collection.find({"download_mark": 0}, {"arxivId": 1, "file_path": 1})

# 下载目录
BASE_DIR = "./paper_storage"

print("downloading files. Press Ctrl + C to cancel ...")

for paper in papers:
    arxiv_id = paper["arxivId"]
    file_path = paper["file_path"]

    # 论文 PDF 下载 URL
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # 论文本地存储路径
    full_path = os.path.join(BASE_DIR, file_path)

    # 确保目录存在
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    try:
        # 下载 PDF
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            with open(full_path, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=1024):
                    pdf_file.write(chunk)
            
            # 下载成功，更新数据库
            collection.update_one({"arxivId": arxiv_id}, {"$set": {"download_mark": 1}})
            logging.info(f"✅ download successfully : {full_path}")
        else:
            logging.warning(f"❌ download failed: {arxiv_id}，status: {response.status_code}")
    except Exception as e:
        logging.info(f"⚠️ Error: {arxiv_id}, {e}")
    time.sleep(10)

logging.info("📂 all the papers have been downloaded ")
