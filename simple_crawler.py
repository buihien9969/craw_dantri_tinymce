import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import os

def extract_text_from_html(html):
    """
    Trích xuất text từ HTML, loại bỏ các thẻ HTML
    """
    # Loại bỏ các thẻ script và style
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)
    
    # Tạo đối tượng BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Lấy text
    text = soup.get_text(separator=' ')
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def crawl_vnexpress(url):
    """
    Crawl bài viết từ VnExpress
    """
    try:
        # Gửi request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy tiêu đề
        title = soup.select_one('h1.title-detail')
        title_text = title.get_text().strip() if title else ""
        
        # Lấy nội dung
        content = soup.select_one('article.fck_detail')
        content_html = str(content) if content else ""
        content_text = extract_text_from_html(content_html)
        
        # Lấy ngày đăng
        date = soup.select_one('span.date')
        date_text = date.get_text().strip() if date else ""
        
        # Tạo kết quả
        result = {
            'url': url,
            'title': title_text,
            'content': content_text,
            'date': date_text
        }
        
        return result
    
    except Exception as e:
        print(f"Lỗi khi crawl URL {url}: {e}")
        return None

def save_to_file(data, filename):
    """
    Lưu dữ liệu vào file
    """
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs('crawled_data', exist_ok=True)
        
        # Lưu dữ liệu vào file JSON
        with open(f'crawled_data/{filename}', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Đã lưu dữ liệu vào file crawled_data/{filename}")
        
        # Lưu nội dung vào file text
        with open(f'crawled_data/{filename.replace(".json", ".txt")}', 'w', encoding='utf-8') as f:
            f.write(f"Tiêu đề: {data['title']}\n\n")
            f.write(f"Ngày đăng: {data['date']}\n\n")
            f.write(f"URL: {data['url']}\n\n")
            f.write(f"Nội dung:\n{data['content']}")
        
        print(f"Đã lưu nội dung vào file crawled_data/{filename.replace('.json', '.txt')}")
    
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu: {e}")

def main():
    """
    Hàm chính
    """
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Crawling URL: {url}")
        
        # Crawl dữ liệu
        data = crawl_vnexpress(url)
        
        if data:
            # Tạo tên file từ URL
            filename = url.split('/')[-1].replace('.html', '.json')
            
            # Lưu dữ liệu
            save_to_file(data, filename)
        else:
            print("Không thể crawl dữ liệu từ URL này.")
    else:
        print("Vui lòng cung cấp URL cần crawl.")
        print("Ví dụ: python simple_crawler.py https://vnexpress.net/nguoi-my-can-kiem-it-nhat-114-000-usd-moi-nam-de-mua-duoc-nha-4881179.html")

if __name__ == "__main__":
    main()
