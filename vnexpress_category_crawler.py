"""
Script để crawl nhiều bài báo từ một danh mục của VnExpress và lưu vào cơ sở dữ liệu
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import time
import argparse
from vnexpress_to_db import crawl_vnexpress, save_to_database

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
        
        # Tìm trong các thẻ article có class item-news
        articles = soup.select('article.item-news')
        for article in articles:
            link_tag = article.select_one('h3.title-news > a')
            if link_tag and 'href' in link_tag.attrs:
                href = link_tag['href']
                if href.startswith('https://vnexpress.net'):
                    article_links.append(href)
                elif href.startswith('/'):
                    article_links.append(f"https://vnexpress.net{href}")
        
        # Giới hạn số lượng bài viết
        return article_links[:limit]
    
    except Exception as e:
        print(f"Lỗi khi lấy danh sách bài viết từ {category_url}: {e}")
        return []

def main():
    """
    Hàm chính
    """
    parser = argparse.ArgumentParser(description='Crawl nhiều bài báo từ một danh mục của VnExpress và lưu vào cơ sở dữ liệu')
    parser.add_argument('category_url', help='URL của trang danh mục cần crawl')
    parser.add_argument('--limit', type=int, default=10, help='Số lượng bài viết tối đa cần crawl (mặc định: 10)')
    parser.add_argument('--author', type=int, default=4, help='ID của tác giả (mặc định: 4)')
    parser.add_argument('--category', type=int, default=2, help='ID của danh mục (mặc định: 2)')
    parser.add_argument('--delay', type=int, default=2, help='Thời gian chờ giữa các lần crawl (giây) (mặc định: 2)')
    
    args = parser.parse_args()
    
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
    for i, url in enumerate(article_links):
        print(f"\nCrawling bài viết {i+1}/{len(article_links)}: {url}")
        
        # Crawl dữ liệu
        data = crawl_vnexpress(url)
        
        if data:
            # Lưu vào cơ sở dữ liệu
            if save_to_database(data, args.author, args.category):
                success_count += 1
        
        # Chờ một khoảng thời gian trước khi crawl bài tiếp theo
        if i < len(article_links) - 1:
            print(f"Chờ {args.delay} giây trước khi crawl bài tiếp theo...")
            time.sleep(args.delay)
    
    print(f"\nĐã hoàn thành! Crawl thành công {success_count}/{len(article_links)} bài viết.")

if __name__ == "__main__":
    main()
