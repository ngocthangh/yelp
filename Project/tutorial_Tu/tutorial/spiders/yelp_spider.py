import scrapy
import json
from scrapy.selector import Selector
from tutorial.items import YelpItem
import csv

class YelpSpider(scrapy.Spider):
    name = "yelp"
    allowed_domains = ["yelp.com"]
    start_urls = [
        'https://www.yelp.com/search?cflt=restaurants&find_loc=501'
    ]

    def parse(self, response):
        cr = csv.reader(open(r"D:\Yelp\SVN\trunk\Project\tutorial_Tu\tutorial\spiders\zipcodetest.csv","r"))
        for row in cr:
            while (row[0][0] == '0'):
                row[0] = row[0][+1:]
            print('$$$$$$$$$$$$$$$$$$$$$$$$$ search: %s $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$' %row[0])
            yelp_url  = "https://www.yelp.com/search?cflt=restaurants&find_loc=%s" % row[0].strip()
            print(yelp_url)
            yield response.follow(yelp_url, self.parseSearchPage)

    def parseSearchPage(self, response):
        
        # lists = response.xpath('//script/text()').extract()
        # index=0
        # for list in lists:
        #     if list.find("yelp.www.init.search.Controller") !=-1:
        #         break
        #     index +=1
        # list = lists[index]
        # words = list.replace(' ','').replace('"','').replace('{','').replace('}','').replace(',longitude',':longitude').split(',')
        # coodinate =[]
        # for word in words:
        #     if word.find("location:latitude") !=-1:
        #         word = word.replace('location:','').replace('latitude:','').replace(':longitude:',',')
        #         coodinate.append(word)
                 
        # script_parse = json.loads(list.replace('yelp.www.init.search.Controller(','').replace(');',''))
        # latitude = script['markers']['1']
        # print('------------------ Location: %s ---------------------------' %latitude)
        
        page_links = response.css('a.biz-name::attr(href)')
        count =0
        for href in page_links:
            yield response.follow(href, self.parseDetailPage)
        # next_page = response.css('a.next::attr(href)').extract_first()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parseSearchPage)
        
    def parseDetailPage(self, response):

        script = response.css('script[type="application/ld+json"]::text').extract_first()
        script_parse = json.loads(script)
        print('#################### PostalCode: %s' % script_parse['address']['postalCode'])
        PostalCode = script_parse['address']['postalCode']

        print('#################### Address Country: %s' % script_parse['address']['addressCountry'])
        Country = script_parse['address']['addressCountry']
        
        mapstate = response.css('div.lightbox-map::attr(data-map-state)').extract_first()
        mapstate_parse = json.loads(mapstate)
        Latitude = mapstate_parse['center']['latitude']
        Longitude = mapstate_parse['center']['longitude']
        Location = str(Latitude) + ',' + str(Longitude)
        
        website = response.css('span.biz-website a::text').extract_first()

        Reviews  = response.css('p.quote::text').extract()
        Review = ''
        for rv in Reviews:
            Review = '|'.join(rv.strip())

        Comment = response.css('div.review-content p::text').extract()

        Address = response.css('div.map-box-address strong.street-address address::text').extract()
        for i in range(0, len(Address)):
            Address[i].strip()
        yield {
                'Name': response.css('h1.biz-page-title::text').extract_first().strip(),
                'Category': response.css('div.price-category span.category-str-list a::text').extract(),
                'Rating': response.css('div.rating-info div.biz-rating div.i-stars::attr(title)').extract_first().split(' ')[0],
                'Address': Address,
                'Phone': response.css('span.biz-phone::text').extract_first().strip(),
                'PostalCode': PostalCode,
                'Country' : Country,
                'Location' : Location,
                'Website': website,
                'Review': Reviews,
                'Comment': Comment
            }
        