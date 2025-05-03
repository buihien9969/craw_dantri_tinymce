"""
Script để crawl bài báo từ Dân Trí và lưu vào cơ sở dữ liệu
"""

import requests
from bs4 import BeautifulSoup
import re
import os
import mysql.connector
import datetime
import hashlib
import argparse
import random
import string
import json
from urllib.parse import urlparse
from slugify import slugify
from datetime import timedelta

def generate_random_datetime(months=12, target_date=None):
    """
    Tạo ngày giờ ngẫu nhiên trong khoảng từ số tháng trước đến target_date

    Args:
        months (int): Số tháng trước target_date để bắt đầu khoảng thời gian
        target_date (datetime, optional): Ngày đích để tính khoảng thời gian. Mặc định là tháng 5/2025

    Returns:
        datetime: Ngày giờ ngẫu nhiên
    """
    # Nếu không có target_date, sử dụng tháng 5/2025
    if target_date is None:
        target_date = datetime.datetime(2025, 5, 15, 12, 0, 0)  # 15/5/2025 12:00:00

    # Tính thời gian bắt đầu (12 tháng trước target_date)
    start_date = target_date - timedelta(days=30 * months)

    # Tính số giây giữa hai thời điểm
    time_delta = (target_date - start_date).total_seconds()

    # Tạo một thời điểm ngẫu nhiên
    random_seconds = random.randint(0, int(time_delta))
    random_datetime = start_date + timedelta(seconds=random_seconds)

    return random_datetime

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

def extract_category_from_url(url):
    """
    Trích xuất thông tin danh mục từ URL của Dân Trí

    Args:
        url (str): URL của bài viết

    Returns:
        tuple: (category_name, subcategory_name)
    """
    try:
        # Phân tích URL
        parsed_url = urlparse(url)
        path = parsed_url.path

        # Loại bỏ phần cuối của URL (slug của bài viết và ID)
        path_parts = path.strip('/').split('/')

        # URL của Dân Trí có thể có dạng:
        # 1. /category/title-id.htm (ví dụ: /giao-duc/title-id.htm)
        # 2. /category/subcategory/title-id.htm (ví dụ: /bat-dong-san/du-an/title-id.htm)

        category_slug = None
        subcategory_slug = None

        if len(path_parts) >= 1:
            category_slug = path_parts[0]

            # Kiểm tra xem có subcategory không
            if len(path_parts) >= 2 and not path_parts[1].endswith('.htm'):
                subcategory_slug = path_parts[1]

        # Chuyển đổi slug thành tên danh mục
        category_mapping = {
            'giao-duc': 'Giáo dục',
            'the-gioi': 'Thế giới',
            'kinh-doanh': 'Kinh doanh',
            'bat-dong-san': 'Bất động sản',
            'the-thao': 'Thể thao',
            'lao-dong-viec-lam': 'Lao động - Việc làm',
            'suc-khoe': 'Sức khỏe',
            'van-hoa': 'Văn hóa',
            'giai-tri': 'Giải trí',
            'o-to-xe-may': 'Ô tô - Xe máy',
            'suc-manh-so': 'Sức mạnh số',
            'du-lich': 'Du lịch',
            'doi-song': 'Đời sống',
            'tinh-yeu-gioi-tinh': 'Tình yêu - Giới tính',
            'khoa-hoc-cong-nghe': 'Khoa học - Công nghệ',
            'xa-hoi': 'Xã hội'
        }

        # Mapping cho subcategory
        subcategory_mapping = {
            'du-an': 'Dự án',
            'thi-truong': 'Thị trường',
            'nha-dat': 'Nhà đất',
            'khong-gian-song': 'Không gian sống',
            'tuyen-sinh': 'Tuyển sinh',
            'du-hoc': 'Du học',
            'chon-nghe': 'Chọn nghề',
            'chon-truong': 'Chọn trường',
            'hoc-tieng-anh': 'Học tiếng Anh'
        }

        category_name = category_mapping.get(category_slug, None)
        subcategory_name = None

        if subcategory_slug:
            subcategory_name = subcategory_mapping.get(subcategory_slug, subcategory_slug.replace('-', ' ').title())

        return category_name, subcategory_name

    except Exception as e:
        print(f"Lỗi khi trích xuất danh mục từ URL: {e}")
        return None, None

def extract_subcategory_from_content(soup):
    """
    Trích xuất thông tin danh mục con từ nội dung bài viết

    Args:
        soup (BeautifulSoup): Đối tượng BeautifulSoup của trang

    Returns:
        str: Tên danh mục con hoặc None
    """
    try:
        # Tìm trong breadcrumb của Dân Trí (mẫu mới)
        breadcrumb = soup.select('ul.dt-text-c808080 li a')
        if len(breadcrumb) >= 2:  # Danh mục > Danh mục con
            subcategory_name = breadcrumb[1].get_text().strip()
            return subcategory_name

        # Thử tìm trong breadcrumb (mẫu cũ)
        breadcrumb = soup.select('ul.breadcrumb li a')
        if len(breadcrumb) >= 3:  # Trang chủ > Danh mục > Danh mục con
            subcategory_name = breadcrumb[2].get_text().strip()
            return subcategory_name

        # Thử tìm trong các thẻ meta
        og_section = soup.select_one('meta[property="article:section"]')
        if og_section and 'content' in og_section.attrs:
            return og_section['content']

        return None
    except Exception as e:
        print(f"Lỗi khi trích xuất danh mục con từ nội dung: {e}")
        return None

