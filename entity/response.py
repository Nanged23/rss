# -*- coding: utf-8 -*-
class Response:
    code = ''
    data = []

    def __init__(self, code, data):
        self.code = code
        self.data = data
