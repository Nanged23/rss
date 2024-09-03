# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET


def create_xml(data, website_info):
    """
    :param data: rss 内容，期望的格式如下：
    [ {"title": "本期内容的标题","url": "本期内容的 URL","description": "本期内容的描述文本"} ]
    :param website_info:rss 网站的基本信息，在 websites.json 中配置
    :return:一段可直接渲染展示的 xml 文本
    """
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = website_info['title']
    ET.SubElement(channel, 'description').text = website_info['description']
    ET.SubElement(channel, 'link').text = website_info['link']
    image = ET.SubElement(channel, 'image')
    ET.SubElement(image, 'url').text = website_info['favicon']
    for item_data in data:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = item_data['title']
        ET.SubElement(item, 'link').text = item_data['url']
        guid = ET.SubElement(item, 'guid', {'isPermaLink': 'true'})
        guid.text = item_data['url']
        if item_data.get('description') is not None:
            ET.SubElement(item, 'description').text = item_data['description']
    return ET.tostring(rss, encoding='utf-8', method='xml').decode('utf-8')
