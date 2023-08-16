import sys
import os

file = os.path.dirname(os.path.abspath(__file__))+'/'+sys.argv[1]
print(file)

languageTable = {'File Dir:': '星云VDB目录',
                 'Select Directory': '浏览目录',
                 'Nebula Name:': '星云文件名前缀',
                 'Index:': '浏览目录',
                 'Color Type:': '颜色类型',
                 'Resolution:': '分辨率',
                 'Nebula Shader:': '星云材质',
                 'Fog Shader:': '雾气材质',
                 'u"Create"': 'u"创建星云"',
                 'u"Get Parameter From Selected"': 'u"从选中星云获取参数"',
                 'u"Replace Selected"': 'u"替换选中星云"'}

def replace_text(file, languageTable):
    with open(file, 'r') as f:
        content = f.read()
    for key, value in languageTable.items():
        content = content.replace(key, value)
    new_file = file.split('.')[0] + '_cn.' + file.split('.')[1]
    with open(new_file, 'w') as f:
        f.write(content)

replace_text(file, languageTable)