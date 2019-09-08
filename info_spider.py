import requests
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame
import re
import time

provinceNmaeDict = {
    '11': '北京市',
    '37': '山东省',
    '22': '吉林省',
    '12': '天津市',
    '13': '河北省',
    '14': '山西省',
    '15': '内蒙古自治区',
    '21': '辽宁省',
    '23': '黑龙江省',
    '31': '上海市',
    '32': '江苏省',
    '33': '浙江省',
    '34': '安徽省',
    '35': '福建省',
    '36': '江西省',
    '41': '河南省',
    '42': '湖北省',
    '43': '湖南省',
    '44': '广东省',
    '45': '广西壮族自治区',
    '46': '海南省',
    '50': '重庆市',
    '51': '四川省',
    '52': '贵州省',
    '53': '云南省',
    '54': '西藏自治区',
    '61': '陕西省',
    '62': '甘肃省',
    '63': '青海省',
    '64': '宁夏回族自治区',
    '65': '新疆维吾尔自治区',
    '71': '台湾省',
    '81': '香港特别行政区',
    '82': '澳门特别行政区'
}

class Graduate:
    def __init__(self, province, category, provinceName):
        self.head = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKi"
            "t/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
        }
        self.data = []
        self.province = province
        self.category = category
        self.provinceName = provinceName

    def get_list_fun(self, url, name):
        response = requests.get(url, headers=self.head)
        resprovince = response.json()
        with open(name + ".txt", "w") as f:
            for x in resprovince:
                f.write(str(x))
                f.write("\n")

    def get_list(self):
        self.get_list_fun("http://yz.chsi.com.cn/zsml/pages/getSs.jsp",
                          "province")
        self.get_list_fun('http://yz.chsi.com.cn/zsml/pages/getMl.jsp',
                          "category")
        self.get_list_fun('http://yz.chsi.com.cn/zsml/pages/getZy.jsp',
                          'major')

    def get_school_url(self):
        url = "https://yz.chsi.com.cn/zsml/queryAction.do"
        data = {
            "ssdm": self.province,
            "yjxkdm": self.category,
        }
        response = requests.post(url, data=data, headers=self.head)
        html = response.text
        reg = re.compile(r'(<tr>.*? </tr>)', re.S)
        content = re.findall(reg, html)
        schools_url = re.findall('<a href="(.*?)" target="_blank">.*?</a>',
                                 str(content))
        return schools_url

    def get_college_data(self, url):
        response = requests.get(url, headers=self.head)
        html = response.text
        colleges_url = re.findall(
            '<td class="ch-table-center"><a href="(.*?)" target="_blank">查看</a>',
            html)
        return colleges_url

    def get_final_data(self, url):
        temp = []
        response = requests.get(url, headers=self.head)
        html = response.text
        soup = BeautifulSoup(html, features='lxml')
        summary = soup.find_all('td', {"class": "zsml-summary"})
        for x in summary:
            temp.append(x.get_text())
        summary = soup.find_all('span', {"class": "zsml-bz"})
        temp.append(summary[1].get_text())
        self.data.append(temp)

    def get_schools_data(self):
        url = "http://yz.chsi.com.cn"
        schools_url = self.get_school_url()
        amount = len(schools_url)
        i = 0
        for school_url in schools_url:
            i += 1
            page = 1
            temp = []
            while True:
                url_ = url + school_url + '&pageno={}'.format(page)
                colleges_url = self.get_college_data(url_)
                if colleges_url not in temp:
                    print('收集第{}页信息'.format(page))
                    temp.append(colleges_url)
                    page += 1
                    for college_url in colleges_url:
                        _url = url + college_url
                        self.get_final_data(_url)
                else:
                    break
            print("已完成" + self.provinceName + "第" + str(i) + "/" +
                  str(amount) + "个高校爬取")
            #time.sleep(30)

    def get_data_frame(self):
        data = DataFrame(self.data)
        data.columns = ['学校', '考试方式', '院系所', '', '专业',
                        '学习方式', '研究方向', '指导教师', '拟招生人数', '备注']
        data.drop(labels='', axis=1, inplace=True)
        data.to_csv(self.provinceName + "研究生招生信息.csv",
                    encoding="utf_8_sig", index=False)


if __name__ == '__main__':
    category = "####" # 专业代码
    for i in list(provinceNmaeDict.keys()):
        province = i
        if province in provinceNmaeDict.keys():
            spyder = Graduate(province, category, provinceNmaeDict[province])
            spyder.get_schools_data()
            spyder.get_data_frame()
            time.sleep(30) # 延迟时间30s
