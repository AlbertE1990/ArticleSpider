import  re
from datetime import datetime

def get_nums(value):
    # num = re.findall("\d+", value)
    # num = re.search("\D*(\d+)\D*", value)
    # num = re.match("\D*(\d+)\D*", value)
    num = re.fullmatch('.*(\d+).*',value)
    if num:
        num = num.group(1)
    else:
        num = 0
    print(num)
    return num

get_nums(" .89 评论 点赞")

print(datetime(1970,1,1))