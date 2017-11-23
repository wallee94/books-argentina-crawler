import re
import scrapy


class ParadigmaSpider(scrapy.Spider):
    name = "paradigmalibros.com"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.details_headers = {
            "Host": "www.paradigmalibros.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }

    def start_requests(self):
        urls = ['https://www.paradigmalibros.com/sitemap_' + str(i) + '.xml' for i in range(0,20)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        response.selector.register_namespace('d', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        locs = response.selector.xpath("//d:loc/text()")

        for loc in locs:
            url = loc.extract()
            if "bookId" in url:
                url = url.replace("http:", "https:")
                yield scrapy.Request(url=url, callback=self.parse_details, headers=self.details_headers)

    def parse_details(self, response):
        data = {
            "url": response.url,
            "title": self.clean_text(response.selector.xpath('//div[@class="detInfoP"]/h1/text()').extract_first()),
            "content": "",
            "author": self.clean_text(response.selector.xpath("//div/span/p/a[@href]/text()").extract_first()),
            "editorial": self.clean_text(response.selector.xpath('//p[contains(text(),"Editorial")]/a[@title]/text()').extract_first()),
            "price": self.clean_price(response.selector.xpath('//div/p[@style]/text()').extract_first()),
            "ISBN": self.clean_text(response.selector.xpath('//p/span/text()').extract_first().split(":")[-1].strip())
        }

        yield data

    def clean_text(self, text):
        print(text)
        if not isinstance(text, str):
            return "asd"
        text = re.sub("[\n\t]+", "", text)
        text = re.sub("\s+", " ", text)
        return text

    def clean_price(self, price):
        if not isinstance(price, str):
            return "-1"
        res = ""
        for c in price:
            if c.isdigit() or c == ".":
                res += c
        return res
