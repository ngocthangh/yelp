import scrapy

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
        cr = csv.reader(open(r"D:\Yelp\Projects\tutorial\tutorial\spiders\us_postal_codes.csv","rb"))
        for row in cr:
            while (row[0][0] == '0'):
                row[0] = row[0][+1:]
            print('$$$$$$$$$$$$$$$$$$$$$$$$$ search: %s $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$' %row[0])
            yelp_url  = "https://www.yelp.com/search?cflt=restaurants&find_loc=%s" % row[0].strip()
            print(yelp_url)
            yield response.follow(yelp_url, self.parse_page)
            for a in response.css('a.next'):
                yield response.follow(a, callback=self.parse_page)

    def parse_page(self, response):
        sites = response.xpath('//*[@id="super-container"]/div/div[2]/div[1]/div/div[4]/ul[2]/li')
        lists = response.xpath('//script/text()').extract()
        index=0
        for list in lists:
            if list.find("yelp.www.init.search.Controller") !=-1:
                break
            index +=1
        list = lists[index]
        words = list.replace(' ','').replace('"','').replace('{','').replace('}','').replace(',longitude',':longitude').split(',')
        coodinate =[]
        for word in words:
            if word.find("location:latitude") !=-1:
                word = word.replace('location:','').replace('latitude:','').replace(':longitude:',',')
                coodinate.append(word)
        count =0
        for site in sites:
            address1 = site.xpath('div/div[1]/div[2]/div/text()').extract()
            if len(address1) > 0:
                address1=address1[0].replace('\n','').strip()
            else:
                address1=''
            tmp_Address1 =site.xpath('div/div[1]/div[2]/address/text()[1]').extract()
            if len(tmp_Address1):
                tmp_Address1 = tmp_Address1[0].replace('\n','').strip()
            else:
                tmp_Address1=''
            tmp_Address2 =site.xpath('div/div[1]/div[2]/address/text()[2]').extract()
            if len(tmp_Address2):
                tmp_Address2 = tmp_Address2[0].replace('\n','').strip()
            else:
                tmp_Address2=''
            address2 = str(tmp_Address1)+" "+str(tmp_Address2)
            if len(address2) ==1:
                address2=address1
            phone1 = site.xpath('div/div[1]/div[2]/span[3]/text()').extract()
            if len(phone1) > 0:
                phone1 = phone1[0].replace('\n','').strip()
            else:
                phone1=''
            phone2 = site.xpath('div/div[1]/div[2]/span[2]/text()').extract()
            if len(phone2) > 0:
                phone2 = phone2[0].replace('\n','').strip()
            else:
                phone2=''
            if len(phone1) == 0:
                phone1= phone2
            category = site.xpath('div/div[1]/div[1]/div/div[2]/div[2]/span[2]/a/text()').extract()

            if len(coodinate[count]) >0:
                location = coodinate[count]
            else:
                location =''
            yield{
                'name':site.xpath('div/div[1]/div[1]/div/div[2]/h3/span/a/span/text()').extract(),
                'category':category,
                'rating':site.xpath('div/div[1]/div[1]/div/div[2]/div[1]/div/@title').extract()[0].split(' ')[0],
                'address':address2,
                'location':location,
                'phone': phone1,
            }
            count +=1
        

        