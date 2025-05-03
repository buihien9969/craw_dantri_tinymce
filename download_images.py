"""
Script để tải ảnh từ URL và lưu vào thư mục storage/uploads
"""

import os
import re
import requests
import hashlib
import argparse
import mysql.connector
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random
import string

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

def process_article_images(article_id):
    """
    Xử lý ảnh trong bài viết
    
    Args:
        article_id (int): ID của bài viết
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Lấy nội dung bài viết
        cursor.execute("SELECT content, thumbnail_url FROM articles WHERE article_id = %s", (article_id,))
        article = cursor.fetchone()
        
        if not article:
            print(f"Không tìm thấy bài viết với ID: {article_id}")
            return False
        
        content = article['content']
        thumbnail_url = article['thumbnail_url']
        
        # Tạo đối tượng BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Tìm tất cả các thẻ img
        img_tags = soup.find_all('img')
        
        # Xử lý từng thẻ img
        for img in img_tags:
            if img.has_attr('src') and img['src'].startswith('http'):
                # Tải ảnh về
                local_path = download_image(img['src'])
                if local_path:
                    # Cập nhật src
                    img['src'] = f"/{local_path}"
                    print(f"Đã tải ảnh: {img['src']}")
        
        # Xử lý thumbnail_url
        if thumbnail_url and thumbnail_url.startswith('http'):
            local_thumbnail = download_image(thumbnail_url, save_dir='thumbnails')
            if local_thumbnail:
                thumbnail_url = local_thumbnail
                print(f"Đã tải thumbnail: {thumbnail_url}")
        
        # Cập nhật nội dung bài viết
        content_html = str(soup)
        cursor.execute("UPDATE articles SET content = %s, thumbnail_url = %s WHERE article_id = %s", 
                      (content_html, thumbnail_url, article_id))
        
        conn.commit()
        print(f"Đã cập nhật bài viết với ID: {article_id}")
        return True
    
    except Exception as e:
        print(f"Lỗi khi xử lý ảnh trong bài viết: {e}")
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
    parser = argparse.ArgumentParser(description='Tải ảnh từ URL và lưu vào thư mục storage/uploads')
    parser.add_argument('article_id', type=int, help='ID của bài viết cần xử lý')
    
    args = parser.parse_args()
    
    print(f"Đang xử lý ảnh trong bài viết với ID: {args.article_id}")
    
    # Xử lý ảnh trong bài viết
    if process_article_images(args.article_id):
        print("Xử lý ảnh thành công!")
    else:
        print("Xử lý ảnh thất bại!")

if __name__ == "__main__":
    main()
