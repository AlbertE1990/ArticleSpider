import requests
from bs4 import BeautifulSoup
import time
from utils.common import get_nums
import MySQLdb
from settings import USER_AGENT,MYSQL_DBNAME,MYSQL_HOST,MYSQL_PASSWORD,MYSQL_USER
headers = {'User-Agent':USER_AGENT}
url = 'http://www.xicidaili.com/nn/'

conn = MySQLdb.connect(host=MYSQL_HOST,user=MYSQL_USER,password=MYSQL_PASSWORD,database=MYSQL_DBNAME,charset='utf8')
cursor = conn.cursor()


def get_page(page_url):
    r = requests.get(page_url, headers=headers, timeout=6)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    ip_tr_list = soup.select('#ip_list tr')
    for ip_tr in ip_tr_list:
        try:
            ip_td_list = ip_tr.find_all('td')
            ip = ip_td_list[1].text
            port = ip_td_list[2].text
            addr = ip_td_list[3].a.text
            ip_type = ip_td_list[5].text
            speed = ip_td_list[6].div['title']
            priority = get_nums(ip_td_list[6].div.div['style'])
            conn_time = ip_td_list[7].div['title']
            alive_time = ip_td_list[8].text
            validate_time = ip_td_list[9].text
            sql = '''
            INSERT INTO xici_ip (ip,port,addr,ip_type,speed,priority,conn_time,validate_time)
            VALUES ('{0}','{1}','{2}','{3}','{4}',{5},'{6}','{7}')
            '''.format(ip,port,addr,ip_type,speed,priority,conn_time,validate_time)
            cursor.execute(sql)
            conn.commit()

        except Exception as e:
            print(e)


def get_pages(home_url,s_page=1,e_page=4000):
    if s_page > e_page:
        raise Exception('start page > end page!!')
    p = s_page
    while 1:
        page_url = home_url+str(p)
        get_page(page_url)
        if  p < e_page:
            p+=1
        else:
            return


class XiciIP(object):
    def get_random_ip(self):
        sql = '''
        SELECT ip,port,ip_type FROM xici_ip
        ORDER BY RAND()
        LIMIT 1
        '''
        cursor.execute(sql)
        conn.commit()
        ip,port,ip_type = cursor.fetchone()

        if self.judge_ip(ip,port,ip_type):
            print('成功获取可用IP：')
            print("{0}://{1}:{2}".format(ip_type, ip, port))
            return  "{0}://{1}:{2}".format(ip_type,ip, port)
        else:
            return self.get_random_ip()

    def judge_ip(self,ip,port,ip_type):
        http_url = "http://www.baidu.com"
        proxy_url = "{0}://{1}:{2}".format(ip_type, ip, port)
        proxy_dict = {ip_type:proxy_url}
        try:
            response = requests.get(http_url,proxies=proxy_dict)
        except Exception as e:
            print("invalid ip")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >=200 and code < 300:
                return True
            else:
                print("invalid ip")
                self.delete_ip(ip)
                return False

    def delete_ip(self,ip):
        sql = '''
        DELETE FROM xici_ip WHERE ip='{}'
        '''.format(ip)
        cursor.execute(sql)
        print('ip:%s 删除成功！'%ip)


if __name__ == '__main__':
    # get_pages(home_url=url,e_page=30)
    xi = XiciIP()
    ip = xi.get_random_ip()
