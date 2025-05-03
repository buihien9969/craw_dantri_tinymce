from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from news_crawler.spiders.news_spider import NewsSpider

def run_crawler():
    # Lấy cài đặt từ settings.py
    settings = get_project_settings()
    
    # Tạo process crawler
    process = CrawlerProcess(settings)
    
    # Thêm spider vào process
    process.crawl(NewsSpider)
    
    # Bắt đầu crawl
    process.start()

if __name__ == "__main__":
    run_crawler()
