"""
Script để tạo category 'Giáo dục' trong cơ sở dữ liệu
"""

import mysql.connector
from slugify import slugify
import datetime

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

def create_education_category():
    """
    Tạo category 'Giáo dục' trong cơ sở dữ liệu
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
            print("Bảng categories không tồn tại")
            return False

        # Kiểm tra cấu trúc bảng categories
        cursor.execute("SHOW COLUMNS FROM categories")
        columns = [column[0] for column in cursor.fetchall()]
        print("Các cột trong bảng categories:", columns)

        # Kiểm tra xem category 'Giáo dục' đã tồn tại chưa
        category_name = "Giáo dục"
        slug = slugify(category_name)
        cursor.execute("SELECT * FROM categories WHERE slug = %s", (slug,))
        existing_category = cursor.fetchone()

        if existing_category:
            print(f"Category '{category_name}' đã tồn tại")
            return True

        # Tạo câu lệnh SQL động dựa trên cấu trúc bảng
        column_names = []
        values = []

        # Thêm các cột cơ bản
        if "name" in columns:
            column_names.append("name")
            values.append(category_name)

        if "slug" in columns:
            column_names.append("slug")
            values.append(slug)

        if "parent_id" in columns:
            column_names.append("parent_id")
            values.append(None)  # Category chính không có parent

        if "description" in columns:
            column_names.append("description")
            values.append("Tin tức giáo dục, đào tạo")

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
        print(f"SQL: {sql}")
        print(f"Values: {values}")

        cursor.execute(sql, values)
        conn.commit()

        print(f"Đã tạo category '{category_name}' thành công")
        return True

    except Exception as e:
        print(f"Lỗi khi tạo category: {e}")
        conn.rollback()
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_education_category()
