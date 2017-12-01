import re
import scrapy


class PlanetaDeLibrosSpider(scrapy.Spider):
    name = "planetadelibros.com.ar"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.details_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }

    def start_requests(self):
        urls = ['https://www.planetadelibros.com.ar/sitemap' + str(i) + '.xml' for i in range(1,13)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        response.selector.register_namespace('d', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        locs = response.selector.xpath("//d:loc/text()")

        for loc in locs:
            url = loc.extract()
            url = url.replace("http:", "https:")
            # if "libro" or "editorial" in url:
            yield scrapy.Request(url=url, callback=self.parse_details, headers=self.details_headers)

    def parse_details(self, response):
        data = {
            "url": response.url,
            "title": self.clean_text(response.selector.xpath('//div[@class="titol"]/h1/text()').extract_first()),
            "content": self.clean_text(response.selector.xpath('//div[@class="frase-mkt"]/p/text()').extract_first()),
            "author": self.clean_text(response.selector.xpath('//div[@class="autors"]/h2/a[@itemprop="author"][1]/text()').extract_first()),
            "editorial": self.clean_text(response.selector.xpath('//div[@class="tematiques-i-coleccions"]/div[@class="segell-nom"]/text()').extract_first()),
            "ISBN": self.clean_isbn(response.selector.xpath('//div[@class]/span[@itemprop="isbn"]/text()').extract_first()),
            "price_arg": self.clean_price(response.selector.xpath('//a[@href]/div[@class="preu"]/text()').extract_first())
        }

        if not data["ISBN"]:
            return

        if data["editorial"]:
            data["editorial"] = data["editorial"].split(":")[-1].strip()

        if not data["author"]:
            data["author"] = self.clean_text(response.selector.xpath('//div[@class="autors"]/h2/text()').extract_first())

        yield data

    def clean_isbn(self, text):
        if not isinstance(text, str):
            return ""
        return re.sub(r"[^\d]", "", text)

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = re.sub("[\n\t]+", "", text)
        text = re.sub("\s+", " ", text)
        return text

    def clean_price(self, price):
        if not isinstance(price, str):
            return "-1"
        price = re.sub(r",", ".", price)
        res = ""
        for c in price:
            if c.isdigit() or c == ".":
                res += c
        return res
