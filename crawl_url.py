from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from news_crawler.spiders.news_spider import NewsSpider

def crawl_specific_url(url):
    """
    Crawl một URL cụ thể
    
    Args:
        url (str): URL của bài viết cần crawl
    """
    # Lấy cài đặt từ settings.py
    settings = get_project_settings()
    
    # Tạo process crawler
    process = CrawlerProcess(settings)
    
    # Thêm spider vào process với tham số start_url
    process.crawl(NewsSpider, start_url=url)
    
    # Bắt đầu crawl
    process.start()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Crawling URL: {url}")
        crawl_specific_url(url)
    else:
        print("Vui lòng cung cấp URL cần crawl.")
        print("Ví dụ: python crawl_url.py https://vnexpress.net/nguoi-my-can-kiem-it-nhat-114-000-usd-moi-nam-de-mua-duoc-nha-4881179.html")
