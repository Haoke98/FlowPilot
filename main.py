# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/4/22
@Software: PyCharm
@disc:
======================================="""
import json
import os

if __name__ == '__main__':
    ignores_list = []
    ignores_fps = os.listdir('ignores')
    for fn in ignores_fps:
        fp = os.path.join('ignores', fn)
        with open(fp, 'r') as f:
            _list = json.load(f)
            print(fp, _list)
            ignores_list.extend(_list)
    final = list(set(ignores_list))
    print("final:", final)
    final_str = ",".join(final)
    print("final_str:", final_str)
    # 控制台不支持范型和通配符, 必须是确切的域名
    print(f'export no_proxy="{final_str}"')
