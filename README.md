# Dự án Crawl Bài Báo

Dự án này sử dụng Scrapy và các thư viện Python khác để crawl bài báo từ nhiều trang web tin tức khác nhau. Dự án được thiết kế để chạy theo yêu cầu, không cần lịch chạy tự động.

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

2. Thiết lập cơ sở dữ liệu MySQL:
- Đảm bảo MySQL đã được cài đặt và đang chạy
- Nhập dữ liệu từ file SQL:
```
mysql -u root -p < "news_crawler/24hnews (2).sql"
```
- Hoặc sử dụng phpMyAdmin để nhập file SQL

3. Cập nhật thông tin kết nối cơ sở dữ liệu:
- Trong file `news_crawler/constants.py` (cho Scrapy)
- Trong file `vnexpress_to_db.py` (cho script crawl trực tiếp)

## Cấu trúc dự án

- `news_crawler/`: Thư mục chính của dự án Scrapy
  - `spiders/`: Chứa các spider để crawl dữ liệu
    - `news_spider.py`: Spider chính để crawl bài báo
  - `items.py`: Định nghĩa cấu trúc dữ liệu bài báo
  - `pipelines.py`: Xử lý dữ liệu sau khi crawl
  - `settings.py`: Cài đặt cho dự án Scrapy
  - `constants.py`: Thông tin kết nối cơ sở dữ liệu
  - `connector.py`: Các hàm kết nối và truy vấn cơ sở dữ liệu
- `run_crawler.py`: Script để chạy crawler cho tất cả các trang web
- `crawl_url.py`: Script để crawl một URL cụ thể sử dụng Scrapy
- `simple_crawler.py`: Script đơn giản để crawl bài báo từ VnExpress và lưu vào file
- `vnexpress_to_db.py`: Script để crawl bài báo từ VnExpress và lưu vào cơ sở dữ liệu (giữ nguyên định dạng HTML)
- `vnexpress_category_crawler.py`: Script để crawl nhiều bài báo từ một danh mục của VnExpress
- `dantri_to_db.py`: Script để crawl bài báo từ Dân Trí và lưu vào cơ sở dữ liệu (giữ nguyên định dạng HTML)
- `dantri_category_crawler.py`: Script để crawl nhiều bài báo từ một danh mục của Dân Trí
- `preview_content.py`: Script để kiểm tra nội dung HTML đã crawl với TinyMCE
- `setup_database.py`: Script để thiết lập cơ sở dữ liệu cho Scrapy
- `requirements.txt`: Danh sách các thư viện cần thiết

## Cách sử dụng

### Phương pháp 1: Crawl một bài báo từ VnExpress và lưu vào cơ sở dữ liệu

```
python vnexpress_to_db.py https://vnexpress.net/nguoi-my-can-kiem-it-nhat-114-000-usd-moi-nam-de-mua-duoc-nha-4881179.html --download-images
```

Tham số tùy chọn:
- `--author`: ID của tác giả (mặc định: 4)
- `--category`: ID của danh mục (mặc định: 2)
- `--download-images`: Tải ảnh về và lưu vào thư mục storage/uploads

Script này sẽ giữ nguyên định dạng HTML của nội dung bài viết, phù hợp để hiển thị trong TinyMCE. Nếu sử dụng tham số `--download-images`, script sẽ tải tất cả các ảnh về và lưu vào thư mục `storage/uploads`, đồng thời cập nhật đường dẫn ảnh trong nội dung HTML.

Sau khi crawl, bạn có thể kiểm tra nội dung HTML với script `preview_content.py`:

```
python preview_content.py [article_id]
```

Ví dụ:
```
python preview_content.py 100
```

Script này sẽ tạo một file HTML trong thư mục `preview/` để bạn có thể mở trong trình duyệt và kiểm tra nội dung với TinyMCE.

### Phương pháp 1.1: Crawl một bài báo từ Dân Trí và lưu vào cơ sở dữ liệu

```
python dantri_to_db.py https://dantri.com.vn/giao-duc/bo-hoc-sinh-gioi-tieu-hoc-hoc-sinh-tien-tien-thcs-nam-hoc-2024-2025-20250430222310486.htm --download-images
```

Tham số tùy chọn:
- `--author`: ID của tác giả (mặc định: 4)
- `--category`: ID của danh mục (mặc định: 2)
- `--save-file`: Lưu bài viết vào file
- `--save-db`: Lưu bài viết vào cơ sở dữ liệu
- `--download-images`: Tải ảnh về và lưu vào thư mục storage/uploads

Mặc định, script sẽ lưu bài viết vào cả file và cơ sở dữ liệu. Nội dung HTML sẽ được giữ nguyên định dạng, phù hợp để hiển thị trong TinyMCE. Nếu sử dụng tham số `--download-images`, script sẽ tải tất cả các ảnh về và lưu vào thư mục `storage/uploads`, đồng thời cập nhật đường dẫn ảnh trong nội dung HTML.

