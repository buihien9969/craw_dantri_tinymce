"""
Script để crawl bài báo từ VnExpress và lưu vào cơ sở dữ liệu
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import mysql.connector
import datetime
import hashlib
import argparse
import random
import string
from urllib.parse import urlparse
from slugify import slugify

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

        # Giữ nguyên định dạng HTML gốc cho TinyMCE
        if content:
            # Loại bỏ các thuộc tính class, id, style không cần thiết để làm sạch HTML
            for tag in content.find_all(True):
                if tag.has_attr('class'):
                    del tag['class']
                if tag.has_attr('id'):
                    del tag['id']
                if tag.has_attr('style'):
                    del tag['style']

            # Chuyển đổi các thẻ img để giữ nguyên src và đảm bảo URL đầy đủ
            for img in content.find_all('img'):
                # Lấy src từ các thuộc tính khác nhau
                if img.has_attr('data-src'):
                    img['src'] = img['data-src']
                    del img['data-src']
                elif img.has_attr('data-original'):
                    img['src'] = img['data-original']
                    del img['data-original']

                # Đảm bảo src là URL đầy đủ
                if img.has_attr('src'):
                    src = img['src']
                    if not src.startswith('http'):
                        if src.startswith('//'):
                            img['src'] = 'https:' + src
                        elif src.startswith('/'):
                            img['src'] = 'https://vnexpress.net' + src

                # Loại bỏ các thuộc tính không cần thiết
                attrs_to_keep = ['src', 'alt']
                for attr in list(img.attrs.keys()):
                    if attr not in attrs_to_keep:
                        del img[attr]

            # Lấy HTML đã được làm sạch
            content_html = str(content)
        else:
            content_html = ""

        # Vẫn trích xuất text thuần túy cho preview
        content_text = extract_text_from_html(content_html)

        # Lấy ngày đăng
        date = soup.select_one('span.date')
        date_text = date.get_text().strip() if date else ""

        # Lấy thumbnail từ nhiều nguồn khác nhau
        thumbnail_url = ""

        # Thử lấy từ meta og:image (cách tốt nhất)
        thumbnail = soup.select_one('meta[property="og:image"]')
        if thumbnail and 'content' in thumbnail.attrs:
            thumbnail_url = thumbnail['content']

        # Nếu không có, thử lấy từ thẻ figure đầu tiên trong bài viết
        if not thumbnail_url and content:
            first_figure = content.select_one('figure img')
            if first_figure and first_figure.has_attr('src'):
                thumbnail_url = first_figure['src']
            elif first_figure and first_figure.has_attr('data-src'):
                thumbnail_url = first_figure['data-src']

        # Đảm bảo thumbnail_url là URL đầy đủ
        if thumbnail_url and not thumbnail_url.startswith('http'):
            if thumbnail_url.startswith('//'):
                thumbnail_url = 'https:' + thumbnail_url
            elif thumbnail_url.startswith('/'):
                thumbnail_url = 'https://vnexpress.net' + thumbnail_url

        # Tạo preview content (lấy 200 ký tự đầu tiên)
        preview_content = content_text[:200] + "..." if len(content_text) > 200 else content_text

        # Tạo kết quả
        result = {
            'url': url,
            'title': title_text,
            'content': content_html,
            'content_text': content_text,
            'preview_content': preview_content,
            'date': date_text,
            'thumbnail_url': thumbnail_url
        }

        return result

    except Exception as e:
        print(f"Lỗi khi crawl URL {url}: {e}")
        return None

def connect_to_database():
    """
    Kết nối đến cơ sở dữ liệu
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Thay đổi mật khẩu theo cài đặt của bạn
            database="24hnews"
        )
        return conn
    except Exception as e:
        print(f"Lỗi kết nối đến cơ sở dữ liệu: {e}")
        return None

def download_image(url, save_dir='storage/uploads'):
    """
    Tải ảnh từ URL và lưu vào thư mục

    Args:
        url (str): URL của ảnh
        save_dir (str): Thư mục lưu ảnh

    Returns:
        str: Đường dẫn tương đối của ảnh đã lưu
    """
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(save_dir, exist_ok=True)

        # Tạo tên file ngẫu nhiên
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=30))

        # Lấy phần mở rộng của file
        parsed_url = urlparse(url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1]
        if not ext:
            ext = '.jpg'  # Mặc định là jpg nếu không có phần mở rộng

        # Tạo tên file
        filename = f"{random_str}{ext}"
        filepath = os.path.join(save_dir, filename)

        # Tải ảnh
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Lưu ảnh
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Trả về đường dẫn tương đối
        return filepath

    except Exception as e:
        print(f"Lỗi khi tải ảnh từ {url}: {e}")
        return None

