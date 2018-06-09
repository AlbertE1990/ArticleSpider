import hashlib
import re

def get_md5(url):
    #py3中没有unicode类型，str默认就是Unicode
    if isinstance(url,str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

#从字符串中提取数字
def get_nums(value):
    num = re.match("\D*([\d|,]+)\D*", value)
    if num:
        num = int(num.group(1).replace(',',''))
    else:
        num = 0
    return num

if __name__ == "__main__":

    pass