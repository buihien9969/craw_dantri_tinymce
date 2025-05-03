"""
Script đơn giản để crawl bài báo từ VnExpress
"""

import re
import os
import sys

def extract_text_from_html(html):
    """
    Trích xuất text từ HTML, loại bỏ các thẻ HTML
    """
    # Loại bỏ các thẻ script và style
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)
    
    # Loại bỏ các thẻ HTML còn lại
    text = re.sub(r'<.*?>', ' ', html)
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def crawl_vnexpress(url, html_content):
    """
    Crawl bài viết từ VnExpress
    """
    try:
        # Tìm tiêu đề
        title_match = re.search(r'<h1[^>]*class="title-detail"[^>]*>(.*?)</h1>', html_content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        
        # Tìm nội dung
        content_match = re.search(r'<article[^>]*class="fck_detail[^"]*"[^>]*>(.*?)</article>', html_content, re.DOTALL)
        content_html = content_match.group(1) if content_match else ""
        content_text = extract_text_from_html(content_html)
        
        # Tìm ngày đăng
        date_match = re.search(r'<span[^>]*class="date"[^>]*>(.*?)</span>', html_content, re.DOTALL)
        date = date_match.group(1).strip() if date_match else ""
        
        # Tạo kết quả
        result = {
            'url': url,
            'title': title,
            'content': content_text,
            'date': date
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
        
        # Lưu nội dung vào file text
        with open(f'crawled_data/{filename}', 'w', encoding='utf-8') as f:
            f.write(f"Tiêu đề: {data['title']}\n\n")
            f.write(f"Ngày đăng: {data['date']}\n\n")
            f.write(f"URL: {data['url']}\n\n")
            f.write(f"Nội dung:\n{data['content']}")
        
        print(f"Đã lưu nội dung vào file crawled_data/{filename}")
    
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu: {e}")

def main():
    """
    Hàm chính
    """
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Crawling URL: {url}")
        
        # Đọc nội dung HTML từ file
        html_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if html_file and os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Crawl dữ liệu
            data = crawl_vnexpress(url, html_content)
            
            if data:
                # Tạo tên file từ URL
                filename = url.split('/')[-1].replace('.html', '.txt')
                
                # Lưu dữ liệu
                save_to_file(data, filename)
            else:
                print("Không thể crawl dữ liệu từ URL này.")
        else:
            print("File HTML không tồn tại hoặc không được cung cấp.")
    else:
        print("Vui lòng cung cấp URL cần crawl và đường dẫn đến file HTML.")
        print("Ví dụ: python vnexpress_crawler.py https://vnexpress.net/nguoi-my-can-kiem-it-nhat-114-000-usd-moi-nam-de-mua-duoc-nha-4881179.html html_file.html")

if __name__ == "__main__":
    main()