def process_images_in_content(content_html, download_images=True):
    """
    Xử lý ảnh trong nội dung HTML

    Args:
        content_html (str): Nội dung HTML
        download_images (bool): Có tải ảnh về không

    Returns:
        str: Nội dung HTML đã xử lý
    """
    # Tạo đối tượng BeautifulSoup
    soup = BeautifulSoup(content_html, 'html.parser')

    # Tìm tất cả các thẻ img
    img_tags = soup.find_all('img')

    # Xử lý từng thẻ img
    for img in img_tags:
        if img.has_attr('src') and img['src'].startswith('http'):
            if download_images:
                # Tải ảnh về
                local_path = download_image(img['src'])
                if local_path:
                    # Cập nhật src
                    img['src'] = f"/{local_path}"
                    print(f"Đã tải ảnh: {img['src']}")

    # Trả về nội dung HTML đã xử lý
    return str(soup)

def save_to_database(data, author_id=4, category_id=2, download_images=True):
    """
    Lưu dữ liệu vào cơ sở dữ liệu
    """
    conn = connect_to_database()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Tạo slug từ tiêu đề
        slug = slugify(data['title'])

        # Tạo code cho bài viết
        current_date = datetime.datetime.now().strftime("%d%m%y")
        random_number = hashlib.md5(data['url'].encode()).hexdigest()[:8]
        code = f"BV-{current_date}-{random_number}"

        # Kiểm tra xem bài viết đã tồn tại chưa
        cursor.execute("SELECT article_id FROM articles WHERE slug = %s", (slug,))
        existing_article = cursor.fetchone()

        if existing_article:
            print(f"Bài viết với slug '{slug}' đã tồn tại trong cơ sở dữ liệu.")
            return False

        # Xử lý ảnh trong nội dung
        content_html = process_images_in_content(data['content'], download_images)

        # Xử lý thumbnail_url
        thumbnail_url = data['thumbnail_url']
        if download_images and thumbnail_url and thumbnail_url.startswith('http'):
            local_thumbnail = download_image(thumbnail_url, save_dir='thumbnails')
            if local_thumbnail:
                thumbnail_url = local_thumbnail
                print(f"Đã tải thumbnail: {thumbnail_url}")

        # Thêm bài viết vào bảng articles
        sql = """
        INSERT INTO articles (code, title, slug, content, preview_content,
                             contains_sensitive_content, author_id, category_id,
                             thumbnail_url, status, views, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            code,
            data['title'],
            slug,
            content_html,
            data['preview_content'],
            0,  # contains_sensitive_content
            author_id,
            category_id,
            thumbnail_url,
            'pending',  # status
            0,  # views
            datetime.datetime.now(),
            datetime.datetime.now()
        )

        cursor.execute(sql, values)
        article_id = cursor.lastrowid

        # Thêm vào bảng approvals
        sql_approval = """
        INSERT INTO approvals (type, article_id, user_id, status, remarks, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values_approval = (
            'article',
            article_id,
            author_id,
            'pending',
            'Bài viết mới, chờ kiểm duyệt',
            datetime.datetime.now(),
            datetime.datetime.now()
        )

        cursor.execute(sql_approval, values_approval)

        conn.commit()
        print(f"Đã lưu bài viết '{data['title']}' vào cơ sở dữ liệu với ID: {article_id}")
        return article_id

    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu vào cơ sở dữ liệu: {e}")
        conn.rollback()
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def main():
    """
    Hàm chính
    """
    parser = argparse.ArgumentParser(description='Crawl bài báo từ VnExpress và lưu vào cơ sở dữ liệu')
    parser.add_argument('url', help='URL của bài viết cần crawl')
    parser.add_argument('--author', type=int, default=4, help='ID của tác giả (mặc định: 4)')
    parser.add_argument('--category', type=int, default=2, help='ID của danh mục (mặc định: 2)')
    parser.add_argument('--download-images', action='store_true', help='Tải ảnh về và lưu vào thư mục storage/uploads')

    args = parser.parse_args()

    print(f"Crawling URL: {args.url}")

    # Crawl dữ liệu
    data = crawl_vnexpress(args.url)

    if data:
        # Lưu vào cơ sở dữ liệu
        article_id = save_to_database(data, args.author, args.category, args.download_images)
        if article_id:
            print(f"Bạn có thể xem trước bài viết bằng cách chạy: python preview_content.py {article_id}")
    else:
        print("Không thể crawl dữ liệu từ URL này.")

if __name__ == "__main__":
    main()
