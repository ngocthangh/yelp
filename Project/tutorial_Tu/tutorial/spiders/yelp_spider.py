import scrapy

from scrapy.selector import Selector
from tutorial.items import YelpItem
class YelpSpider(scrapy.Spider):
    name = "yelp"
    allowed_domains = ["yelp.com"]
    start_urls = [
        'https://www.yelp.com/search?find_loc=San+Francisco,+CA,+US&start=10'
    ]

    for i in range(2,100):
       	start_urls.append("https://www.yelp.com/search?find_loc=San+Francisco,+CA,+US&start="+str(i*10))

    def parse(self, response):
        sites = response.xpath('//*[@id="super-container"]/div/div[2]/div[1]/div/div[4]/ul[2]/li')
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

            yield{
                'name':site.xpath('div/div[1]/div[1]/div/div[2]/h3/span/a/span/text()').extract(),
                'category':category,
                'rating':site.xpath('div/div[1]/div[1]/div/div[2]/div[1]/div/@title').extract()[0].split(' ')[0],
                'address':address2,
                'phone': phone1,
            }

        #     item = YelpItem()
        #     name = site.xpath('div/div[1]/div[2]/h3/span/a/text()').extract()
        #     if len(name) > 0:
        #         item['name'] = name[0]
        #     else:
        #         item['name'] = ''
        #
        #     url = site.xpath('div/div[1]/div[2]/h3/span/a/@href').extract()
        #     if len(url) > 0:
        #         item['url'] = u'http://www.yelp.com' + url[0]
        #     else:
        #         item['url'] = ''
        #
        #     address_l1 = site.xpath('div/div[2]/address/text()[1]').extract()
        #     if len(address_l1) > 0:
        #         item['address_l1'] = address_l1[0].replace('\n', '').strip()
        #     else:
        #         item['address_l1'] = ''
        #
        #     address_l2 = site.xpath('div/div[2]/address/text()[2]').extract()
        #     if len(address_l2) > 0:
        #         item['address_l2'] = address_l2[0].replace('\n', '').strip()
        #     else:
        #         item['address_l2'] = ''
        #
        #     phone = site.xpath('div/div[2]/span[2]/text()').extract()
        #     if len(phone) > 0:
        #         item['phone'] = phone[0].replace('\n', '').strip()
        #     else:
        #         item['phone'] = ''
        #
        #     item['category'] = site.xpath('div/div[1]/div[2]/div[2]/span[2]/a/text()').extract()
        #
        #     rating = site.xpath('div/div[1]/div[2]/div[1]/div/i/@title').extract()
        #     if len(rating) > 0:
        #         item['rating'] = rating[0].split(' ')[0]
        #     else:
        #         item['rating'] = ''
        #
        #     thumbUrl = site.xpath('div/div[1]/div[1]/div/a/img/@src').extract()
        #     if len(thumbUrl) > 0:
        #         item['thumbUrl'] = u'http:' + thumbUrl[0]
        #     else:
        #         item['thumbUrl'] = ''
        #
        #     fav_comment_user = site.xpath('div/div[3]/div[1]/div/a/img/@alt').extract()
        #     if len(fav_comment_user) > 0:
        #         item['fav_comment_user'] = fav_comment_user[0]
        #     else:
        #         item['fav_comment_user'] = ''
        #
        #     fav_comment_content = site.xpath('div/div[3]/div[2]/p/text()').extract()
        #     if len(fav_comment_content) > 0:
        #         item['fav_comment_content'] = fav_comment_content[0]
        #     else:
        #         item['fav_comment_content'] = ''
        #
        #     fav_comment_user_face = site.xpath('div/div[3]/div[1]/div/a/img/@src').extract()
        #     if len(fav_comment_user_face) > 0:
        #         item['fav_comment_user_face'] = u'http:' + fav_comment_user_face[0]
        #     else:
        #         item['fav_comment_user_face'] = ''
        #
        #     items.append(item)
        # return items
