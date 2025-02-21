import os
import sys
import logging
from datetime import datetime, timedelta
import schedule
import time
from scrapper import scrapper

logging.basicConfig(filename='cs-scrapper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# 进度点文件路径
progress_file = 'progress.txt'

# 创建进度点文件，如果文件不存在就写入昨日日期
def get_saved_date():
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as file:
            saved_date = file.read().strip()
            return saved_date
    else:
        # 获取昨日日期
        yesterday = datetime.now() - timedelta(days=1)
        saved_date = yesterday.strftime('%Y-%m-%d')
        with open(progress_file, 'w') as file:
            file.write(saved_date)
        return saved_date

# 定时任务：每天2点运行
def scheduled_task():
    logging.info("starting scheduled scrapper task")
    # 设置从日期和到日期（你可以根据需求调整这个范围）
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 任务一：爬取昨日论文
    logging.info("[task 1] : getting paper information of yesterday...")
    scrapper(yesterday, today)

    # 任务二：从存档点向前爬取论文
    logging.info("[task 2] : Scrape paper information from the archive point forward...")
    # 获取保存的进度点日期
    to_date = get_saved_date()
    # 从后向前逐天爬取
    while True:
        to_date_dt = datetime.strptime(to_date, '%Y-%m-%d')
        from_date_dt = to_date_dt - timedelta(days=1)
        from_date = from_date_dt.strftime('%Y-%m-%d')
        # 更新存档点
        scrapper(from_date, to_date)
        logging.info(f"{from_date} task completed")
        update_progress_file(from_date)
        to_date = from_date
        # 控制访问频率
        time.sleep(15)

# 更新进度点文件为新的日期
def update_progress_file(new_date):
    with open(progress_file, 'w') as file:
        file.write(new_date)

# 停止脚本执行的任务
def stop_task():
    logging.info("stopping scheduled task...")
    sys.exit()
# 仅在脚本直接执行时调用 main() 函数
if __name__ == "__main__":
    # # 设置每天的定时任务：下午2点执行
    # schedule.every().day.at("14:00").do(scheduled_task)
    # # 设置每天的定时任务：下午1点停止执行
    # schedule.every().day.at("13:00").do(stop_task)

    # # 持续运行定时任务
    # while True:
    #     schedule.run_pending()  # 执行待执行的任务
    #     time.sleep(10)  # 检查一次
    
    # 调试
    scheduled_task()