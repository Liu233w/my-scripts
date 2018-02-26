# -*- coding: utf-8 -*-
"""
用于合并 json 文件
"""

a_file = r"d:\Software\ZeroNet-win-dist\data\sites.json"
b_file = r"g:\Software\ZeroNet-win-dist\data\sites.json"

dist_file = r"d:\temp\out.json"

import json

def read_json_from_file(file_path):
    with open(file_path, encoding='utf-8') as fr:
        return(json.load(fr))

aj = read_json_from_file(a_file)
bj = read_json_from_file(b_file)

bj.update(aj)

with open(dist_file, 'w', encoding='utf-8') as fr:
    json.dump(bj, fr, indent=2, separators=[', ', ': '])
