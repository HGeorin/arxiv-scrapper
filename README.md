# arxiv-scrapper

A python scrapper in order to get information for papers, and store the information into mongoDB

0 14 * * * cd /home/user/hgeorin/code/arxiv-scrapper/cs-scrapper && /usr/local/bin/gunicorn -w 4 scrapper-main:scheduled_task >> /home/user/hgeorin/code/arxiv-scrapper/cs-scrapper/logs/inf-scrapper.log 2>&1
