# -*- coding: utf-8 -*-
import json
import re
import time
import xml.etree.ElementTree as ET

import feedparser
import requests
from flask import Flask, Response
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)
data = {
    'channel': {
        'title': '网站名称',
        'description': '网站描述',
        'link': '网站链接',
        'image_url': '网站logo'
    },
    'items': [
        {
            'title': 'item_title',
            'link': 'https://example.com/12',
            'guid': 'https://example.com/12',
            'description': '',
            'pub_date': '2024-04-29 00:00:00'  # 日期字符串，需符合预期格式
        }
    ]
}
lis = [
    {
        "url": "https://www.douban.com/gallery/",
        "origin": "豆瓣-话题广场",
        "link": "https://www.douban.com/gallery/",
        "favicon": "https://www.douban.com/favicon.ico"
    }, {
        "url": "https://sspai.com/api/v1/article/tag/special/page/get?limit=10&offset=0&created_at={}&tag=%E6%95%88%E7%8E%87%E6%8A%80%E5%B7%A7&search_type=1",
        "origin": "少数派-效率技巧",
        "link": "https://sspai.com/",
        "favicon": "https://cdn-static.sspai.com/favicon/sspai.ico"
    }, {
        "url": "https://sspai.com/api/v1/article/tag/page/get?limit=10&offset=0&created_at={}&tag=%E7%94%9F%E6%B4%BB%E6%96%B9%E5%BC%8F&search_type=1",
        "origin": "少数派-生活方式",
        "link": "https://sspai.com/",
        "favicon": "https://cdn-static.sspai.com/favicon/sspai.ico"
    }, {
        "url": "https://weekly.tw93.fun/rss.xml",
        "origin": "潮流周刊",
        "link": "https://weekly.tw93.fun/",
        "favicon": "https://gw.alicdn.com/imgextra/i2/O1CN01m9YYjS1QBeW5DOm3I_!!6000000001938-2-tps-400-400.png"
    }
]


@app.route('/content/<route_name>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def content_route(route_name):
    try:
        if route_name == 'douBan':
            content = create_xml(douBan(lis[0]['url']), lis[0])
        elif route_name == 'shaoShuPai1':
            content = create_xml(shaoShuPai(lis[1]['url']), lis[1])
        elif route_name == 'shaoShuPai2':
            content = create_xml(shaoShuPai(lis[2]['url']), lis[2])
        elif route_name == 'fashionWeekly':
            content = create_xml(fashionWeekly(lis[3]['url']), lis[3])

        else:
            content = "<error>该 RSS 源不存在或出现故障，详情请联系管理员:nanged23</error>"
        return Response(content, content_type='application/xml; charset=utf-8')
    except Exception as e:
        return Response("接口出现如下错误：" + str(e) + "\n详情请联系管理员:nanged23",
                        content_type='text/plain; charset=utf-8')


def douBan(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    ans = []

    if response.status_code == 200:
        html_content = response.text
        pattern = r'<a\s*href="(.*?)"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        for match in matches[-18:-8]:
            href = match[0]
            text = match[1].strip()
            ans.append({
                "title": text,
                'url': href,
            })
        return ans
    else:
        print('获取豆瓣数据出现错误', response.text)
        return []


def fashionWeekly(url):
    response = requests.get(url, verify=False)
    # 确保请求成功
    if response.status_code == 200:
        # 使用feedparser解析RSS内容
        feed = feedparser.parse(response.text)

        # 获取其中的标题、摘要和链接
        ans = []
        for entry in feed.entries:
            # 使用正则表达式从描述中提取图片URL
            pattern = r'<img src="([^"]+)"'
            match = re.search(pattern, entry.description)
            if match:
                img_url = match.group(1)
                ans.append({
                    "title": entry.title,
                    'url': entry.link,
                    'img': img_url,
                })
        return ans
    else:
        print(f"从RSS源获取失败 {response.status_code}")
        return []


def shaoShuPai(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/123.0.0.0 Safari/537.36'
    }
    timestamp = time.time()
    url = url.format(timestamp)
    response = requests.get(url, headers=headers)
    text = response.text
    data = json.loads(text)
    url_prefix = "https://sspai.com/post/"
    ans = []
    img_prefix = "https://cdn.sspai.com/"
    for first_data in data['data']:
        title = first_data.get('title')
        img = img_prefix + first_data.get('banner')
        # 有些并不存在被推荐到首页的时间 只有发布时间和最后修改时间
        # pub_time = first_data.get('recommend_to_home_at')
        temp = (url_prefix + str(first_data.get('id')))
        # pub_time = datetime.fromtimestamp(float(pub_time), tz=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        # ans.append([temp, title, banner, pub_time])
        ans.append({
            "title": title,
            "url": temp,
            "img": img
        })
    return ans


def create_xml(data, website_info):
    # 创建根节点
    rss = ET.Element('rss', {'version': '2.0'})

    # 添加<script>节点（空节点）
    script = ET.SubElement(rss, 'script')

    # 添加<channel>节点及其子节点
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = website_info['origin']
    ET.SubElement(channel, 'description').text = website_info['origin']
    image = ET.SubElement(channel, 'image')
    ET.SubElement(channel, 'link').text = website_info['link']
    ET.SubElement(image, 'url').text = website_info['favicon']

    # 添加<item>节点及其子节点，假设有一个列表存储多个item
    for item_data in data:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = item_data['title']
        ET.SubElement(item, 'link').text = item_data['url']
        guid = ET.SubElement(item, 'guid', {'isPermaLink': 'true'})
        guid.text = item_data['url']
        if item_data.get('img') is not None:
            ET.SubElement(item, 'description').text = item_data['img']
        # pub_date = datetime.strptime(item_data['pub_date'], '%Y-%m-%d %H:%M:%S')  # 假设日期格式
        # pub_date_str = pub_date.strftime('%a, %d %b %Y %X GMT')  # 转换为所需格式
        # ET.SubElement(item, 'pubDate').text = pub_date_str

    # 生成最终的XML字符串
    return ET.tostring(rss, encoding='utf-8', method='xml').decode('utf-8')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=4010)
