# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from spider.items import SpiderItem


class CqjlpggzyzhjySpider(scrapy.Spider):
    name = 'cqjlpggzyzhjy'
    allowed_domains = ['cqjlpggzyzhjy.gov.cn']

    def start_requests(self):
        urls = [
            'http://www.cqjlpggzyzhjy.gov.cn/cqjl/jyxx/003001/003001001/003001001001/MoreInfo.aspx?CategoryNum=003001001001',
            'http://www.cqjlpggzyzhjy.gov.cn/cqjl/jyxx/003001/003001001/003001001002/MoreInfo.aspx?CategoryNum=003001001002',
            'http://www.cqjlpggzyzhjy.gov.cn/cqjl/ZtbWebDyProject/DaYi_List.aspx',
            'http://www.cqjlpggzyzhjy.gov.cn/cqjl/ZtbWebDyProject/BuYiAll_List.aspx'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_parameters)


    def parse_parameters(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        soupCtl = soup.find(id='ctl00') or soup.find(id='Form1')

        viewstate = soupCtl.find(id='__VIEWSTATE').attrs['value']
        viewstategenerator = soupCtl.find(id='__VIEWSTATEGENERATOR').attrs['value']

        soupPager1 = soup.find(id='MoreInfoList1_Pager')
        page1 = soupPager1 and soupPager1.find_all('b')[1].get_text()

        soupPager2 = soup.find(id='Pager')
        page2 = soupPager2 and soupPager2.find_all('b')[0].get_text()

        count_pages = int(page1 or page2)

        for page in range(0, count_pages):
            yield scrapy.FormRequest(url=response.url,
                        formdata={'__VIEWSTATE': viewstate, '__VIEWSTATEGENERATOR': viewstategenerator,
                            '__EVENTTARGET': 'MoreInfoList1$Pager', '__EVENTARGUMENT': str(page + 1)},
                        callback=self.parse_list)

    def parse_list(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        soup_list = soup.find(id='MoreInfoList1_tdcontent') or soup.find(id='DataGrid1')
        soup_list = soup_list.find_all('a')
        soup_type = soup.find(id='lastfont')

        for i in soup_list:
            if 'infodetail' in i.attrs['href'].lower():
                yield scrapy.Request(url=response.urljoin(i.attrs['href']), callback=self.parse_info)
            elif 'buyi_list' in i.attrs['href'].lower():
                yield scrapy.Request(url=response.urljoin(i.attrs['href']), callback=self.parse_parameters)
            else:
                item = SpiderItem()

                item['category'] = soup_type.string.strip()
                item['title'] = i.string.strip()
                item['date'] = i.parent.next_sibling.string.strip().replace('-', '/')
                item['content'] = ''

                item['file_urls'] = [response.urljoin(i.attrs['href'])]
                item['file_names'] = ['test.txt']

                item['url'] = response.urljoin(i.attrs['href'])

                yield item



    def parse_info(self, response):
        item = SpiderItem()

        soup = BeautifulSoup(response.body, 'html.parser')

        soup_type = soup.find(id='lastfont')
        item['category'] = soup_type.string.strip()

        soup_title = soup.find(id='tdTitle').div
        item['title'] = soup_title.font.b.string.strip()

        soup_title = soup_title.next_sibling.next_sibling
        item['date'] = soup_title.get_text().split('\r\n')[1].strip()

        soup_content = soup.find(id='TDContent')
        item['content'] = soup_content.get_text()

        item['file_urls'] = []
        item['file_names'] = []
        soup_files = soup.find(id='filedown').find_all('a')
        for soup_file in soup_files:
            item['file_urls'].append(response.urljoin(soup_file.attrs['href']))
            item['file_names'].append(soup_file.get_text().strip())
        
        item['url'] = response.url
        return item