def create_category(category_name, parent_id=None, moderator_id=None):
    """
    Tạo danh mục mới nếu chưa tồn tại

    Args:
        category_name (str): Tên của danh mục
        parent_id (int, optional): ID của danh mục cha
        moderator_id (int, optional): ID của kiểm duyệt viên (random từ [5, 6] nếu None và parent_id là None)

    Returns:
        int: ID của danh mục đã tạo hoặc None nếu có lỗi
    """
    # Random moderator_id chỉ khi đây là category chính (không có parent_id)
    # và moderator_id chưa được chỉ định
    if parent_id is None and moderator_id is None:
        moderator_id = random.choice([5, 6])
    # Nếu đây là subcategory (có parent_id), đặt moderator_id là None
    elif parent_id is not None:
        moderator_id = None
    conn = connect_to_database()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        # Tạo slug từ tên danh mục
        slug = slugify(category_name)

        # Kiểm tra xem bảng categories có tồn tại không
        cursor.execute("SHOW TABLES LIKE 'categories'")
        categories_exists = cursor.fetchone()

        if not categories_exists:
            # Tạo bảng categories nếu chưa tồn tại
            cursor.execute("""
            CREATE TABLE categories (
                category_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) NOT NULL,
                parent_id INT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """)
            print("Đã tạo bảng categories")

        # Kiểm tra cấu trúc bảng categories
        cursor.execute("SHOW COLUMNS FROM categories")
        columns = [column[0] for column in cursor.fetchall()]

        # Kiểm tra xem danh mục đã tồn tại chưa
        if parent_id:
            cursor.execute("SELECT category_id FROM categories WHERE slug = %s AND parent_id = %s", (slug, parent_id))
        else:
            cursor.execute("SELECT category_id FROM categories WHERE slug = %s AND parent_id IS NULL", (slug,))

        existing_category = cursor.fetchone()

        if existing_category:
            category_id = existing_category[0]
            print(f"Danh mục '{category_name}' đã tồn tại với ID: {category_id}")
            return category_id

        # Tạo danh mục mới
        # Tạo câu lệnh SQL động dựa trên cấu trúc bảng
        column_names = ["name", "slug"]
        values = [category_name, slug]

        # Chỉ thêm moderator_id nếu:
        # 1. Trường moderator_id tồn tại trong bảng
        # 2. moderator_id không phải là None (đã được xử lý ở đầu hàm)
        if "moderator_id" in columns and moderator_id is not None:
            column_names.append("moderator_id")
            values.append(moderator_id)

        if "parent_id" in columns:
            column_names.append("parent_id")
            values.append(parent_id)

        if "description" in columns:
            description = f"Danh mục {category_name}"
            if parent_id:
                description = f"Danh mục con của {parent_id}"
            column_names.append("description")
            values.append(description)

        if "created_at" in columns:
            column_names.append("created_at")
            values.append(datetime.datetime.now())

        if "updated_at" in columns:
            column_names.append("updated_at")
            values.append(datetime.datetime.now())

        # Tạo câu lệnh SQL
        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(column_names)

        sql = f"INSERT INTO categories ({columns_str}) VALUES ({placeholders})"
        cursor.execute(sql, values)

        category_id = cursor.lastrowid
        conn.commit()

        print(f"Đã tạo danh mục mới '{category_name}' với ID: {category_id}")
        return category_id

    except Exception as e:
        print(f"Lỗi khi tạo danh mục: {e}")
        conn.rollback()
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_category_ids(category_name, subcategory_name=None):
    """
    Lấy category_id và subcategory_id từ cơ sở dữ liệu dựa trên tên

    Args:
        category_name (str): Tên của danh mục
        subcategory_name (str, optional): Tên của danh mục con

    Returns:
        tuple: (category_id, subcategory_id)
    """
    conn = connect_to_database()
    if not conn:
        return None, None

    try:
        cursor = conn.cursor()

        # Kiểm tra cấu trúc bảng categories
        try:
            # Kiểm tra xem bảng categories có tồn tại không
            cursor.execute("SHOW TABLES LIKE 'categories'")
            categories_exists = cursor.fetchone()

            if not categories_exists:
                print("Bảng categories không tồn tại trong cơ sở dữ liệu.")
                return None, None

            # Kiểm tra cấu trúc bảng
            cursor.execute("SHOW COLUMNS FROM categories")
            columns = [column[0] for column in cursor.fetchall()]

            # Xác định tên cột ID
            id_column = "category_id" if "category_id" in columns else "id"

            # Xác định tên cột tên danh mục
            name_column = "name" if "name" in columns else "category_name"

            # Xác định tên cột slug
            slug_column = "slug" if "slug" in columns else "category_slug"

            # Xác định tên cột parent_id
            parent_column = "parent_id" if "parent_id" in columns else "parent_category_id"

            # Tìm category_id dựa trên tên
            cursor.execute(f"SELECT {id_column} FROM categories WHERE {name_column} = %s AND {parent_column} IS NULL", (category_name,))
            category_result = cursor.fetchone()

            # Nếu không tìm thấy, thử tìm dựa trên slug
            if not category_result and slug_column in columns:
                slug = slugify(category_name) if category_name else None
                if slug:
                    cursor.execute(f"SELECT {id_column} FROM categories WHERE {slug_column} = %s AND {parent_column} IS NULL", (slug,))
                    category_result = cursor.fetchone()

            category_id = category_result[0] if category_result else None
            subcategory_id = None

            # Tìm subcategory_id nếu có
            if category_id and subcategory_name:
                # Tìm dựa trên tên và parent_id
                cursor.execute(
                    f"SELECT {id_column} FROM categories WHERE {name_column} = %s AND {parent_column} = %s",
                    (subcategory_name, category_id)
                )
                subcategory_result = cursor.fetchone()

                # Nếu không tìm thấy, thử tìm dựa trên slug
                if not subcategory_result and slug_column in columns:
                    slug = slugify(subcategory_name)
                    cursor.execute(
                        f"SELECT {id_column} FROM categories WHERE {slug_column} = %s AND {parent_column} = %s",
                        (slug, category_id)
                    )
                    subcategory_result = cursor.fetchone()

                subcategory_id = subcategory_result[0] if subcategory_result else None

            return category_id, subcategory_id

        except Exception as e:
            print(f"Lỗi khi kiểm tra cấu trúc bảng categories: {e}")

            # Sử dụng cấu trúc mặc định nếu có lỗi
            # Tìm category_id dựa trên tên
            cursor.execute("SELECT category_id FROM categories WHERE name = %s AND parent_id IS NULL", (category_name,))
            category_result = cursor.fetchone()

            # Nếu không tìm thấy, thử tìm dựa trên slug
            if not category_result:
                slug = slugify(category_name) if category_name else None
                if slug:
                    cursor.execute("SELECT category_id FROM categories WHERE slug = %s AND parent_id IS NULL", (slug,))
                    category_result = cursor.fetchone()

            category_id = category_result[0] if category_result else None
            subcategory_id = None

            # Tìm subcategory_id nếu có
            if category_id and subcategory_name:
                # Tìm dựa trên tên và parent_id
                cursor.execute(
                    "SELECT category_id FROM categories WHERE name = %s AND parent_id = %s",
                    (subcategory_name, category_id)
                )
                subcategory_result = cursor.fetchone()

                # Nếu không tìm thấy, thử tìm dựa trên slug
                if not subcategory_result:
                    slug = slugify(subcategory_name)
                    cursor.execute(
                        "SELECT category_id FROM categories WHERE slug = %s AND parent_id = %s",
                        (slug, category_id)
                    )
                    subcategory_result = cursor.fetchone()

                subcategory_id = subcategory_result[0] if subcategory_result else None

            return category_id, subcategory_id

    except Exception as e:
        print(f"Lỗi khi lấy category_id và subcategory_id: {e}")
        return None, None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def crawl_dantri(url):
    """
    Crawl bài viết từ Dân Trí
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
        title = soup.select_one('h1.title-page')
        title_text = title.get_text().strip() if title else ""

        # Lấy nội dung
        content_div = soup.select_one('div.singular-content')

        # Giữ nguyên định dạng HTML gốc cho TinyMCE
        if content_div:
            # Loại bỏ các thuộc tính class, id không cần thiết để làm sạch HTML
            # Giữ lại style cho một số thẻ để điều chỉnh cỡ chữ
            for tag in content_div.find_all(True):
                if tag.has_attr('class'):
                    del tag['class']
                if tag.has_attr('id'):
                    del tag['id']

                # Điều chỉnh cỡ chữ cho các thẻ văn bản
                if tag.name in ['p', 'span', 'div']:
                    tag['style'] = 'font-size: 18px; line-height: 1.6;'
                elif tag.name == 'h1':
                    tag['style'] = 'font-size: 28px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;'
                elif tag.name == 'h2':
                    tag['style'] = 'font-size: 24px; font-weight: bold; margin-top: 15px; margin-bottom: 10px;'
                elif tag.name == 'h3':
                    tag['style'] = 'font-size: 20px; font-weight: bold; margin-top: 15px; margin-bottom: 10px;'
                elif tag.name == 'li':
                    tag['style'] = 'font-size: 18px; margin-bottom: 5px;'

            # Chuyển đổi các thẻ img để giữ nguyên src và đảm bảo URL đầy đủ
            for img in content_div.find_all('img'):
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
                            img['src'] = 'https://dantri.com.vn' + src

                # Loại bỏ các thuộc tính không cần thiết
                attrs_to_keep = ['src', 'alt']
                for attr in list(img.attrs.keys()):
                    if attr not in attrs_to_keep:
                        del img[attr]

            # Lấy HTML đã được làm sạch
            content_html = str(content_div)
        else:
            content_html = ""

        # Vẫn trích xuất text thuần túy cho preview
        content_text = extract_text_from_html(content_html)

        # Lấy ngày đăng
        date_element = soup.select_one('time.author-time')
        date_text = date_element.get_text().strip() if date_element else ""

        # Lấy thumbnail từ nhiều nguồn khác nhau
        thumbnail_url = ""

        # Thử lấy từ meta og:image (cách tốt nhất)
        thumbnail = soup.select_one('meta[property="og:image"]')
        if thumbnail and 'content' in thumbnail.attrs:
            thumbnail_url = thumbnail['content']

        # Nếu không có, thử lấy từ thẻ figure đầu tiên trong bài viết
        if not thumbnail_url and content_div:
            first_figure = content_div.select_one('figure img')
            if first_figure and first_figure.has_attr('src'):
                thumbnail_url = first_figure['src']
            elif first_figure and first_figure.has_attr('data-src'):
                thumbnail_url = first_figure['data-src']
            elif first_figure and first_figure.has_attr('data-original'):
                thumbnail_url = first_figure['data-original']

        # Đảm bảo thumbnail_url là URL đầy đủ
        if thumbnail_url and not thumbnail_url.startswith('http'):
            if thumbnail_url.startswith('//'):
                thumbnail_url = 'https:' + thumbnail_url
            elif thumbnail_url.startswith('/'):
                thumbnail_url = 'https://dantri.com.vn' + thumbnail_url

        # Tạo preview content (lấy 200 ký tự đầu tiên)
        preview_content = content_text[:200] + "..." if len(content_text) > 200 else content_text

        # Trích xuất thông tin danh mục từ URL
        category_name, subcategory_from_url = extract_category_from_url(url)
        print(f"Danh mục từ URL: {category_name}")
        if subcategory_from_url:
            print(f"Danh mục con từ URL: {subcategory_from_url}")

        # Trích xuất thông tin danh mục con từ nội dung
        subcategory_from_content = extract_subcategory_from_content(soup)
        if subcategory_from_content:
            print(f"Danh mục con từ nội dung: {subcategory_from_content}")

        # Ưu tiên subcategory từ URL, nếu không có thì dùng từ nội dung
        subcategory_name = subcategory_from_url or subcategory_from_content

        # Lấy tags từ meta keywords
        tags = []
        keywords_meta = soup.select_one('meta[name="keywords"]')
        if keywords_meta and 'content' in keywords_meta.attrs:
            keywords_content = keywords_meta['content']
            if keywords_content:
                tags = [tag.strip() for tag in keywords_content.split(',') if tag.strip()]

        # Tạo kết quả
        result = {
            'url': url,
            'title': title_text,
            'content': content_html,
            'content_text': content_text,
            'preview_content': preview_content,
            'date': date_text,
            'thumbnail_url': thumbnail_url,
            'category_name': category_name,
            'subcategory_name': subcategory_name,
            'tags': tags
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
        # Thử import constants từ news_crawler
        try:
            from news_crawler import constants
            # Kiểm tra xem PASSWORD có phải là None không
            password = "" if constants.PASSWORD is None else constants.PASSWORD
            conn = mysql.connector.connect(
                host=constants.HOST,
                user=constants.USER,
                password=password,  # Sử dụng chuỗi rỗng nếu PASSWORD là None
                database=constants.DATABASE,
                port=constants.PORT
            )
        except ImportError:
            # Nếu không import được, sử dụng thông tin kết nối mặc định
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Mật khẩu rỗng
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
                    # Đảm bảo đường dẫn bắt đầu bằng / và không có dấu \ (thay bằng /)
                    local_path = local_path.replace('\\', '/')
                    img['src'] = f"/{local_path}"
                    print(f"Đã tải ảnh: {img['src']}")

    # Trả về nội dung HTML đã xử lý
    return str(soup)

def save_to_database(data, author_id=None, admin_id=None, moderator_id=None, user_id=None, category_id=2, subcategory_id=None, tags=None, download_images=True):
    """
    Lưu dữ liệu vào cơ sở dữ liệu

    Args:
        data (dict): Dữ liệu bài viết
        author_id (int, optional): ID của tác giả (random từ [7, 8] nếu None)
        admin_id (int, optional): ID của admin (random từ [3, 4] nếu None)
        moderator_id (int, optional): ID của kiểm duyệt viên (random từ [5, 6] nếu None)
        user_id (int, optional): ID của người dùng thông thường (random từ [9, 10] nếu None)
        category_id (int): ID của danh mục
        subcategory_id (int, optional): ID của danh mục con
        tags (list, optional): Danh sách các tag
        download_images (bool): Có tải ảnh về không
    """
    # Tạo các thời gian ngẫu nhiên cho bài viết và các bảng liên quan
    # Thời gian tạo bài viết (trong khoảng 12 tháng trước đến tháng 5/2025)
    article_created_at = generate_random_datetime(months=12)

    # Thời gian cho các bảng liên quan - đảm bảo thứ tự thời gian hợp lý
    # Tạo một khoảng thời gian ngẫu nhiên (tính bằng phút) để thêm vào thời gian cơ sở

    # Thời gian tạo phiên bản đầu tiên - cùng lúc với bài viết
    version_created_at = article_created_at

    # Thời gian tạo lịch sử bài viết - cùng lúc với bài viết
    history_edited_at = article_created_at

    # Thời gian tạo approval - sau khi tạo bài viết một chút (5-30 phút)
    approval_created_at = article_created_at + timedelta(minutes=random.randint(5, 30))

    # Random trạng thái approval
    # Có 3 trạng thái có thể có: 'pending', 'approved', 'rejected'
    # Tỷ lệ: 20% pending, 70% approved, 10% rejected
    approval_status_random = random.random()
    if approval_status_random < 0.2:
        approval_status = 'pending'
    elif approval_status_random < 0.9:
        approval_status = 'approved'
    else:
        approval_status = 'rejected'

    # Random trạng thái article dựa trên trạng thái approval
    if approval_status == 'pending':
        # Nếu approval đang pending, article cũng phải pending
        article_status = 'pending'
    elif approval_status == 'approved':
        # Nếu approval đã approved, article có thể là published hoặc archived
        # Tỷ lệ: 90% published, 10% archived
        article_status = 'published' if random.random() < 0.9 else 'archived'
    else:  # approval_status == 'rejected'
        # Nếu approval bị rejected, article có thể là draft hoặc rejected
        # Tỷ lệ: 30% draft, 70% rejected
        article_status = 'draft' if random.random() < 0.3 else 'rejected'

    # Thời gian cập nhật approval - sau khi tạo approval (10-60 phút)
    # Nếu approval không còn ở trạng thái pending, thời gian cập nhật sẽ dài hơn
    if approval_status == 'pending':
        approval_updated_at = approval_created_at + timedelta(minutes=random.randint(10, 60))
    else:
        # Nếu đã approved hoặc rejected, thời gian xử lý lâu hơn (1-24 giờ)
        approval_updated_at = approval_created_at + timedelta(hours=random.randint(1, 24))

    # Thời gian cập nhật phiên bản - sau khi tạo phiên bản (nếu có chỉnh sửa, 1-3 giờ)
    version_updated_at = version_created_at + timedelta(hours=random.randint(1, 3))

    # Thời gian cập nhật bài viết - sau cùng, sau khi tất cả các quá trình khác hoàn tất
    # Lấy thời gian muộn nhất trong các thời gian trên và thêm 30-60 phút
    latest_time = max(approval_updated_at, version_updated_at)
    article_updated_at = latest_time + timedelta(minutes=random.randint(30, 60))
    # Random các ID người dùng nếu chưa được chỉ định
    if author_id is None:
        author_id = random.choice([7, 8])
    if admin_id is None:
        admin_id = random.choice([3, 4])
    if moderator_id is None:
        moderator_id = random.choice([5, 6])
    if user_id is None:
        user_id = random.choice([9, 10])
    conn = connect_to_database()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Tạo slug từ tiêu đề
        slug = slugify(data['title'])

        # Thêm một chuỗi ngẫu nhiên vào slug để đảm bảo tính duy nhất
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        slug = f"{slug}-{random_suffix}"

        # Tạo code cho bài viết
        current_date = datetime.datetime.now().strftime("%d%m%y")
        random_number = hashlib.md5(data['url'].encode()).hexdigest()[:8]
        code = f"BV-{current_date}-{random_number}"

        # Kiểm tra cấu trúc bảng articles
        try:
            # Kiểm tra xem bảng articles có tồn tại không
            cursor.execute("SHOW TABLES LIKE 'articles'")
            articles_exists = cursor.fetchone()

            if not articles_exists:
                # Thử kiểm tra bảng news (từ migration)
                cursor.execute("SHOW TABLES LIKE 'news'")
                news_exists = cursor.fetchone()

                if news_exists:
                    print("Sử dụng bảng news thay vì articles.")
                    # Kiểm tra xem bài viết đã tồn tại chưa
                    cursor.execute("SELECT id FROM news WHERE title = %s", (data['title'],))
                    existing_article = cursor.fetchone()

                    if existing_article:
                        print(f"Bài viết với tiêu đề '{data['title']}' đã tồn tại trong cơ sở dữ liệu.")
                        return False

                    # Xử lý ảnh trong nội dung
                    content_html = process_images_in_content(data['content'], download_images)

                    # Xử lý thumbnail_url
                    thumbnail_url = data['thumbnail_url']
                    if download_images and thumbnail_url and thumbnail_url.startswith('http'):
                        local_thumbnail = download_image(thumbnail_url, save_dir='thumbnails')
                        if local_thumbnail:
                            # Đảm bảo đường dẫn không có dấu \ (thay bằng /)
                            local_thumbnail = local_thumbnail.replace('\\', '/')
                            thumbnail_url = local_thumbnail
                            print(f"Đã tải thumbnail: {thumbnail_url}")

                    # Thêm bài viết vào bảng news
                    sql = """
                    INSERT INTO news (title, category, content, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """

                    values = (
                        data['title'],
                        data['category_name'] or "Uncategorized",
                        content_html,
                        article_created_at,
                        article_updated_at
                    )

                    cursor.execute(sql, values)
                    article_id = cursor.lastrowid

                    conn.commit()
                    print(f"Đã lưu bài viết '{data['title']}' vào bảng news với ID: {article_id}")
                    return article_id
                else:
                    print("Không tìm thấy bảng articles hoặc news trong cơ sở dữ liệu.")
                    return False

            # Kiểm tra cấu trúc bảng articles
            cursor.execute("SHOW COLUMNS FROM articles")
            columns = [column[0] for column in cursor.fetchall()]

            # Xác định tên cột ID
            id_column = "article_id" if "article_id" in columns else "id"

            # Kiểm tra xem bài viết đã tồn tại chưa
            cursor.execute(f"SELECT {id_column} FROM articles WHERE slug = %s", (slug,))
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
                    # Đảm bảo đường dẫn không có dấu \ (thay bằng /)
                    local_thumbnail = local_thumbnail.replace('\\', '/')
                    thumbnail_url = local_thumbnail
                    print(f"Đã tải thumbnail: {thumbnail_url}")

            # Tạo danh sách các cột và giá trị
            column_names = []
            values = []

            # Thêm các trường cơ bản
            if "code" in columns:
                column_names.append("code")
                values.append(code)

            column_names.extend(["title", "slug", "content"])
            values.extend([data['title'], slug, content_html])

            if "preview_content" in columns:
                column_names.append("preview_content")
                values.append(data['preview_content'])

            if "contains_sensitive_content" in columns:
                column_names.append("contains_sensitive_content")
                values.append(0)

            if "author_id" in columns:
                column_names.append("author_id")
                values.append(author_id)

            if "category_id" in columns:
                column_names.append("category_id")
                values.append(category_id)

            if "subcategory_id" in columns:
                column_names.append("subcategory_id")
                values.append(subcategory_id)

            if "thumbnail_url" in columns:
                column_names.append("thumbnail_url")
                values.append(thumbnail_url)

            if "status" in columns:
                column_names.append("status")
                values.append(article_status)

            # Thêm approved_by nếu có trong cấu trúc bảng và article đã được phê duyệt hoặc từ chối
            if "approved_by" in columns:
                column_names.append("approved_by")
                if approval_status in ['approved', 'rejected']:
                    values.append(approval_user_id)  # Người phê duyệt hoặc từ chối
                else:
                    values.append(None)  # Chưa được phê duyệt

            if "views" in columns:
                column_names.append("views")
                values.append(0)

            column_names.extend(["created_at", "updated_at"])
            values.extend([article_created_at, article_updated_at])

            # Tạo câu lệnh SQL động
            placeholders = ", ".join(["%s"] * len(values))
            columns_str = ", ".join(column_names)

            sql = f"INSERT INTO articles ({columns_str}) VALUES ({placeholders})"

            cursor.execute(sql, values)
            article_id = cursor.lastrowid

            # Kiểm tra bảng approvals
            cursor.execute("SHOW TABLES LIKE 'approvals'")
            approvals_exists = cursor.fetchone()

            if approvals_exists:
                # Kiểm tra cấu trúc bảng approvals
                cursor.execute("SHOW COLUMNS FROM approvals")
                approval_columns = [column[0] for column in cursor.fetchall()]

                # Chuẩn bị các trường và giá trị cơ bản
                approval_column_names = ["type", "article_id", "user_id", "status", "remarks", "created_at", "updated_at"]

                approval_values = [
                    'article',
                    article_id,
                    approval_user_id,  # Sử dụng ID của admin hoặc kiểm duyệt viên
                    approval_status,
                    remarks,
                    approval_created_at,
                    approval_updated_at
                ]

                # Thêm approved_by nếu có trong cấu trúc bảng và approval đã được phê duyệt hoặc từ chối
                if "approved_by" in approval_columns:
                    approval_column_names.append("approved_by")
                    if approval_status in ['approved', 'rejected']:
                        approval_values.append(approval_user_id)  # Người phê duyệt hoặc từ chối
                    else:
                        approval_values.append(None)  # Chưa được phê duyệt

                # Thêm các trường bổ sung nếu có trong cấu trúc bảng
                if "violation_level" in approval_columns:
                    approval_column_names.append("violation_level")
                    # Nếu bị từ chối, có thể có mức độ vi phạm
                    if approval_status == 'rejected':
                        # Random mức độ vi phạm: 10% none, 30% low, 40% medium, 20% high
                        violation_random = random.random()
                        if violation_random < 0.1:
                            violation_level = "none"
                        elif violation_random < 0.4:
                            violation_level = "low"
                        elif violation_random < 0.8:
                            violation_level = "medium"
                        else:
                            violation_level = "high"
                    else:
                        violation_level = "none"
                    approval_values.append(violation_level)

                if "violations" in approval_columns:
                    approval_column_names.append("violations")
                    # Nếu bị từ chối và có mức độ vi phạm, thêm thông tin vi phạm
                    if approval_status == 'rejected' and 'violation_level' in locals() and violation_level != "none":
                        possible_violations = [
                            "Nội dung không phù hợp",
                            "Thông tin sai lệch",
                            "Vi phạm bản quyền",
                            "Ngôn ngữ không phù hợp",
                            "Quảng cáo trá hình",
                            "Nội dung nhạy cảm"
                        ]
                        # Chọn 1-3 vi phạm ngẫu nhiên
                        num_violations = random.randint(1, min(3, len(possible_violations)))
                        violations = random.sample(possible_violations, num_violations)
                        violations_text = ", ".join(violations)
                    else:
                        violations_text = None
                    approval_values.append(violations_text)

                if "violation_details" in approval_columns:
                    approval_column_names.append("violation_details")
                    # Nếu có vi phạm, thêm chi tiết
                    if 'violations_text' in locals() and violations_text:
                        # Tạo JSON với chi tiết vi phạm
                        violation_details = {}
                        for i, violation in enumerate(violations):
                            violation_details[f"violation_{i+1}"] = {
                                "type": violation,
                                "description": f"Chi tiết về vi phạm: {violation.lower()}",
                                "severity": violation_level
                            }
                        violation_details_json = json.dumps(violation_details)
                    else:
                        violation_details_json = None
                    approval_values.append(violation_details_json)

                if "processed_at" in approval_columns:
                    approval_column_names.append("processed_at")
                    # Nếu approval đã được xử lý (approved hoặc rejected), thêm thời gian xử lý
                    if approval_status in ['approved', 'rejected']:
                        processed_at = approval_updated_at
                    else:
                        processed_at = None
                    approval_values.append(processed_at)

                if "processed_by" in approval_columns:
                    approval_column_names.append("processed_by")
                    # Nếu approval đã được xử lý, thêm người xử lý
                    if approval_status in ['approved', 'rejected']:
                        processed_by = approval_user_id
                    else:
                        processed_by = None
                    approval_values.append(processed_by)

                # Tạo câu lệnh SQL động
                approval_placeholders = ", ".join(["%s"] * len(approval_values))
                approval_columns_str = ", ".join(approval_column_names)

                sql_approval = f"INSERT INTO approvals ({approval_columns_str}) VALUES ({approval_placeholders})"

                cursor.execute(sql_approval, approval_values)

            # Kiểm tra bảng tags và article_tags
            cursor.execute("SHOW TABLES LIKE 'tags'")
            tags_exists = cursor.fetchone()

            cursor.execute("SHOW TABLES LIKE 'article_tags'")
            article_tags_exists = cursor.fetchone()

            # Thêm tags vào bảng article_tags nếu có
            if tags and isinstance(tags, list) and len(tags) > 0 and tags_exists and article_tags_exists:
                # Lấy hoặc tạo tag_id cho mỗi tag
                for tag_name in tags:
                    # Kiểm tra xem tag đã tồn tại chưa
                    cursor.execute("SELECT tag_id FROM tags WHERE name = %s", (tag_name,))
                    tag_result = cursor.fetchone()

                    if tag_result:
                        tag_id = tag_result[0]
                    else:
                        # Tạo tag mới
                        cursor.execute(
                            "INSERT INTO tags (name, description) VALUES (%s, %s)",
                            (tag_name, "")
                        )
                        tag_id = cursor.lastrowid

                    # Thêm vào bảng article_tags
                    cursor.execute(
                        "INSERT INTO article_tags (article_id, tag_id, created_at, updated_at) VALUES (%s, %s, %s, %s)",
                        (article_id, tag_id, article_created_at, article_updated_at)
                    )
                    print(f"Đã thêm tag '{tag_name}' cho bài viết")

            # Kiểm tra bảng article_versions
            cursor.execute("SHOW TABLES LIKE 'article_versions'")
            article_versions_exists = cursor.fetchone()

            if article_versions_exists:
                # Kiểm tra cấu trúc bảng article_versions
                cursor.execute("SHOW COLUMNS FROM article_versions")
                version_columns = [column[0] for column in cursor.fetchall()]

                # Sử dụng thời gian đã được tạo ở đầu hàm
                # Không cần tạo lại thời gian ở đây

                # Tạo version_id duy nhất
                version_id = f"V-{version_created_at.strftime('%Y%m%d%H%M%S')}-{hashlib.md5(str(article_id).encode()).hexdigest()[:8]}"

                # Chuẩn bị các trường và giá trị cơ bản
                version_column_names = ["version_id", "article_id", "user_id", "title", "content", "slug"]
                version_values = [
                    version_id,
                    article_id,
                    author_id,  # Sử dụng ID của tác giả vì tác giả là người tạo và chỉnh sửa bài viết
                    data['title'],
                    content_html,
                    slug
                ]

                # Thêm các trường bổ sung nếu có trong cấu trúc bảng
                if "category_id" in version_columns:
                    version_column_names.append("category_id")
                    version_values.append(category_id)

                if "subcategory_id" in version_columns:
                    version_column_names.append("subcategory_id")
                    version_values.append(subcategory_id)

                if "featured_image" in version_columns:
                    version_column_names.append("featured_image")
                    version_values.append(thumbnail_url)

                if "tags" in version_columns and tags:
                    version_column_names.append("tags")
                    version_values.append(json.dumps(tags))

                if "change_reason" in version_columns:
                    version_column_names.append("change_reason")
                    version_values.append("Bài viết mới từ crawl")

                if "created_at" in version_columns:
                    version_column_names.append("created_at")
                    version_values.append(version_created_at)

                if "updated_at" in version_columns:
                    version_column_names.append("updated_at")
                    version_values.append(version_updated_at)

                # Tạo câu lệnh SQL động
                version_placeholders = ", ".join(["%s"] * len(version_values))
                version_columns_str = ", ".join(version_column_names)

                sql_version = f"INSERT INTO article_versions ({version_columns_str}) VALUES ({version_placeholders})"

                cursor.execute(sql_version, version_values)
                print(f"Đã thêm phiên bản đầu tiên cho bài viết với ID: {article_id}")

            # Kiểm tra bảng article_history
            cursor.execute("SHOW TABLES LIKE 'article_history'")
            article_history_exists = cursor.fetchone()

            if article_history_exists:
                # Thêm vào bảng article_history
                sql_history = """
                INSERT INTO article_history (article_id, content, edited_by, edited_at)
                VALUES (%s, %s, %s, %s)
                """

                # Sử dụng thời gian đã được tạo ở đầu hàm
                # Không cần tạo lại thời gian ở đây

                values_history = (
                    article_id,
                    content_html,
                    author_id,  # Sử dụng ID của tác giả vì tác giả là người tạo và chỉnh sửa bài viết
                    history_edited_at
                )

                cursor.execute(sql_history, values_history)
                print(f"Đã thêm lịch sử cho bài viết với ID: {article_id}")

            # Kiểm tra bảng article_media
            cursor.execute("SHOW TABLES LIKE 'article_media'")
            article_media_exists = cursor.fetchone()

            if article_media_exists and thumbnail_url:
                # Thêm thumbnail vào bảng article_media
                sql_media = """
                INSERT INTO article_media (article_id, media_type, media_url, caption, position)
                VALUES (%s, %s, %s, %s, %s)
                """

                values_media = (
                    article_id,
                    'image',
                    thumbnail_url,
                    data['title'],
                    0  # Vị trí đầu tiên
                )

                cursor.execute(sql_media, values_media)
                print(f"Đã thêm thumbnail vào bảng article_media cho bài viết với ID: {article_id}")

                # Trích xuất các ảnh từ nội dung và thêm vào bảng article_media
                soup = BeautifulSoup(content_html, 'html.parser')
                images = soup.find_all('img')

                for i, img in enumerate(images, 1):
                    if img.has_attr('src'):
                        img_url = img['src']
                        img_caption = img.get('alt', '') or data['title']

                        # Thêm ảnh vào bảng article_media
                        sql_media = """
                        INSERT INTO article_media (article_id, media_type, media_url, caption, position)
                        VALUES (%s, %s, %s, %s, %s)
                        """

                        values_media = (
                            article_id,
                            'image',
                            img_url,
                            img_caption,
                            i  # Vị trí tăng dần
                        )

                        cursor.execute(sql_media, values_media)
                        print(f"Đã thêm ảnh từ nội dung vào bảng article_media cho bài viết với ID: {article_id}")

            conn.commit()
            print(f"Đã lưu bài viết '{data['title']}' vào cơ sở dữ liệu với ID: {article_id}")
            return article_id

        except Exception as e:
            print(f"Lỗi khi kiểm tra cấu trúc bảng: {e}")

            # Sử dụng cấu trúc mặc định nếu có lỗi
            # Tạo slug mới với chuỗi ngẫu nhiên để đảm bảo tính duy nhất
            slug = slugify(data['title'])
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            slug = f"{slug}-{random_suffix}"

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
                    # Đảm bảo đường dẫn không có dấu \ (thay bằng /)
                    local_thumbnail = local_thumbnail.replace('\\', '/')
                    thumbnail_url = local_thumbnail
                    print(f"Đã tải thumbnail: {thumbnail_url}")

            # Thêm bài viết vào bảng articles
            sql = """
            INSERT INTO articles (code, title, slug, content, preview_content,
                                contains_sensitive_content, author_id, category_id, subcategory_id,
                                thumbnail_url, status, views, approved_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Random giữa admin và moderator cho người kiểm duyệt
            approval_user_id = random.choice([admin_id, moderator_id])

            # Tạo ghi chú phù hợp với trạng thái approval
            if approval_status == 'pending':
                remarks = 'Bài viết mới, chờ kiểm duyệt'
            elif approval_status == 'approved':
                remarks = 'Bài viết đã được phê duyệt'
            else:  # rejected
                # Tạo lý do từ chối ngẫu nhiên
                reject_reasons = [
                    'Bài viết bị từ chối do vi phạm quy định về nội dung',
                    'Bài viết chứa thông tin không chính xác',
                    'Bài viết có nội dung nhạy cảm không phù hợp',
                    'Bài viết trùng lặp với nội dung đã có',
                    'Bài viết không đáp ứng tiêu chuẩn chất lượng',
                    'Bài viết vi phạm bản quyền'
                ]
                remarks = random.choice(reject_reasons)

            values = (
                code,
                data['title'],
                slug,
                content_html,
                data['preview_content'],
                0,  # contains_sensitive_content
                author_id,
                category_id,
                subcategory_id,  # subcategory_id
                thumbnail_url,
                article_status,  # status
                0,  # views
                approval_user_id if approval_status in ['approved', 'rejected'] else None,  # approved_by
                article_created_at,
                article_updated_at
            )

            cursor.execute(sql, values)
            article_id = cursor.lastrowid

            # Kiểm tra cấu trúc bảng approvals
            cursor.execute("SHOW COLUMNS FROM approvals")
            approval_columns = [column[0] for column in cursor.fetchall()]

            # Chuẩn bị các trường và giá trị cơ bản
            approval_column_names = ["type", "article_id", "user_id", "status", "remarks", "created_at", "updated_at"]
            # Random giữa admin và moderator cho người kiểm duyệt
            approval_user_id = random.choice([admin_id, moderator_id])
            approval_values = [
                'article',
                article_id,
                approval_user_id,  # Sử dụng ID của admin hoặc kiểm duyệt viên
                approval_status,
                remarks,
                approval_created_at,
                approval_updated_at
            ]

            # Thêm các trường bổ sung nếu có trong cấu trúc bảng
            if "violation_level" in approval_columns:
                approval_column_names.append("violation_level")
                # Nếu bị từ chối, có thể có mức độ vi phạm
                if approval_status == 'rejected':
                    # Random mức độ vi phạm: 10% none, 30% low, 40% medium, 20% high
                    violation_random = random.random()
                    if violation_random < 0.1:
                        violation_level = "none"
                    elif violation_random < 0.4:
                        violation_level = "low"
                    elif violation_random < 0.8:
                        violation_level = "medium"
                    else:
                        violation_level = "high"
                else:
                    violation_level = "none"
                approval_values.append(violation_level)

            if "violations" in approval_columns:
                approval_column_names.append("violations")
                # Nếu bị từ chối và có mức độ vi phạm, thêm thông tin vi phạm
                if approval_status == 'rejected' and 'violation_level' in locals() and violation_level != "none":
                    possible_violations = [
                        "Nội dung không phù hợp",
                        "Thông tin sai lệch",
                        "Vi phạm bản quyền",
                        "Ngôn ngữ không phù hợp",
                        "Quảng cáo trá hình",
                        "Nội dung nhạy cảm"
                    ]
                    # Chọn 1-3 vi phạm ngẫu nhiên
                    num_violations = random.randint(1, min(3, len(possible_violations)))
                    violations = random.sample(possible_violations, num_violations)
                    violations_text = ", ".join(violations)
                else:
                    violations_text = None
                approval_values.append(violations_text)

            if "violation_details" in approval_columns:
                approval_column_names.append("violation_details")
                # Nếu có vi phạm, thêm chi tiết
                if 'violations_text' in locals() and violations_text:
                    # Tạo JSON với chi tiết vi phạm
                    violation_details = {}
                    for i, violation in enumerate(violations):
                        violation_details[f"violation_{i+1}"] = {
                            "type": violation,
                            "description": f"Chi tiết về vi phạm: {violation.lower()}",
                            "severity": violation_level
                        }
                    violation_details_json = json.dumps(violation_details)
                else:
                    violation_details_json = None
                approval_values.append(violation_details_json)

            if "processed_at" in approval_columns:
                approval_column_names.append("processed_at")
                # Nếu approval đã được xử lý (approved hoặc rejected), thêm thời gian xử lý
                if approval_status in ['approved', 'rejected']:
                    processed_at = approval_updated_at
                else:
                    processed_at = None
                approval_values.append(processed_at)

            if "processed_by" in approval_columns:
                approval_column_names.append("processed_by")
                # Nếu approval đã được xử lý, thêm người xử lý
                if approval_status in ['approved', 'rejected']:
                    processed_by = approval_user_id
                else:
                    processed_by = None
                approval_values.append(processed_by)

            # Tạo câu lệnh SQL động
            approval_placeholders = ", ".join(["%s"] * len(approval_values))
            approval_columns_str = ", ".join(approval_column_names)

            sql_approval = f"INSERT INTO approvals ({approval_columns_str}) VALUES ({approval_placeholders})"

            cursor.execute(sql_approval, approval_values)

            # Thêm tags vào bảng article_tags nếu có
            if tags and isinstance(tags, list) and len(tags) > 0:
                # Lấy hoặc tạo tag_id cho mỗi tag
                for tag_name in tags:
                    # Kiểm tra xem tag đã tồn tại chưa
                    cursor.execute("SELECT tag_id FROM tags WHERE name = %s", (tag_name,))
                    tag_result = cursor.fetchone()

                    if tag_result:
                        tag_id = tag_result[0]
                    else:
                        # Tạo tag mới
                        cursor.execute(
                            "INSERT INTO tags (name, description) VALUES (%s, %s)",
                            (tag_name, "")
                        )
                        tag_id = cursor.lastrowid

                    # Thêm vào bảng article_tags
                    cursor.execute(
                        "INSERT INTO article_tags (article_id, tag_id, created_at, updated_at) VALUES (%s, %s, %s, %s)",
                        (article_id, tag_id, article_created_at, article_updated_at)
                    )
                    print(f"Đã thêm tag '{tag_name}' cho bài viết")

            # Kiểm tra bảng article_versions
            cursor.execute("SHOW TABLES LIKE 'article_versions'")
            article_versions_exists = cursor.fetchone()

            if article_versions_exists:
                # Kiểm tra cấu trúc bảng article_versions
                cursor.execute("SHOW COLUMNS FROM article_versions")
                version_columns = [column[0] for column in cursor.fetchall()]

                # Sử dụng thời gian đã được tạo ở đầu hàm
                # Không cần tạo lại thời gian ở đây

                # Tạo version_id duy nhất
                version_id = f"V-{version_created_at.strftime('%Y%m%d%H%M%S')}-{hashlib.md5(str(article_id).encode()).hexdigest()[:8]}"

                # Chuẩn bị các trường và giá trị cơ bản
                version_column_names = ["version_id", "article_id", "user_id", "title", "content", "slug"]
                version_values = [
                    version_id,
                    article_id,
                    author_id,  # Sử dụng ID của tác giả vì tác giả là người tạo và chỉnh sửa bài viết
                    data['title'],
                    content_html,
                    slug
                ]

                # Thêm các trường bổ sung nếu có trong cấu trúc bảng
                if "category_id" in version_columns:
                    version_column_names.append("category_id")
                    version_values.append(category_id)

                if "subcategory_id" in version_columns:
                    version_column_names.append("subcategory_id")
                    version_values.append(subcategory_id)

                if "featured_image" in version_columns:
                    version_column_names.append("featured_image")
                    version_values.append(thumbnail_url)

                if "tags" in version_columns and tags:
                    version_column_names.append("tags")
                    version_values.append(json.dumps(tags))

                if "change_reason" in version_columns:
                    version_column_names.append("change_reason")
                    version_values.append("Bài viết mới từ crawl")

                if "created_at" in version_columns:
                    version_column_names.append("created_at")
                    version_values.append(version_created_at)

                if "updated_at" in version_columns:
                    version_column_names.append("updated_at")
                    version_values.append(version_updated_at)

                # Tạo câu lệnh SQL động
                version_placeholders = ", ".join(["%s"] * len(version_values))
                version_columns_str = ", ".join(version_column_names)

                sql_version = f"INSERT INTO article_versions ({version_columns_str}) VALUES ({version_placeholders})"

                cursor.execute(sql_version, version_values)
                print(f"Đã thêm phiên bản đầu tiên cho bài viết với ID: {article_id}")

            # Kiểm tra bảng article_history
            cursor.execute("SHOW TABLES LIKE 'article_history'")
            article_history_exists = cursor.fetchone()

            if article_history_exists:
                # Thêm vào bảng article_history
                sql_history = """
                INSERT INTO article_history (article_id, content, edited_by, edited_at)
                VALUES (%s, %s, %s, %s)
                """

                # Sử dụng thời gian đã được tạo ở đầu hàm
                # Không cần tạo lại thời gian ở đây

                values_history = (
                    article_id,
                    content_html,
                    author_id,  # Sử dụng ID của tác giả vì tác giả là người tạo và chỉnh sửa bài viết
                    history_edited_at
                )

                cursor.execute(sql_history, values_history)
                print(f"Đã thêm lịch sử cho bài viết với ID: {article_id}")

            # Kiểm tra bảng article_media
            cursor.execute("SHOW TABLES LIKE 'article_media'")
            article_media_exists = cursor.fetchone()

            if article_media_exists and thumbnail_url:
                # Thêm thumbnail vào bảng article_media
                sql_media = """
                INSERT INTO article_media (article_id, media_type, media_url, caption, position)
                VALUES (%s, %s, %s, %s, %s)
                """

                values_media = (
                    article_id,
                    'image',
                    thumbnail_url,
                    data['title'],
                    0  # Vị trí đầu tiên
                )

                cursor.execute(sql_media, values_media)
                print(f"Đã thêm thumbnail vào bảng article_media cho bài viết với ID: {article_id}")

                # Trích xuất các ảnh từ nội dung và thêm vào bảng article_media
                soup = BeautifulSoup(content_html, 'html.parser')
                images = soup.find_all('img')

                for i, img in enumerate(images, 1):
                    if img.has_attr('src'):
                        img_url = img['src']
                        img_caption = img.get('alt', '') or data['title']

                        # Thêm ảnh vào bảng article_media
                        sql_media = """
                        INSERT INTO article_media (article_id, media_type, media_url, caption, position)
                        VALUES (%s, %s, %s, %s, %s)
                        """

                        values_media = (
                            article_id,
                            'image',
                            img_url,
                            img_caption,
                            i  # Vị trí tăng dần
                        )

                        cursor.execute(sql_media, values_media)
                        print(f"Đã thêm ảnh từ nội dung vào bảng article_media cho bài viết với ID: {article_id}")

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

def save_to_file(data, filename=None):
    """
    Lưu dữ liệu vào file
    """
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs('crawled_data', exist_ok=True)

        # Tạo tên file từ URL nếu không được cung cấp
        if not filename:
            filename = data['url'].split('/')[-1].replace('.htm', '.html')

        # Lưu nội dung vào file HTML
        with open(f'crawled_data/{filename}', 'w', encoding='utf-8') as f:
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{data['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        img {{ max-width: 100%; height: auto; }}
        .thumbnail {{ margin-bottom: 20px; }}
        .date {{ color: #666; font-style: italic; margin-bottom: 20px; }}
        .content {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>{data['title']}</h1>
    <div class="date">{data['date']}</div>

    <div class="thumbnail">
        <img src="{data['thumbnail_url']}" alt="{data['title']}">
    </div>

    <div class="content">
        {data['content']}
    </div>

    <div class="source">
        <p>Nguồn: <a href="{data['url']}">{data['url']}</a></p>
    </div>
</body>
</html>"""
            f.write(html_content)

        print(f"Đã lưu nội dung vào file crawled_data/{filename}")
        return f'crawled_data/{filename}'

    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu vào file: {e}")
        return None

def main():
    """
    Hàm chính
    """
    parser = argparse.ArgumentParser(description='Crawl bài báo từ Dân Trí và lưu vào cơ sở dữ liệu')
    parser.add_argument('url', help='URL của bài viết cần crawl')
    parser.add_argument('--author', type=int, help='ID của tác giả (mặc định: random từ [7, 8])')
    parser.add_argument('--admin', type=int, help='ID của admin (mặc định: random từ [3, 4])')
    parser.add_argument('--moderator', type=int, help='ID của kiểm duyệt viên (mặc định: random từ [5, 6])')
    parser.add_argument('--normal-user', type=int, help='ID của người dùng thông thường (mặc định: random từ [9, 10])')
    parser.add_argument('--category', type=int, help='ID của danh mục (tự động xác định nếu không chỉ định)')
    parser.add_argument('--subcategory', type=int, help='ID của danh mục con (tự động xác định nếu không chỉ định)')
    parser.add_argument('--tags', help='Danh sách các tag, phân cách bằng dấu phẩy (tự động trích xuất nếu không chỉ định)')
    parser.add_argument('--save-file', action='store_true', help='Lưu bài viết vào file')
    parser.add_argument('--save-db', action='store_true', help='Lưu bài viết vào cơ sở dữ liệu')
    parser.add_argument('--download-images', action='store_true', help='Tải ảnh về máy chủ')
    parser.add_argument('--database', help='Tên cơ sở dữ liệu (mặc định: sử dụng cấu hình trong constants.py hoặc 24hnews)')
    parser.add_argument('--host', default='localhost', help='Địa chỉ máy chủ cơ sở dữ liệu (mặc định: localhost)')
    parser.add_argument('--user', default='root', help='Tên người dùng cơ sở dữ liệu (mặc định: root)')
    parser.add_argument('--password', default='', help='Mật khẩu cơ sở dữ liệu (mặc định: rỗng)')

    args = parser.parse_args()

    # Mặc định lưu vào cả file và database nếu không có tham số nào được chỉ định
    if not args.save_file and not args.save_db:
        args.save_file = True
        args.save_db = True

    # Cập nhật thông tin kết nối cơ sở dữ liệu nếu được chỉ định
    if args.database or args.host != 'localhost' or args.user != 'root' or args.password != '':
        # Import constants module
        try:
            from news_crawler import constants

            # Cập nhật thông tin kết nối
            if args.database:
                constants.DATABASE = args.database
            if args.host != 'localhost':
                constants.HOST = args.host
            if args.user != 'root':
                constants.USER = args.user
            # Luôn cập nhật mật khẩu để đảm bảo sử dụng đúng giá trị
            constants.PASSWORD = args.password

            print(f"Đã cập nhật thông tin kết nối cơ sở dữ liệu: {constants.HOST}/{constants.DATABASE}")
        except ImportError:
            print("Không thể import module constants, sẽ sử dụng thông tin kết nối từ tham số dòng lệnh")
            # Tạo một module constants tạm thời
            import types
            constants_module = types.ModuleType('constants')
            constants_module.HOST = args.host
            constants_module.USER = args.user
            constants_module.PASSWORD = args.password
            constants_module.DATABASE = args.database or '24hnews'
            constants_module.PORT = '3306'

            # Thêm module vào sys.modules
            import sys
            sys.modules['news_crawler.constants'] = constants_module

            print(f"Đã thiết lập thông tin kết nối cơ sở dữ liệu: {constants_module.HOST}/{constants_module.DATABASE}")

    print(f"Crawling URL: {args.url}")

    # Crawl dữ liệu
    data = crawl_dantri(args.url)

    if data:
        # Xử lý danh sách tags
        tags = None
        if args.tags:
            # Sử dụng tags từ tham số dòng lệnh nếu có
            tags = [tag.strip() for tag in args.tags.split(',') if tag.strip()]
        elif 'tags' in data and data['tags']:
            # Sử dụng tags tự động trích xuất từ bài viết
            tags = data['tags']

        if tags:
            print(f"Tags: {tags}")

        # Xác định category_id và subcategory_id
        category_id = args.category
        subcategory_id = args.subcategory

        # Nếu không chỉ định category_id, tự động xác định từ dữ liệu
        if category_id is None and 'category_name' in data and data['category_name']:
            auto_category_id, auto_subcategory_id = get_category_ids(
                data['category_name'],
                data.get('subcategory_name')
            )

            if auto_category_id:
                category_id = auto_category_id
                print(f"Đã tự động xác định category_id: {category_id} ('{data['category_name']}')")

                # Chỉ sử dụng subcategory_id tự động nếu không chỉ định
                if subcategory_id is None and auto_subcategory_id:
                    subcategory_id = auto_subcategory_id
                    print(f"Đã tự động xác định subcategory_id: {subcategory_id} ('{data['subcategory_name']}')")
            else:
                print(f"Không tìm thấy category_id cho '{data['category_name']}' trong cơ sở dữ liệu")
                # Tạo category mới với moderator_id
                # Sử dụng random moderator_id từ [5, 6]
                random_moderator_id = random.choice([5, 6])
                new_category_id = create_category(data['category_name'], moderator_id=random_moderator_id)
                if new_category_id:
                    category_id = new_category_id
                    print(f"Đã tạo category mới với ID: {category_id}")

                    # Tạo subcategory nếu có
                    if subcategory_id is None and data.get('subcategory_name'):
                        # Subcategory chỉ cần parent_id, không cần moderator_id
                        new_subcategory_id = create_category(data['subcategory_name'], parent_id=category_id)
                        if new_subcategory_id:
                            subcategory_id = new_subcategory_id
                            print(f"Đã tạo subcategory mới với ID: {subcategory_id}")

        # Sử dụng giá trị mặc định nếu vẫn không xác định được
        if category_id is None:
            # Thử tạo category mặc định với random moderator_id
            random_moderator_id = random.choice([5, 6])
            default_category_id = create_category("Uncategorized", moderator_id=random_moderator_id)
            if default_category_id:
                category_id = default_category_id
            else:
                category_id = 2  # Mặc định: 2
                print(f"Sử dụng category_id mặc định: {category_id}")

        # Hiển thị thông tin về subcategory nếu có
        if 'subcategory_name' in data and data['subcategory_name'] and subcategory_id is None:
            print(f"Không tìm thấy subcategory_id cho '{data['subcategory_name']}' trong cơ sở dữ liệu")
            # Tạo subcategory mới nếu có category_id
            if category_id:
                # Subcategory chỉ cần parent_id, không cần moderator_id
                new_subcategory_id = create_category(data['subcategory_name'], parent_id=category_id)
                if new_subcategory_id:
                    subcategory_id = new_subcategory_id
                    print(f"Đã tạo subcategory mới '{data['subcategory_name']}' với ID: {subcategory_id}")

        # Lưu vào file nếu được yêu cầu
        if args.save_file:
            save_to_file(data)

        # Lưu vào cơ sở dữ liệu nếu được yêu cầu
        if args.save_db:
            article_id = save_to_database(
                data,
                author_id=args.author,
                admin_id=args.admin,
                moderator_id=args.moderator,
                user_id=args.normal_user,
                category_id=category_id,
                subcategory_id=subcategory_id,
                tags=tags,
                download_images=args.download_images
            )
            if article_id:
                print(f"Bạn có thể xem trước bài viết bằng cách chạy: python preview_content.py {article_id}")
    else:
        print("Không thể crawl dữ liệu từ URL này.")

if __name__ == "__main__":
    main()
