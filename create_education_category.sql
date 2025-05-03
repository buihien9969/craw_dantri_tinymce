-- Kiểm tra xem category 'Giáo dục' đã tồn tại chưa
SELECT * FROM categories WHERE slug = 'giao-duc';

-- Nếu không tồn tại, thêm vào
INSERT INTO categories (name, slug, created_at, updated_at)
SELECT 'Giáo dục', 'giao-duc', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'giao-duc');

-- Kiểm tra lại
SELECT * FROM categories WHERE slug = 'giao-duc';
