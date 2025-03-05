# cs-scrapper

## 说明

### 主要功能

1.爬取arxiv某方面相关的论文信息爬取到mongoDB数据库中，包括arXivId、标题、摘要、提交日期等字段

2.批量下载pdf文件至本地

两个功能分开运行，其中功能2(下载pdf)依赖于功能1的工作

### 细节

- download_mark说明: 0为未下载 1为下载完成 2为没有pdf 3为文件名过长
- 需指定爬取的论文主题，以advanced search中的主题为标准
- 脚本实现两个任务，首先爬取昨日的论文信息，再从存档点向后爬取论文信息(如2025-02-17，2020-02-16...)
- 查看日志:已实现简易日志，可查看存入论文信息数量以及task2执行到的时间点

## 使用方式

### 准备工作

- 需在根目录创建/logs文件夹，否则会报错(懒得写创建文件夹了，可能以后会带着补上)
- 修改url以指定论文主题，默认为cs即计算机科学相关
- 部署mongoDB服务器，并在scrapper.py中硬编码mongoDB配置，(ip:port，数据库名和表名)，若数据库不在内网中，因安全性问题可自行设置账户密码
- 若无法访问arxiv.org，请配置proxies_，否则将request.get()中的proxies=proxies_删去
- downloader默认下载cs.CV的论文，可自行修改查询条件
- 安装库：

```bash
pip install -r requirements.txt
```

- 建议直接运行scrapper-main.py和downloader.py，两个sh文件未经过测试
- 若脚本在Linux操作系统上，可使用两个sh文件运行，否则直接用python命令运行scrapper-main.py 和 download.py，或者自己编写批处理文件
