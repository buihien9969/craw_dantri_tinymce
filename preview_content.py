"""
Script để kiểm tra nội dung HTML đã crawl và hiển thị nó trong TinyMCE
"""

import argparse
import mysql.connector
import os
import sys

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

def get_article_content(article_id):
    """
    Lấy nội dung bài viết từ cơ sở dữ liệu
    """
    conn = connect_to_database()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT title, content, thumbnail_url FROM articles WHERE article_id = %s", (article_id,))
        article = cursor.fetchone()

        if not article:
            print(f"Không tìm thấy bài viết với ID: {article_id}")
            return None

        return article

    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ cơ sở dữ liệu: {e}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_preview_html(article, article_id):
    """
    Tạo file HTML để xem trước nội dung với TinyMCE

    Args:
        article (dict): Thông tin bài viết
        article_id (int): ID của bài viết
    """
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Xem trước nội dung: {article['title']}</title>
    <script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/5/tinymce.min.js" referrerpolicy="origin"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #444;
            font-size: 20px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .thumbnail-container {{
            margin-bottom: 20px;
            text-align: center;
        }}
        .thumbnail-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            padding: 5px;
            border-radius: 3px;
        }}
        .instructions {{
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #007bff;
            margin-bottom: 20px;
        }}
        .editor-container {{
            border: 1px solid #ddd;
            border-radius: 3px;
            overflow: hidden;
        }}
    </style>
    <script>
        tinymce.init({{
            selector: '#editor',
            height: 600,
            plugins: [
                'advlist autolink lists link image charmap print preview anchor',
                'searchreplace visualblocks code fullscreen',
                'insertdatetime media table paste code help wordcount'
            ],
            toolbar: 'undo redo | formatselect | fontsizeselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
            content_style: 'body {{ font-family:Helvetica,Arial,sans-serif; font-size:18px }}',
            font_size_formats: '8pt 10pt 12pt 14pt 16pt 18pt 20pt 22pt 24pt 26pt 28pt 36pt 48pt 72pt'
        }});
    </script>
</head>
<body>
    <div class="container">
        <h1>Xem trước nội dung: {article['title']}</h1>

        <div class="thumbnail-container">
            <h2>Thumbnail:</h2>
            {f'<img src="/{article["thumbnail_url"]}" />' if article.get('thumbnail_url') else '<p>Không có thumbnail</p>'}
        </div>

        <div class="instructions">
            <p>Nội dung HTML đã được crawl và lưu vào cơ sở dữ liệu. Bạn có thể kiểm tra định dạng dưới đây.</p>
            <p>Sử dụng công cụ <strong>Font Size</strong> trong thanh công cụ để thay đổi cỡ chữ.</p>
        </div>

        <div class="editor-container">
            <textarea id="editor">{article['content']}</textarea>
        </div>

        <p>Nếu nội dung hiển thị đúng định dạng trong TinyMCE, điều đó có nghĩa là HTML đã được lưu đúng cách.</p>
    </div>
</body>
</html>"""

    # Tạo thư mục nếu chưa tồn tại
    os.makedirs('preview', exist_ok=True)

    # Lưu file HTML
    preview_file = f"preview/article_{article_id}.html"
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return preview_file

def main():
    """
    Hàm chính
    """
    parser = argparse.ArgumentParser(description='Kiểm tra nội dung HTML đã crawl và hiển thị nó trong TinyMCE')
    parser.add_argument('article_id', type=int, help='ID của bài viết cần kiểm tra')

    args = parser.parse_args()

    print(f"Đang lấy nội dung bài viết với ID: {args.article_id}")

    # Lấy nội dung bài viết
    article = get_article_content(args.article_id)

    if article:
        # Tạo file HTML để xem trước
        preview_file = create_preview_html(article, args.article_id)

        print(f"Đã tạo file xem trước: {preview_file}")
        print(f"Mở file này trong trình duyệt để kiểm tra nội dung với TinyMCE.")
    else:
        print("Không thể lấy nội dung bài viết.")

if __name__ == "__main__":
    main()
