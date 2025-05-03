"""
Script để kiểm tra cấu trúc bảng categories
"""

import mysql.connector

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

def check_categories_table():
    """
    Kiểm tra cấu trúc bảng categories
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
        columns = cursor.fetchall()

        print("Cấu trúc bảng categories:")
        for column in columns:
            print(f"- {column[0]}: {column[1]}")

        # Kiểm tra dữ liệu trong bảng categories
        cursor.execute("SELECT * FROM categories LIMIT 10")
        rows = cursor.fetchall()

        print("\nDữ liệu trong bảng categories:")
        if rows:
            for row in rows:
                print(f"- ID: {row[0]}, Name: {row[1]}")
        else:
            print("Không có dữ liệu trong bảng categories")

        return True

    except Exception as e:
        print(f"Lỗi khi kiểm tra bảng categories: {e}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    check_categories_table()
