# cs-scrapper

## 说明

### 主要功能

爬取arxiv某方面相关的论文信息爬取到mongoDB数据库中，包括arXivId、标题、摘要、提交日期等字段

### 细节

- download_mark说明: 0为未下载 1为下载完成 2为没有pdf 3为文件名过长
- 需指定爬取的论文主题，以advanced search中的主题为标准
- 脚本实现两个任务，首先爬取昨日的论文信息，再从存档点向后爬取论文信息(如2025-02-17，2020-02-16...)
- 查看日志:已实现简易日志，可查看存入论文信息数量以及task2执行到的时间点

## 使用方式

### 准备工作

- 修改url以指定论文主题，默认为cs即计算机科学相关
- 部署mongoDB服务器，并在scrapper.py中硬编码mongoDB配置，(ip:port，数据库名和表名)，若数据库不在内网中，因安全性问题可自行设置账户密码
- 安装库：

```bash
pip install -r requirements.txt
```

- 若脚本在Linux操作系统上，使用脚本运行，否则直接用python命令运行scrapper-main.py 和 download.py，或者自己编写批处理文件

```bash
./run_scrapper.sh
```

### TODO

- 项目目录结构、代码风格持续优化
- 持续测试修复bug
- *批量下载pdf脚本