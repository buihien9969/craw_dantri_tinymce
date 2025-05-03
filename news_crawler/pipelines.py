from itemadapter import ItemAdapter
import json

class NewsCrawlerPipeline:
    def process_item(self, item, spider):
        # Ở đây bạn có thể lưu dữ liệu vào file JSON hoặc cơ sở dữ liệu
        # Trong ví dụ này, chúng ta sẽ in ra màn hình để kiểm tra
        print(f"Đã crawl bài viết: {item['title']}")
        return item

# Nếu bạn muốn lưu vào file JSON, bạn có thể sử dụng đoạn code sau:
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('news_items.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True
        
    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()
        
    def process_item(self, item, spider):
        line = ItemAdapter(item).asdict()
        line_json = json.dumps(line, ensure_ascii=False)
        
        if self.first_item:
            self.first_item = False
        else:
            self.file.write(',\n')
            
        self.file.write(line_json)
        return item
