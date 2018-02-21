# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import hashlib
import os
import csv
import urllib

from spider import settings
from spider.items import SpiderItem

from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes


class SpiderPipeline(object):
    def __init__(self, *args, **kwargs):
        self.csv_file = open(settings.CSV_PATH, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csv_file, delimiter=';')
        self.writer.writerow(SpiderItem.fields.keys())


    def __del__(self, *args, **kwargs):
        self.csv_file.close()

    def process_item(self, item, spider):
        self.writer.writerow([item[key] for key in item.fields.keys()])

class MyFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_guid = media_guid[-8:]
        
        name = request.meta.get('file_name','test.txt')
        if response != None:
            name = os.path.basename(urllib.parse.unquote(response.url))

        media_name = os.path.splitext(name)[0]
        media_ext = os.path.splitext(name)[1]

        media_tag = request.meta.get('file_tag','test')
        media_title = request.meta.get('file_title','test')

        return '【%s】【%s】%s.%s%s' % (media_tag, media_title, media_name, media_guid, media_ext)


    def get_media_requests(self, item, info):
        for file_url, file_name in zip(item['file_urls'], item['file_names']):
            meta = {'file_name': file_name, 'file_tag': item['category'],
                'file_title': item['title']}
            yield Request(url=file_url, meta=meta)

