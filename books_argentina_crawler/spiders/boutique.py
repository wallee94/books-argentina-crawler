import re
import scrapy


class BoutiqueDelLibroSpider(scrapy.Spider):
    name = "boutiquedellibro.com"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.details_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }

    def start_requests(self):
        urls = ['https://www.boutiquedellibro.com.ar/sitemap' + str(i) + '.xml' for i in range(0,6)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        response.selector.register_namespace('d', 'http://www.google.com/schemas/sitemap/0.9')
        locs = response.selector.xpath("//d:loc/text()")

        for loc in locs:
            url = loc.extract()
            url = url.replace("http:", "https:")
            if "resultados.aspx" not in url:
                yield scrapy.Request(url=url, callback=self.parse_details, headers=self.details_headers)

    def parse_details(self, response):
        # we don't want ebooks
        format = response.selector.xpath("//h3/span/text()").extract_first()
        if format and format.strip().lower() == "libro digital":
            return

        data = {
            "url": response.url,
            "title": self.clean_text(response.selector.xpath('//div/h1/a[@href]/text()').extract_first()),
            "content": "",
            "author": self.clean_text(response.selector.xpath("//p/span/a[@href]/text()").extract_first()),
            "editorial": self.clean_text(response.selector.xpath('//li/span/a[@href]/text()').extract_first()),
            "price_arg": self.clean_price(response.selector.xpath('//div/p/span[@class]/text()').extract_first()),
            "ISBN": self.clean_isbn(response.selector.xpath('//li/span[@itemprop="isbn"]/text()').extract_first())
        }

        if data["ISBN"]:
            data["ISBN"] = data["ISBN"].split(":")[-1].strip()
        else:
            return

        yield data

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = re.sub("[\n\t]+", "", text)
        text = re.sub("\s+", " ", text)
        return text

    def clean_isbn(self, text):
        if not isinstance(text, str):
            return ""
        return re.sub(r"[^\d]", "", text)

    def clean_price(self, price):
        if not isinstance(price, str):
            return "-1"
        cents = price.split(",")[-1]
        price = re.sub(r"[^\d]", "", price)
        price = price[:-2] + "." + cents

        return price