import scrapy
import json
from msvcrt import getch
import csv
import re

NATION = ['JP']

class YelpSpider(scrapy.Spider):
    name = "yelp"
    allowed_domains = ["yelp.com"]
    start_urls = [
        'https://www.yelp.com/search?cflt=restaurants&find_loc=501',
    ]
    handle_httpstatus_list = [503]

    def __init__(self):
        self.ids_seen = set()
        self.ids_rev = set()

    def parse(self, response):
        cr = csv.reader(open(r"tutorial\spiders\postalcode\test.csv","r"))
        for row in cr:
            while (row[0][0] == '0'):
                row[0] = row[0][+1:]
            print('$$$$$$$$$$$$$$$$$$$$$$$$$ search: %s $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$' %row[0])
            yelp_url  = "https://www.yelp.com/search?cflt=restaurants&find_loc=%s" % row[0].strip()
            print(yelp_url)
            yield response.follow(yelp_url, self.parseSearchPage)

    def parseSearchPage(self, response):
        if response.status == 503:
            print('ERROR ON GETTING DATA !!!!!!!!!!!!!!!!!!!!!!!!!!!')
            getch()
        restaurants = response.css('div.search-result')
        for restaurant in restaurants:
            id = restaurant.css('::attr(data-biz-id)').extract()
            id = id[0].strip() if len(id) else ''
            if id != '' and id not in self.ids_seen:
                self.ids_seen.add(id)
                page_link = restaurant.css('a.biz-name::attr(href)').extract()
                page_link = page_link[0].strip() if len(page_link) else ''
                if page_link != '':
                    yield response.follow(page_link, self.parseDetailPage, meta={'id':id})
            else:
                print('Ignoring duplicate restaurant...')
        next_page = response.css('a.next::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parseSearchPage)
        
    def parseDetailPage(self, response):
        if response.status == 503:
            print('ERROR ON GETTING DATA !!!!!!!!!!!!!!!!!!!!!!!!!!!')
            getch()
        id = response.meta['id']
        script = response.css('script[type="application/ld+json"]::text').extract_first()
        script_parse = ''
        try:
            script_parse = json.loads(str(script))
            pass
        except Exception as e:
            return
            raise
        print('#################### PostalCode: %s' % script_parse['address']['postalCode'])
        PostalCode = script_parse['address']['postalCode']

        print('#################### Address Country: %s' % script_parse['address']['addressCountry'])
        Country = script_parse['address']['addressCountry']
        if Country not in NATION:
            print('Skipping not JP restaurant...')
            return
        mapstate = response.css('div.lightbox-map::attr(data-map-state)').extract_first()
        mapstate_parse = json.loads(mapstate)
        Latitude = mapstate_parse['center']['latitude']
        Longitude = mapstate_parse['center']['longitude']
        Location = str(Latitude) + ',' + str(Longitude)
        
        website = response.css('span.biz-website a::text').extract_first()

        quotes  = response.css('p.quote')
        Reviews =[]
        for quote in quotes:
            name = quote.css('a::text').extract_first()
            quote = quote.css('p.quote').extract_first()
            beginIndex = quote.find("<a")
            endIndex = quote.find("</a>")
            endIndex +=4
            quote = quote[:beginIndex]+name+quote[endIndex:]
            beginIndex = quote.find("\n")
            endIndex = quote.find("<a")
            beginIndex +=2
            endIndex -=1
            quote = quote[beginIndex:endIndex]
            quote = quote.strip()[+1:-1]
            Reviews.append(quote)

        Comments = response.css('div.review')
        Comments = Comments[1:]
        listComments =''
        for comment in Comments:
            name = comment.css('a.user-display-name::text').extract()[0].replace('.','')
            words = comment.css('div.review-content p::text').extract()
            listWords =''
            for word in words:
                listWords +=word.strip()+" "
            listComments +=name+": "+listWords+'\n'

        Address = ''
        Address0 = response.css('div.map-box-address strong.street-address address::text').extract()
        Address1 = []
        Address2 = []
        if len(Address0) <= 0:
            Address1 = response.css('div.map-box-address strong.street-address a::text').extract()
            if len(Address1) <= 0:
                Address1 = response.css('div.map-box-address strong.street-address::text').extract()
            Address2 = response.css('div.map-box-address address::text').extract()
        for i in range(0, len(Address0)):
            Address += Address0[i].strip() + ', '
        for i in range(0, len(Address1)):
            Address += Address1[i].strip() + ', '
        for i in range(0, len(Address2)):
            Address += Address2[i].strip() + ', '
        Address = Address[1:]

        Sidebar = response.css('div.sidebar')
        Openrail = Sidebar.css('div.open-rail')
        PriceRange = Openrail.css('dd.price-description::text').extract_first()

        Hour = Sidebar.css('div.biz-hours')
        BizDate = Hour.css('table.hours-table th::text').extract()
        Schedule = []
        delta = 0
        for i in range(1, len(BizDate) + 1):
            BizHour = Hour[0].xpath('//table/tbody/tr[%s]/td[1]/span/text()' %(i + delta)).extract()
            if (len(BizHour) <= 0):
                td = Hour[0].xpath('//table/tbody/tr[%s]/td[1]/strong/text()' %(i + delta)).extract()
                if(len(td) <= 0):
                    td = Hour[0].xpath('//table/tbody/tr[%s]/td[1]/text()' %(i + delta)).extract()
                if(len(td) > 0):
                    td2 = Hour[0].xpath('//table/tbody/tr[%s]/td[2]/span/text()' %(i + delta)).extract()
                    if(len(td2) > 0):
                        BizHour = Hour[0].xpath('//table/tbody/tr[%s]/td[1]/small/span/text()' %(i+1+delta)).extract()
                        hour = ''
                        for biz in BizHour:
                            hour += biz + ','
                        hour = hour[:-1]
                        Schedule.append(BizDate[i - 1] + ' : ' + hour)
                        delta = delta + 1
                    else:
                        Schedule.append(BizDate[i - 1] + ' : ' + str(td[0]).strip())
            else:
                hour = ''
                for biz in BizHour:
                    hour += biz + ','
                hour = hour[:-1]
                Schedule.append(BizDate[i - 1] + ' : ' + hour)
        Schedules = ''
        for hour in Schedule:
            Schedules += hour + '; '
        Info1 = Sidebar.css('div.ywidget ul.ylist dl dt::text').extract()
        Info2 = Sidebar.css('div.ywidget ul.ylist dl dd::text').extract()
        Info = []
        for i in range(0, len(Info1)):
            Info.append(Info1[i].strip() + ' : ' + Info2[i].strip())
        phone =response.css('span.biz-phone::text').extract()
        if len(phone)>0:
            phone=phone[0].strip()
        else:
            phone=''
        rating=response.css('div.rating-info div.biz-rating div.i-stars::attr(title)').extract()
        if len(rating)>0:
            rating=rating[0].split(' ')[0]
        else:
            rating=''
        cates = response.css('div.price-category')
        category = cates[0].css('span.category-str-list a::text').extract()
        yield {
                'id' : id,
                'Name': response.css('h1.biz-page-title::text').extract_first().strip(),
                'Category': category,
                'Rating': rating,
                'Address': Address,
                'Phone': phone,
                'PostalCode': PostalCode,
                'Country' : Country,
                'Location' : Location,
                'Website': website,
                'Review': Reviews,
                'Comment': listComments,
                'PriceRange': str(PriceRange).strip(),
                'Hour': Schedules,
                'MoreInfo': Info,
                'Link': response.request.url
            }
        