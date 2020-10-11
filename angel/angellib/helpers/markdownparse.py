#!/usr/bin/env python3

import mistune
import re
import os

class MarkdownText:
    def __init__(self, text):
        self.text = text
        if os.environ.get("DEBUG", "") == 'true':
            print(text)

    def parse(self):
        htmltext = mistune.html(self.text)
        if os.environ.get("DEBUG", "") == 'true':
            print(htmltext)
        return htmltext

    def toRawText(self):
        step1 = re.sub(r'\<[^>]*>', r' ', self.text)
        step2 = re.sub(r'\s{2,}', r' ', step1)
        return step2.strip()
