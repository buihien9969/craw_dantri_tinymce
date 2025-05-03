# Hướng dẫn đưa dự án lên Git

## Bước 1: Khởi tạo Git repository và commit code

Chạy file `setup_git.bat` để thực hiện các bước sau:
- Khởi tạo Git repository
- Thêm tất cả các file vào staging area
- Commit các thay đổi

## Bước 2: Tạo repository trên GitHub

1. Truy cập [GitHub](https://github.com) và đăng nhập vào tài khoản của bạn
2. Nhấn vào nút "New" để tạo repository mới
3. Đặt tên cho repository (ví dụ: "news-crawler")
4. Không chọn "Initialize this repository with a README"
5. Nhấn "Create repository"

## Bước 3: Kết nối repository local với repository remote

Sau khi tạo repository trên GitHub, bạn sẽ thấy hướng dẫn để kết nối repository local với repository remote. Thực hiện các lệnh sau trong Command Prompt hoặc PowerShell:

```
git remote add origin https://github.com/YOUR_USERNAME/news-crawler.git
git push -u origin master
```

Thay `YOUR_USERNAME` bằng tên người dùng GitHub của bạn.

## Bước 4: Xác thực với GitHub

Khi thực hiện lệnh `git push`, bạn sẽ được yêu cầu nhập thông tin đăng nhập GitHub. Nhập tên người dùng và mật khẩu của bạn.

Nếu bạn đã bật xác thực hai yếu tố, bạn cần tạo Personal Access Token:
1. Truy cập [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Nhấn "Generate new token"
3. Đặt tên cho token và chọn quyền "repo"
4. Nhấn "Generate token"
5. Sao chép token và sử dụng nó thay cho mật khẩu khi được yêu cầu

## Bước 5: Kiểm tra repository trên GitHub

Sau khi push thành công, truy cập repository của bạn trên GitHub để kiểm tra xem code đã được đưa lên chưa.

## Các lệnh Git cơ bản

- Kiểm tra trạng thái: `git status`
- Thêm file vào staging area: `git add filename` hoặc `git add .` (thêm tất cả)
- Commit thay đổi: `git commit -m "Mô tả thay đổi"`
- Push lên remote repository: `git push`
- Pull từ remote repository: `git pull`
- Tạo branch mới: `git checkout -b tên-branch`
- Chuyển branch: `git checkout tên-branch`
- Xem lịch sử commit: `git log`
