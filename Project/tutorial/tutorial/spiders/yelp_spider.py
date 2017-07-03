import scrapy
import json
from scrapy.contrib.linkextractors import LinkExtractor

DOMAIN = 'yelp.com'
class YelpSpider(scrapy.Spider):
    name = "yelp"
    allowed_domains = [DOMAIN]
    start_urls = [
        # 'https://www.yelp.com/biz/rail-stop-restaurant-and-bar-boston-3',
        # 'https://www.yelp.com/biz/neptune-oyster-boston',
        # 'https://www.yelp.com/biz/monicas-mercato-boston-3',
        # 'https://www.yelp.com/biz/nirvana-the-taste-of-india-cambridge',
        'https://www.yelp.com/biz/monkey-cafe-d-k-y-%E6%B8%8B%E8%B0%B7%E5%8C%BA',
    ]

    def parse(self, response):
        # information = response.css('script[type="application/ld+json"]').extract_first()
        def getPostalCode(response):
            script = response.css('script[type="application/ld+json"]::text').extract_first()
            script_parse = json.loads(script)
            print('#################### PostalCode: %s' % script_parse['address']['postalCode'])
            return script_parse['address']['postalCode']
        def getCountry(response):
            script = response.css('script[type="application/ld+json"]::text').extract_first()
            script_parse = json.loads(script)
            print('#################### Address Country: %s' % script_parse['address']['addressCountry'])
            return script_parse['address']['addressCountry']
        def getLatitude(response):
            mapstate = response.css('div.lightbox-map::attr(data-map-state)').extract_first()
            mapstate_parse = json.loads(mapstate)
            return mapstate_parse['center']['latitude']
        def getLongitude(response):
            mapstate = response.css('div.lightbox-map::attr(data-map-state)').extract_first()
            mapstate_parse = json.loads(mapstate)
            return mapstate_parse['center']['longitude']
        def parse_links(response):
            extractor = LinkExtractor(allow=r'yelp\.com/biz/')
            links = extractor.extract_links(response)
            print('##################################################################')
            print(links)
            return links
        yield {
                'Name': response.css('h1.biz-page-title::text').extract_first().strip(),
                'Address': response.css('div.map-box-address strong.street-address address::text').extract_first().strip(),
                'Phone': response.css('span.biz-phone::text').extract_first().strip(),
                'PostalCode': getPostalCode(response),
                'Country' : getCountry(response),
                'Latitude' : getLatitude(response),
                'Longitude' : getLongitude(response),
            }
        parse_links(response)
        # script = response.css('script[type="application/ld+json"]::text').extract_first()
        # script_parse = json.loads(script)
        # print('#################### PostalCode: %s' % script_parse['address']['postalCode'])
        # print('#################### Address Country: %s' % script_parse['address']['addressCountry'])

        # mapstate = response.css('div.lightbox-map::attr(data-map-state)').extract_first()
        # mapstate_parse = json.loads(mapstate)
        # latitude = mapstate_parse['center']['latitude']
        # longitude = mapstate_parse['center']['longitude']
        # print('######################Location of this Restaurant is: %s : %s' % (latitude, longitude) ) 