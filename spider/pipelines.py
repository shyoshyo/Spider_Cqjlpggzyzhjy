# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import hashlib
import os

from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes


class SpiderPipeline(object):
    def process_item(self, item, spider):
        print('!!!!!!!! SpiderPipeline')
        spider.log(item)
        return None
        return item

class MyFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation
        
        name = request.meta.get('file_name','test.txt')

        media_name = os.path.splitext(name)[0]
        media_ext = os.path.splitext(name)[1]        

        return '%s%s%s' % (media_name, media_guid, media_ext)


    def get_media_requests(self, item, info):
        print('!!!!!!!! MyFilesPipeline')
        for file_url, file_name in zip(item['file_urls'], item['file_names']):
            meta = {'file_name': file_name}
            yield Request(url=file_url, meta=meta)


