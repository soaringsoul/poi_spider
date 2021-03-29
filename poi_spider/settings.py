

BOT_NAME = 'poi_spider'
# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'poi_spider.pipelines.BaidumapwebapispierPipeline': 300,
}
SPIDER_MODULES = ['poi_spider.spiders']
NEWSPIDER_MODULE = 'poi_spider.spiders'

LOG_LEVEL = 'ERROR'

LOG_FILE = 'log.txt'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
DOWNLOAD_TIMEOUT = 180
