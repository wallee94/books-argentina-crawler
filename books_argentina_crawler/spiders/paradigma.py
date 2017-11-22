import re
import scrapy


class ParadigmaSpider(scrapy.Spider):
    name = "paradigmalibros.com"

    def start_requests(self):
        urls = ['http://www.paradigmalibros.com/sitemap_' + str(i) for i in range(0,20) + '.xml']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        response.selector.register_namespace('d', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        locs = response.selector.xpath("//d:loc/text()")

        self.details_headers = {
            "Host": "www.paradigmalibros.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        for loc in locs:
            url = loc.extract()
            if "bookId" in url:
                yield scrapy.Request(url=url, callback=self.parse_details, headers=self.details_headers)

    def parse_details(self, response):
        data={
            "url": response.url,
            "title": self.clean_text(response.selector.xpath('//div[@class="detInfoP"]/h1/text()').extract_first()),
            #"content": self.clean_text(response.selector.xpath('//div/p[@itemprop="description"]/text()').extract_first()),
            "author": self.clean_text(response.selector.xpath("//div/span/p/a/text()").extract_first()),
            "editorial": self.clean_text(response.selector.xpath('//p[contains(text(),"Editorial"")]/a/text()').extract_first()),
            "price": self.clean_price(response.selector.xpath('//div/p[@style]/text()').extract_first()),
            "ISBN": self.clean_price(response.selector.xpath('//p/span/text()').extract_first())
        }

        yield data

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
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