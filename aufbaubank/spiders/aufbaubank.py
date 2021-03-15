import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from aufbaubank.items import Article


class AufbaubankSpider(scrapy.Spider):
    name = 'aufbaubank'
    start_urls = ['https://www.aufbaubank.de/?p=289&ajaxReq=news&tag_id=0&loaded_news=0']
    page = 1

    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)
            self.page += 1
            next_page = f'https://www.aufbaubank.de/?p=289&ajaxReq=news&tag_id=0&loaded_news={(self.page-1)*10}'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
