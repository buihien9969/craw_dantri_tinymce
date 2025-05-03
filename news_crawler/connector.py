import mysql.connector
from news_crawler import constants

def get_connection():
    try:
        db = mysql.connector.connect(
            host=constants.HOST,
            user=constants.USER,
            password=constants.PASSWORD,
            database=constants.DATABASE,
            port=constants.PORT
        )
        return db
    except Exception as e:
        print(f"Lỗi kết nối đến cơ sở dữ liệu: {e}")
        return None

# Lấy tất cả website từ cơ sở dữ liệu
def get_all_websites():
    db = get_connection()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM websites")
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append(row)
    
    cursor.close()
    db.close()
    return result

# Lấy tất cả danh mục của website
def get_categories(website_id):
    db = get_connection()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM x_path_categories WHERE website_id = %s", (website_id,))
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append(row[2])
    
    cursor.close()
    db.close()
    return result

# Lấy x_path của tiêu đề, nội dung, ngày đăng của website
def get_contents(website_id):
    db = get_connection()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM x_path_contents WHERE website_id = %s", (website_id,))
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({"title": row[2], "content": row[3], "date": row[4]})
    
    cursor.close()
    db.close()
    return result
