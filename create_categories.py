"""
Script để tạo các danh mục (categories) trong cơ sở dữ liệu
"""

import mysql.connector
import datetime
from slugify import slugify

def connect_to_database():
    """
    Kết nối đến cơ sở dữ liệu
    """
    try:
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

def create_categories():
    """
    Tạo các danh mục trong cơ sở dữ liệu
    """
    conn = connect_to_database()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

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
                description TEXT,
                parent_id INT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories(category_id) ON DELETE CASCADE
            )
            """)
            print("Đã tạo bảng categories")

        # Danh sách các danh mục chính
        main_categories = [
            {"name": "Thời sự", "description": "Tin tức thời sự trong nước và quốc tế"},
            {"name": "Thế giới", "description": "Tin tức quốc tế, thời sự thế giới"},
            {"name": "Kinh doanh", "description": "Tin tức kinh tế, tài chính, kinh doanh"},
            {"name": "Bất động sản", "description": "Thông tin về thị trường bất động sản"},
            {"name": "Thể thao", "description": "Tin tức thể thao trong nước và quốc tế"},
            {"name": "Lao động - Việc làm", "description": "Thông tin về thị trường lao động"},
            {"name": "Sức khỏe", "description": "Thông tin y tế, sức khỏe, phòng bệnh"},
            {"name": "Văn hóa", "description": "Tin tức văn hóa, nghệ thuật"},
            {"name": "Giải trí", "description": "Tin tức giải trí, showbiz"},
            {"name": "Ô tô - Xe máy", "description": "Thông tin về ô tô, xe máy"},
            {"name": "Sức mạnh số", "description": "Tin tức công nghệ số"},
            {"name": "Du lịch", "description": "Thông tin du lịch, địa điểm du lịch"},
            {"name": "Đời sống", "description": "Thông tin đời sống xã hội"},
            {"name": "Tình yêu - Giới tính", "description": "Thông tin về tình yêu, giới tính"},
            {"name": "Khoa học - Công nghệ", "description": "Tin tức khoa học, công nghệ"},
            {"name": "Xã hội", "description": "Tin tức xã hội"},
            {"name": "Giáo dục", "description": "Tin tức giáo dục, đào tạo"}
        ]

        # Danh sách các danh mục con
        sub_categories = {
            "Thời sự": ["Chính trị", "Dân sinh", "Lao động - Việc làm", "Giao thông", "Mekong"],
            "Thế giới": ["Quân sự", "Tư liệu", "Phân tích", "Người Việt 4 phương", "Chuyện lạ"],
            "Kinh doanh": ["Tài chính", "Chứng khoán", "Doanh nghiệp", "Khởi nghiệp", "Tiêu dùng"],
            "Bất động sản": ["Dự án", "Thị trường", "Nhà đất", "Không gian sống"],
            "Thể thao": ["Bóng đá Việt Nam", "Bóng đá Anh", "Bóng đá Tây Ban Nha", "Bóng đá Ý", "Bóng đá Đức", "Bóng đá Pháp", "Tennis", "Golf", "Võ thuật"],
            "Sức khỏe": ["Làm đẹp", "Khỏe đẹp mỗi ngày", "Giới tính", "Dinh dưỡng", "Bệnh thường gặp"],
            "Văn hóa": ["Đời sống văn hóa", "Điện ảnh", "Âm nhạc", "Sách", "Mỹ thuật"],
            "Giải trí": ["Sao Việt", "Sao châu Á", "Sao Hollywood"],
            "Giáo dục": ["Tuyển sinh", "Du học", "Chọn nghề", "Chọn trường", "Học tiếng Anh"]
        }

        # Thêm các danh mục chính
        for category in main_categories:
            name = category["name"]
            slug = slugify(name)
            description = category["description"]

            # Kiểm tra xem danh mục đã tồn tại chưa
            cursor.execute("SELECT category_id FROM categories WHERE slug = %s", (slug,))
            existing_category = cursor.fetchone()

            if not existing_category:
                # Thêm danh mục mới
                cursor.execute("""
                INSERT INTO categories (name, slug, description, parent_id, created_at, updated_at)
                VALUES (%s, %s, %s, NULL, %s, %s)
                """, (name, slug, description, datetime.datetime.now(), datetime.datetime.now()))
                print(f"Đã thêm danh mục: {name}")
            else:
                print(f"Danh mục '{name}' đã tồn tại")

        # Thêm các danh mục con
        for parent_name, sub_cats in sub_categories.items():
            # Lấy ID của danh mục cha
            cursor.execute("SELECT category_id FROM categories WHERE name = %s", (parent_name,))
            parent_result = cursor.fetchone()

            if not parent_result:
                print(f"Không tìm thấy danh mục cha: {parent_name}")
                continue

            parent_id = parent_result[0]

            # Thêm các danh mục con
            for sub_name in sub_cats:
                sub_slug = slugify(sub_name)
                
                # Kiểm tra xem danh mục con đã tồn tại chưa
                cursor.execute("SELECT category_id FROM categories WHERE slug = %s AND parent_id = %s", (sub_slug, parent_id))
                existing_sub = cursor.fetchone()

                if not existing_sub:
                    # Thêm danh mục con mới
                    cursor.execute("""
                    INSERT INTO categories (name, slug, description, parent_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, (sub_name, sub_slug, f"Danh mục con của {parent_name}", parent_id, datetime.datetime.now(), datetime.datetime.now()))
                    print(f"Đã thêm danh mục con: {sub_name} (thuộc {parent_name})")
                else:
                    print(f"Danh mục con '{sub_name}' (thuộc {parent_name}) đã tồn tại")

        conn.commit()
        print("Đã tạo các danh mục thành công!")
        return True

    except Exception as e:
        print(f"Lỗi khi tạo danh mục: {e}")
        conn.rollback()
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_categories()
