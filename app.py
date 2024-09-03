# -*- coding: utf-8 -*-
import json
from flask import Flask, Response
from flask_cors import CORS

from resources.douban_club import douban_club
from resources.create_xml import create_xml

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return "<h1 align='center'>欢迎来到主界面 🪿</h1><hr>本网站内容主要有:<br>1. 通过<code>/rss/xxx</code>路径访问 RSS 源"


# 自定义404错误处理函数
@app.errorhandler(404)
def page_not_found(err):
    return "<h1>404 - 页面未找到</h1><p>抱歉，您访问的页面不存在。😥</p>", 404


@app.route('/rss/<path:route_name>', methods=['GET'])
def get_rss_content(route_name):
    route_name = str(route_name)
    ans = route_name.rsplit("/", 1)
    if ans[0] == "douban-club":
        club_id = ans[1]
        content = douban_club(club_id)
        if content.code != 200:
            return Response(content.data, content_type='text/plain; charset=utf-8')
        else:
            with open('websites.json', 'r', encoding='utf-8') as f:
                websites = json.load(f)
            for item in websites:
                if item["origin"] == ans[0]:
                    return Response(create_xml(content.data, item), content_type='application/xml; charset=utf-8')
    else:
        return Response("暂且开发该 rss 接口，可催更作者～", content_type='text/plain; charset=utf-8')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=True)
