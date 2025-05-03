import scrapy

class NewsItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
