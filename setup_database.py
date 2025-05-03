import mysql.connector
from news_crawler import constants

def setup_database():
    # Kết nối đến MySQL server
    try:
        # Kết nối không chỉ định database
        conn = mysql.connector.connect(
            host=constants.HOST,
            user=constants.USER,
            password=constants.PASSWORD,
            port=constants.PORT
        )

        cursor = conn.cursor()

        # Tạo database nếu chưa tồn tại
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {constants.DATABASE}")
        cursor.execute(f"USE {constants.DATABASE}")

        # Tạo bảng websites
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS websites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            domain VARCHAR(255) NOT NULL,
            categories JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)

        # Tạo bảng x_path_categories
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS x_path_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            website_id INT NOT NULL,
            xpath_category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites(id)
        )
        """)

        # Tạo bảng x_path_contents
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS x_path_contents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            website_id INT NOT NULL,
            xpath_title TEXT NOT NULL,
            xpath_content TEXT NOT NULL,
            xpath_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites(id)
        )
        """)

        # Thêm dữ liệu mẫu cho vietnamnet.vn
        cursor.execute("""
        INSERT INTO websites (domain, categories)
        VALUES ('https://vietnamnet.vn', '[\"/vn/thoi-su/\", \"/vn/kinh-doanh/\", \"/vn/giai-tri/\", \"/vn/the-gioi/\"]')
        """)

        website_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO x_path_categories (website_id, xpath_category)
        VALUES (%s, '//div[contains(@class, \"clearfix\")]')
        """, (website_id,))

        cursor.execute("""
        INSERT INTO x_path_contents (website_id, xpath_title, xpath_content, xpath_date)
        VALUES (%s, '//h1[contains(@class, \"title\")]', '//div[contains(@class, \"ArticleContent\")]', '//span[contains(@class, \"ArticleDate\")]')
        """, (website_id,))

        # Thêm dữ liệu mẫu cho kenh14.vn
        cursor.execute("""
        INSERT INTO websites (domain, categories)
        VALUES ('https://kenh14.vn', '[\"/star\", \"/musik\", \"/tv-show\", \"/cine\"]')
        """)

        website_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO x_path_categories (website_id, xpath_category)
        VALUES (%s, '//div[contains(@class, \"list-news-fp\")]')
        """, (website_id,))

        cursor.execute("""
        INSERT INTO x_path_contents (website_id, xpath_title, xpath_content, xpath_date)
        VALUES (%s, '//h1[contains(@class, \"kbwc-title\")]', '//div[contains(@class, \"knc-content\")]', '//span[contains(@class, \"kbwc-time\")]')
        """, (website_id,))

        # Thêm dữ liệu mẫu cho vnexpress.net
        cursor.execute("""
        INSERT INTO websites (domain, categories)
        VALUES ('https://vnexpress.net', '[\"/thoi-su\", \"/the-gioi\", \"/kinh-doanh\", \"/bat-dong-san\", \"/giai-tri\"]')
        """)

        website_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO x_path_categories (website_id, xpath_category)
        VALUES (%s, '//article[contains(@class, \"item-news\")]')
        """, (website_id,))

        cursor.execute("""
        INSERT INTO x_path_contents (website_id, xpath_title, xpath_content, xpath_date)
        VALUES (%s, '//h1[contains(@class, \"title-detail\")]', '//article[contains(@class, \"fck_detail\")]', '//span[contains(@class, \"date\")]')
        """, (website_id,))

        conn.commit()
        print("Đã thiết lập cơ sở dữ liệu thành công!")

    except Exception as e:
        print(f"Lỗi khi thiết lập cơ sở dữ liệu: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()
