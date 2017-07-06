import scrapy
import json

import csv
import re

class YelpSpider(scrapy.Spider):
    name = "yelp"
    allowed_domains = ["yelp.com"]
    start_urls = [
        'https://www.yelp.com/search?cflt=restaurants&find_loc=501'
    ]

    def parse(self, response):
        cr = csv.reader(open(r"D:\tutorial_Tu_Update1\tutorial_Tu\tutorial\spiders\zipcodetest.csv","r"))
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
        for href in page_links:
            yield response.follow(href, self.parseDetailPage)
        next_page = response.css('a.next::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parseSearchPage)
        
    def parseDetailPage(self, response):

        script = response.css('script[type="application/ld+json"]::text').extract_first()
        script_parse = json.loads(str(script))
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
        # for i in range(0, len(Reviews)):
        #     Reviews[i] = (Reviews[i].strip())[+1:-1]
        Comments = response.css('div.review-content p::text').extract()
        for i in range(0, len(Comments)):
            if(i < len(Comments) - 1):
                Comments[i] = Comments[i].strip() 

        Address = response.css('div.map-box-address strong.street-address address::text').extract()
        for i in range(0, len(Address)):
            Address[i] = Address[i].strip()

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
                        Schedule.append(BizDate[i - 1] + ' : ' + str(td[0]).strip() + ' - ' + str(td2[0]).strip() + '(Normally:' + hour + ')')
                        delta = delta + 1
                    else:
                        Schedule.append(BizDate[i - 1] + ' : ' + str(td[0]).strip())
            else:
                hour = ''
                for biz in BizHour:
                    hour += biz + ','
                hour = hour[:-1]
                Schedule.append(BizDate[i - 1] + ' : ' + hour)

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
        category = response.css('div.price-category span.category-str-list a::text').extract()
        yield {
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
                'Comment': Comments,
                'PriceRange': str(PriceRange).strip(),
                'Hour': Schedule,
                'MoreInfo': Info
            }
        