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

def create_category(category_name, parent_id=None):
    """
    Tạo danh mục mới nếu chưa tồn tại

    Args:
        category_name (str): Tên của danh mục
        parent_id (int, optional): ID của danh mục cha

    Returns:
        int: ID của danh mục đã tạo hoặc None nếu có lỗi
    """
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

def save_to_database(data, author_id=4, category_id=2, subcategory_id=None, tags=None, download_images=True):
    """
    Lưu dữ liệu vào cơ sở dữ liệu

    Args:
        data (dict): Dữ liệu bài viết
        author_id (int): ID của tác giả
        category_id (int): ID của danh mục
        subcategory_id (int, optional): ID của danh mục con
        tags (list, optional): Danh sách các tag
        download_images (bool): Có tải ảnh về không
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
                        datetime.datetime.now(),
                        datetime.datetime.now()
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
                values.append('pending')

            if "views" in columns:
                column_names.append("views")
                values.append(0)

            column_names.extend(["created_at", "updated_at"])
            values.extend([datetime.datetime.now(), datetime.datetime.now()])

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
                        (article_id, tag_id, datetime.datetime.now(), datetime.datetime.now())
                    )
                    print(f"Đã thêm tag '{tag_name}' cho bài viết")

            conn.commit()
            print(f"Đã lưu bài viết '{data['title']}' vào cơ sở dữ liệu với ID: {article_id}")
            return article_id

        except Exception as e:
            print(f"Lỗi khi kiểm tra cấu trúc bảng: {e}")

            # Sử dụng cấu trúc mặc định nếu có lỗi
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
                                thumbnail_url, status, views, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                subcategory_id,  # subcategory_id
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
                        (article_id, tag_id, datetime.datetime.now(), datetime.datetime.now())
                    )
                    print(f"Đã thêm tag '{tag_name}' cho bài viết")

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
    parser.add_argument('--author', type=int, default=4, help='ID của tác giả (mặc định: 4)')
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
                # Tạo category mới
                new_category_id = create_category(data['category_name'])
                if new_category_id:
                    category_id = new_category_id
                    print(f"Đã tạo category mới với ID: {category_id}")

                    # Tạo subcategory nếu có
                    if subcategory_id is None and data.get('subcategory_name'):
                        new_subcategory_id = create_category(data['subcategory_name'], parent_id=category_id)
                        if new_subcategory_id:
                            subcategory_id = new_subcategory_id
                            print(f"Đã tạo subcategory mới với ID: {subcategory_id}")

        # Sử dụng giá trị mặc định nếu vẫn không xác định được
        if category_id is None:
            # Thử tạo category mặc định
            default_category_id = create_category("Uncategorized")
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
