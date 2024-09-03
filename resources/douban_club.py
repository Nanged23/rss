# -*- coding: utf-8 -*-
import requests
from lxml import etree
from entity.response import Response
import re


def douban_club(club_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/123.0.0.0 Safari/537.36'
    }
    url = "https://www.douban.com/club/" + club_id + "/timeline"
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    tree = etree.HTML(response.text)
    divs = tree.xpath('//div[@class="status-saying"]')
    try:
        if divs:
            result_list = []
            for div in divs:
                text_content = div.xpath('.//blockquote/p//text()')
                text_content = ''.join(text_content).replace('  ', '')
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                url = div.xpath('.//blockquote//a[@title]/@href')
                url = url[0] if url else None
                img_srcs = div.xpath('.//img/@src')
                description = f"{' '.join(img_srcs)} {text_content}"
                item = {
                    "title": text_content,
                    "url": url,
                    "description": description
                }
                result_list.append(item)
            return Response(200, result_list)
        else:
            return Response(404, ['没有发现小组内容，请确保 club_id 正确！'])
    except Exception as e:
        return Response(404, [e])


douban_club("23225541")
