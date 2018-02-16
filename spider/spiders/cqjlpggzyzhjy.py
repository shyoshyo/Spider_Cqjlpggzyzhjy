# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from spider.items import SpiderItem


class CqjlpggzyzhjySpider(scrapy.Spider):
    name = 'cqjlpggzyzhjy'
    allowed_domains = ['cqjlpggzyzhjy.gov.cn']

    def start_requests(self):
        urls = [
            'http://www.cqjlpggzyzhjy.gov.cn/cqjl/jyxx/003001/003001001/003001001001/MoreInfo.aspx?CategoryNum=003001001001'
        ]
        #for url in urls:
        #    yield scrapy.Request(url=url, callback=self.parse_parameters)

        url = 'http://www.cqjlpggzyzhjy.gov.cn/cqjl/InfoDetail/Default.aspx?InfoID=0dd5c89b-e503-42d6-8137-cdbe7275c4e1&CategoryNum=003001001001'
        # url = 'http://www.cqjlpggzyzhjy.gov.cn/cqjl/infodetail/?infoid=847fdddf-3bd2-4532-92bc-ca0b11759379&categoryNum=003001001001'
        yield scrapy.Request(url=url, callback=self.parse)



    def parse_parameters(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        soup = soup.find(id='ctl00')

        viewstate = soup.find(id='__VIEWSTATE').attrs['value']
        viewstategenerator = soup.find(id='__VIEWSTATEGENERATOR').attrs['value']

        self.log(viewstate[0:10] + ' ' + viewstategenerator)
        self.log(response.url)

        for i in range(1, 2):
            yield scrapy.FormRequest(url=response.url,
                        formdata={'__VIEWSTATE': viewstate, '__VIEWSTATEGENERATOR': viewstategenerator,
                            '__EVENTTARGET': 'MoreInfoList1$Pager', '__EVENTARGUMENT': str(i)},
                        callback=self.parse_list)


        # page = response.url.split("/")[-2]
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % response.body)


    def parse_list(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        soup = soup.find(id='MoreInfoList1_tdcontent')
        soup = soup.find_all('a')

        for i in soup:
            self.log(str(response.urljoin(i.attrs['href'])))

            yield scrapy.Request(url=response.urljoin(i.attrs['href']), callback=self.parse)

    def parse(self, response):
        item = SpiderItem()

        soup = BeautifulSoup(response.body, 'html.parser')
        soup_title = soup.find(id='tdTitle').div

        item['title'] = soup_title.font.b.string.strip()
        # self.log('title %s' % (title))

        soup_title = soup_title.next_sibling.next_sibling
        item['date'] = soup_title.get_text().split('\r\n')[1].strip()
        # self.log('date %s' % (date))

        soup_content = soup.find(id='TDContent')
        item['content'] = soup_content.get_text()
        # self.log('content %s' % (content))

        item['file_urls'] = []
        item['file_names'] = []
        soup_files = soup.find(id='filedown').find_all('a')
        for soup_file in soup_files:
            item['file_urls'].append(response.urljoin(soup_file.attrs['href']))
            item['file_names'].append(soup_file.get_text().strip())

            # self.log('url %s' % (url))
            # self.log('url %s' % (file_name))
        return item
