import os
import requests
import time
# import tqdm
import logging
from pymongo import MongoClient

logging.basicConfig(filename='./logs/cs-downloader.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 连接 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["arxiv"] 
collection = db["cs-paper"]

# 查询需要下载的论文
papers = collection.find({"download_mark": 0}, {"arxivId": 1, "file_path": 1})

# 下载目录
BASE_DIR = "./paper_storage"

print("downloading files. Press Ctrl + C to cancel ...")

# 下载超时时间
max_time = 10 * 60  # 最大下载时间

for paper in papers:
    arxiv_id = paper["arxivId"]
    file_path = paper["file_path"]

    # 论文 PDF 下载 URL
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # 论文本地存储路径
    full_path = os.path.join(BASE_DIR, file_path)

    # 确保目录存在
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # 检查文件是否存在，若存在则删除
    if os.path.exists(full_path):
        os.remove(full_path)

    try:
        # 下载 PDF
        response = requests.get(pdf_url, stream=True, timeout=60)
        if response.status_code == 200:
            download_flag = 1
            with open(full_path, "wb") as pdf_file:
                start_time = time.time()  # 记录开始时间
                for chunk in response.iter_content(chunk_size=1024):
                    # 检查下载总时长
                    elapsed_time = time.time() - start_time
                    if elapsed_time > max_time:  # 如果下载时间超过最大限制
                        os.remove(full_path)
                        logging.warning(f"⚠️ download timeout and skip: {arxiv_id}")
                        download_flag = 0
                        break
                    pdf_file.write(chunk)
            
            # 下载成功，更新数据库
            if download_flag:
                collection.update_one({"arxivId": arxiv_id}, {"$set": {"download_mark": 1}})
                logging.info(f"✅ download successfully : {full_path}")
        else:
            logging.warning(f"⚠️ download failed: {arxiv_id}，status: {response.status_code}")
    except requests.exceptions.Timeout:
        os.remove(full_path)
        logging.warning(f"⚠️ connection timeout and skip: {arxiv_id}")
    except Exception as e:
        logging.error(f"❌ {arxiv_id}, {e}")
    time.sleep(10)

logging.info("📂 all the papers have been downloaded ")
