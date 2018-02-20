# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import hashlib
import os
import csv

from spider import settings
from spider.items import SpiderItem

from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes


class SpiderPipeline(object):
    def process_item(self, item, spider):
        return None

class MyFilesPipeline(FilesPipeline):
    def __init__(self, *args, **kwargs):
        super(MyFilesPipeline, self).__init__(*args, **kwargs)
        self.csv_file = open(settings.CSV_PATH, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csv_file, delimiter=';')
        self.writer.writerow(SpiderItem.fields.keys())
        
    def __del__(self, *args, **kwargs):
        self.csv_file.close()

    def file_path(self, request, response=None, info=None):
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_guid = media_guid[-8:]
        
        name = request.meta.get('file_name','test.txt')

        media_name = os.path.splitext(name)[0]
        media_ext = os.path.splitext(name)[1]

        media_tag = request.meta.get('file_tag','test')

        return '[%s]%s.%s%s' % (media_tag, media_name, media_guid, media_ext)


    def get_media_requests(self, item, info):
        for file_url, file_name in zip(item['file_urls'], item['file_names']):
            meta = {'file_name': file_name, 'file_tag': item['category']}
            yield Request(url=file_url, meta=meta)

    def process_item(self, item, spider):
        FilesPipeline.process_item(self, item, spider)

        print(item)
        self.writer.writerow([item[key] for key in item.fields.keys()])

