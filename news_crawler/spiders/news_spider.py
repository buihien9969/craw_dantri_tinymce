import scrapy
import json
import re
from news_crawler.items import NewsItem
from news_crawler.connector import get_all_websites, get_categories, get_contents

class NewsSpider(scrapy.Spider):
    name = "news"

    def start_requests(self):
        # Nếu có URL cụ thể được truyền vào, ưu tiên crawl URL đó
        if hasattr(self, 'start_url') and self.start_url:
            # Xác định website_id dựa trên domain của URL
            domain = self.extract_domain(self.start_url)
            website_id = self.get_website_id_by_domain(domain)

            if website_id:
                self.logger.info(f"Crawling specific URL: {self.start_url}")
                yield scrapy.Request(
                    url=self.start_url,
                    callback=self.parse,
                    meta={"website_id": website_id, "domain": domain}
                )
            else:
                self.logger.error(f"Không tìm thấy cấu hình cho domain: {domain}")
        else:
            # Crawl tất cả các website trong cơ sở dữ liệu
            list_websites = get_all_websites()
            for website in list_websites:
                domain = website[1]  # Lấy domain của website: https://vietnamnet.vn
                categories = json.loads(website[2])  # Lấy danh sách danh mục của website: /thoi-su, /chinh-tri

                for category in categories:
                    link = domain + category
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_links,
                        meta={"website_id": website[0], "domain": domain}
                    )

    def extract_domain(self, url):
        # Trích xuất domain từ URL
        match = re.match(r'(https?://[^/]+)', url)
        if match:
            return match.group(1)
        return None

    def get_website_id_by_domain(self, domain):
        # Lấy website_id dựa trên domain
        websites = get_all_websites()
        for website in websites:
            if website[1] == domain:
                return website[0]
        return None

    def parse_links(self, response):
        result = set()

        x_path_categories = get_categories(response.meta.get("website_id"))
        for x_path_category in x_path_categories:
            # Lấy tất cả thẻ a, sau đó lấy tất cả thuộc tính href chứa link của bài viết
            x_path = x_path_category + "//a/@href"
            list_href = response.xpath(x_path).extract()

            for href in list_href:
                # Xử lý URL
                if href.startswith('http'):
                    # URL đầy đủ
                    result.add(href)
                elif href.startswith('/'):
                    # URL tương đối
                    result.add(response.meta.get("domain") + href)
                else:
                    # URL không hợp lệ
                    continue

        for item in result:
            yield scrapy.Request(
                url=item,
                callback=self.parse,
                meta={"website_id": response.meta.get("website_id")}
            )

    def parse(self, response):
        website_id = response.meta.get("website_id")
        posts = get_contents(website_id)

        for post in posts:
            # Lấy tiêu đề
            title_xpath = post["title"]
            title = response.xpath(title_xpath + "/text()").get()
            if not title:
                title = response.xpath(title_xpath + "//text()").get()

            # Lấy nội dung
            content_xpath = post["content"]
            content_html = response.xpath(content_xpath).get()

            # Lấy ngày đăng
            date_xpath = post["date"]
            date = response.xpath(date_xpath + "/text()").get()
            if not date:
                date = response.xpath(date_xpath + "//text()").get()

            # Xử lý nội dung HTML để lấy text
            if content_html:
                # Loại bỏ các thẻ HTML để lấy text thuần túy
                content_text = self.extract_text_from_html(content_html)
            else:
                content_text = ""

            # Chuẩn hóa dữ liệu
            title = self.normalize(title)
            content_text = self.normalize(content_text)
            date = self.normalize(date)

            # Tạo item
            news_item = NewsItem()
            news_item['title'] = title
            news_item['content'] = content_text
            news_item['date'] = date
            news_item['url'] = response.url

            self.logger.info(f"Đã crawl bài viết: {title}")
            yield news_item

    def extract_text_from_html(self, html):
        # Loại bỏ các thẻ script và style
        html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)

        # Loại bỏ các thẻ HTML còn lại
        text = re.sub(r'<.*?>', ' ', html)

        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def normalize(self, text):
        if text is None:
            return ""
        return text.strip()
