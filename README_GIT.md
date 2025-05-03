# Hướng dẫn đưa dự án lên GitHub

Dự án này đã được chuẩn bị để đưa lên GitHub. Dưới đây là các bước để thực hiện:

## Bước 1: Khởi tạo Git repository

Chạy file `setup_git.bat` bằng cách nhấp đúp vào nó. File này sẽ:
- Khởi tạo Git repository
- Thêm tất cả các file vào staging area
- Commit các thay đổi với message "Initial commit"

## Bước 2: Tạo repository trên GitHub

1. Truy cập [GitHub](https://github.com) và đăng nhập vào tài khoản của bạn
2. Nhấn vào nút "New" (hoặc dấu + ở góc trên bên phải) để tạo repository mới
3. Đặt tên cho repository (ví dụ: "news-crawler")
4. Thêm mô tả (tùy chọn)
5. Chọn "Public" hoặc "Private" tùy theo nhu cầu của bạn
6. **QUAN TRỌNG**: KHÔNG chọn "Initialize this repository with a README"
7. Nhấn "Create repository"

## Bước 3: Đẩy code lên GitHub

Sau khi tạo repository trên GitHub, bạn sẽ thấy URL của repository. Chạy file `push_to_github.bat` bằng cách nhấp đúp vào nó và nhập URL repository khi được yêu cầu.

File này sẽ:
- Kết nối repository local với repository remote
- Đẩy code lên GitHub

## Bước 4: Kiểm tra repository trên GitHub

Sau khi hoàn thành các bước trên, truy cập repository của bạn trên GitHub để kiểm tra xem code đã được đưa lên chưa.

## Lưu ý

- Nếu bạn gặp lỗi khi đẩy code lên GitHub, có thể bạn cần xác thực. Nếu bạn đã bật xác thực hai yếu tố, bạn cần tạo Personal Access Token:
  1. Truy cập [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
  2. Nhấn "Generate new token"
  3. Đặt tên cho token và chọn quyền "repo"
  4. Nhấn "Generate token"
  5. Sao chép token và sử dụng nó thay cho mật khẩu khi được yêu cầu

- File `.gitignore` đã được tạo để loại trừ các file không cần thiết như:
  - File cache của Python
  - Thư mục crawled_data
  - Thư mục storage/uploads
  - File cơ sở dữ liệu
  - File tạm

- Để biết thêm chi tiết về các lệnh Git, xem file `GIT_INSTRUCTIONS.md`