### Phương pháp 2: Crawl nhiều bài báo từ một danh mục của VnExpress

```
python vnexpress_category_crawler.py https://vnexpress.net/thoi-su
```

Tham số tùy chọn:
- `--limit`: Số lượng bài viết tối đa cần crawl (mặc định: 10)
- `--author`: ID của tác giả (mặc định: 4)
- `--category`: ID của danh mục (mặc định: 2)
- `--delay`: Thời gian chờ giữa các lần crawl (giây) (mặc định: 2)

### Phương pháp 2.1: Crawl nhiều bài báo từ một danh mục của Dân Trí

```
python dantri_category_crawler.py https://dantri.com.vn/giao-duc.htm
```

Tham số tùy chọn:
- `--limit`: Số lượng bài viết tối đa cần crawl (mặc định: 10)
- `--author`: ID của tác giả (mặc định: 4)
- `--category`: ID của danh mục (mặc định: 2)
- `--delay`: Thời gian chờ giữa các lần crawl (giây) (mặc định: 2)
- `--save-file`: Lưu bài viết vào file
- `--save-db`: Lưu bài viết vào cơ sở dữ liệu

Mặc định, script sẽ lưu bài viết vào cả file và cơ sở dữ liệu.

### Phương pháp 3: Sử dụng script đơn giản (Lưu vào file)

Cách đơn giản nhất để crawl một bài báo từ VnExpress và lưu vào file:

```
python simple_crawler.py https://vnexpress.net/nguoi-my-can-kiem-it-nhat-114-000-usd-moi-nam-de-mua-duoc-nha-4881179.html
```

Kết quả sẽ được lưu trong thư mục `crawled_data/` dưới dạng file JSON và TXT.

### Phương pháp 4: Sử dụng Scrapy để crawl một URL cụ thể

```
python crawl_url.py https://vnexpress.net/nguoi-my-can-kiem-it-nhat-114-000-usd-moi-nam-de-mua-duoc-nha-4881179.html
```

### Phương pháp 5: Crawl tất cả các trang web đã cấu hình trong cơ sở dữ liệu

1. Chạy crawler:
```
python run_crawler.py
```

2. Hoặc sử dụng lệnh Scrapy trực tiếp:
```
scrapy crawl news
```

## Cấu trúc cơ sở dữ liệu

### Bảng `articles`
- `article_id`: ID của bài viết
- `code`: Mã bài viết
- `title`: Tiêu đề bài viết
- `slug`: Slug của bài viết
- `content`: Nội dung bài viết
- `preview_content`: Nội dung xem trước
- `contains_sensitive_content`: Có chứa nội dung nhạy cảm không
- `author_id`: ID của tác giả
- `category_id`: ID của danh mục
- `subcategory_id`: ID của danh mục con
- `thumbnail_url`: URL của ảnh đại diện
- `status`: Trạng thái bài viết (draft, pending, published, archived, rejected)
- `views`: Số lượt xem
- `approved_by`: ID của người duyệt
- `created_at`: Thời gian tạo
- `updated_at`: Thời gian cập nhật

### Bảng `approvals`
- `approval_id`: ID của bản ghi phê duyệt
- `type`: Loại phê duyệt
- `article_id`: ID của bài viết
- `user_id`: ID của người dùng
- `status`: Trạng thái phê duyệt (pending, approved, rejected)
- `remarks`: Ghi chú
- `created_at`: Thời gian tạo
- `updated_at`: Thời gian cập nhật

### Bảng cấu hình Scrapy
1. Bảng `websites`: Lưu thông tin về các trang web cần crawl
   - `id`: ID của website
   - `domain`: Tên miền của website (ví dụ: https://vietnamnet.vn)
   - `categories`: Danh sách các danh mục cần crawl (định dạng JSON)

2. Bảng `x_path_categories`: Lưu XPath để lấy danh sách bài viết từ trang danh mục
   - `id`: ID của bản ghi
   - `website_id`: ID của website
   - `xpath_category`: XPath để lấy phần tử chứa danh sách bài viết

3. Bảng `x_path_contents`: Lưu XPath để lấy nội dung bài viết
   - `id`: ID của bản ghi
   - `website_id`: ID của website
   - `xpath_title`: XPath để lấy tiêu đề bài viết
   - `xpath_content`: XPath để lấy nội dung bài viết
   - `xpath_date`: XPath để lấy ngày đăng bài viết

## Các trang web được hỗ trợ

1. VnExpress (https://vnexpress.net)
2. VietnamNet (https://vietnamnet.vn)
3. Kenh14 (https://kenh14.vn)
4. Dân Trí (https://dantri.com.vn)
