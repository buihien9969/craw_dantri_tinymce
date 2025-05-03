BOT_NAME = "news_crawler"

SPIDER_MODULES = ["news_crawler.spiders"]
NEWSPIDER_MODULE = "news_crawler.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 1

# Enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#    "news_crawler.middlewares.NewsCrawlerSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# DOWNLOADER_MIDDLEWARES = {
#    "news_crawler.middlewares.NewsCrawlerDownloaderMiddleware": 543,
# }

# Configure item pipelines
ITEM_PIPELINES = {
   "news_crawler.pipelines.NewsCrawlerPipeline": 300,
   "news_crawler.pipelines.JsonWriterPipeline": 800,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
