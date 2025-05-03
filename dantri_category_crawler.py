"""
Script để crawl nhiều bài báo từ một danh mục của Dân Trí và lưu vào cơ sở dữ liệu
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import time
import argparse
from dantri_to_db import crawl_dantri, save_to_database, save_to_file

def get_article_links_from_category(category_url, limit=10):
    """
    Lấy danh sách các link bài viết từ trang danh mục
    
    Args:
        category_url (str): URL của trang danh mục
        limit (int): Số lượng bài viết tối đa cần lấy
        
    Returns:
        list: Danh sách các URL bài viết
    """
    try:
        # Gửi request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(category_url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các link bài viết
        article_links = []
        
        # Tìm trong các thẻ article có class article-item
        articles = soup.select('article.article-item')
        for article in articles:
            link_tag = article.select_one('a.article-title')
            if link_tag and 'href' in link_tag.attrs:
                href = link_tag['href']
                if href.startswith('https://dantri.com.vn'):
                    article_links.append(href)
                elif href.startswith('/'):
                    article_links.append(f"https://dantri.com.vn{href}")
        
        # Giới hạn số lượng bài viết
        return article_links[:limit]
    
    except Exception as e:
        print(f"Lỗi khi lấy danh sách bài viết từ {category_url}: {e}")
        return []

def main():
    """
    Hàm chính
    """
    parser = argparse.ArgumentParser(description='Crawl nhiều bài báo từ một danh mục của Dân Trí và lưu vào cơ sở dữ liệu')
    parser.add_argument('category_url', help='URL của trang danh mục cần crawl')
    parser.add_argument('--limit', type=int, default=10, help='Số lượng bài viết tối đa cần crawl (mặc định: 10)')
    parser.add_argument('--author', type=int, default=4, help='ID của tác giả (mặc định: 4)')
    parser.add_argument('--category', type=int, default=2, help='ID của danh mục (mặc định: 2)')
    parser.add_argument('--delay', type=int, default=2, help='Thời gian chờ giữa các lần crawl (giây) (mặc định: 2)')
    parser.add_argument('--save-file', action='store_true', help='Lưu bài viết vào file')
    parser.add_argument('--save-db', action='store_true', help='Lưu bài viết vào cơ sở dữ liệu')
    
    args = parser.parse_args()
    
    # Mặc định lưu vào cả file và database nếu không có tham số nào được chỉ định
    if not args.save_file and not args.save_db:
        args.save_file = True
        args.save_db = True
    
    print(f"Crawling danh mục: {args.category_url}")
    print(f"Giới hạn: {args.limit} bài viết")
    
    # Lấy danh sách các link bài viết
    article_links = get_article_links_from_category(args.category_url, args.limit)
    
    if not article_links:
        print("Không tìm thấy bài viết nào trong danh mục này.")
        return
    
    print(f"Đã tìm thấy {len(article_links)} bài viết.")
    
    # Crawl từng bài viết
    success_count = 0
    article_ids = []
    
    for i, url in enumerate(article_links):
        print(f"\nCrawling bài viết {i+1}/{len(article_links)}: {url}")
        
        # Crawl dữ liệu
        data = crawl_dantri(url)
        
        if data:
            # Lưu vào file nếu được yêu cầu
            if args.save_file:
                save_to_file(data)
            
            # Lưu vào cơ sở dữ liệu nếu được yêu cầu
            if args.save_db:
                article_id = save_to_database(data, args.author, args.category)
                if article_id:
                    success_count += 1
                    article_ids.append(article_id)
        
        # Chờ một khoảng thời gian trước khi crawl bài tiếp theo
        if i < len(article_links) - 1:
            print(f"Chờ {args.delay} giây trước khi crawl bài tiếp theo...")
            time.sleep(args.delay)
    
    print(f"\nĐã hoàn thành! Crawl thành công {success_count}/{len(article_links)} bài viết.")
    
    if args.save_db and article_ids:
        print("\nDanh sách ID của các bài viết đã lưu vào cơ sở dữ liệu:")
        for article_id in article_ids:
            print(f"- {article_id}")
        print("\nBạn có thể xem trước bài viết bằng cách chạy: python preview_content.py [article_id]")

if __name__ == "__main__":
    main()
