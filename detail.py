import time
import datetime
import re
from boss_monogo import BossMongo
from base import Base


class Detail(Base):
    def __init__(self, browser, checkInfo=True):
        self.mongo = BossMongo()
        self.browser = browser
        self.container = browser(resourceId="com.hpbr.bosszhipin:id/lv_chat")
        self.container.scroll.vert.toEnd()
        self.infos = {}
        self.checkInfo = checkInfo
        self.start()

    def getItem(self):
        return self.container.child(className='android.widget.LinearLayout')

    def sex(self):
        info = self.browser.screenshot().crop((101, 380, 102, 381))
        blue = info.getcolors(1)[0][1][2]
        return '男' if blue == 255 else '女'

    def saveInfo(self, key, fn, *args, **kwargs):
        cache = self.infos
        if key not in cache.keys():
            info = fn(*args, **kwargs)
            if info is not None:
                cache[key] = info

    def getWeixin(self, item):
        text = self.getText(item.child(resourceId='com.hpbr.bosszhipin:id/tv_text'))
        if text is not None and '微信号' in text:
            sg = re.search(r'\：(.+)', text)
            if sg is not None:
                return sg[1]

    def getPhone(self, item):
        text = self.getText(item.child(resourceId='com.hpbr.bosszhipin:id/tv_text'))
        if text is not None and '手机号' in text:
            sg = re.search(r'\：(\d+)', text)
            if sg is not None:
                return sg[1]

    def tagAsked(self, item):
        asked = item.child(text='方便发一份你的简历过来么？').exists or item.child(text='请问在考虑新的工作机会吗？').exists
        return True if asked else None

    def needCollect(self):
        caches = self.infos
        keys = caches.keys()
        return 'wx' not in keys or 'phone' not in keys or 'asked' not in keys

    def getDetail(self):
        items = self.getItem()
        if self.needCollect():
            for item in items:
                self.saveInfo('wx', self.getWeixin, item)
                self.saveInfo('phone', self.getPhone, item)
                self.saveInfo('asked', self.tagAsked, item)

    def getCompanies(self, co_item):
        experience_co = self.getText(co_item.child(resourceId="com.hpbr.bosszhipin:id/tv_company_name"))
        experience_period = self.getText(co_item.child(resourceId='com.hpbr.bosszhipin:id/tv_year'))
        experience_major = self.getText(co_item.child(resourceId='com.hpbr.bosszhipin:id/tv_position'))
        return {
          "experience_co": experience_co,
          "experience_period": experience_period,
          "experience_major": experience_major
        }

    def findJobId(self):
        d = self.browser
        title = d(resourceId='com.hpbr.bosszhipin:id/tv_expect_position').get_text()
        salaries = d(resourceId='com.hpbr.bosszhipin:id/tv_expect_salary').get_text()
        return self.mongo.find_job_id(title, salaries)

    def getBaseInfo(self, items):
        item = items.child(resourceId='com.hpbr.bosszhipin:id/ll_head')
        if item.exists:
            name = self.getText(item.child(resourceId='com.hpbr.bosszhipin:id/tv_name'))
            age = self.getText(item.child(resourceId='com.hpbr.bosszhipin:id/tv_age'))
            desc = self.getText(item.child(resourceId='com.hpbr.bosszhipin:id/tv_advantage'))
            level = self.getText(item.child(resourceId="com.hpbr.bosszhipin:id/tv_degree"))
            tags = [self.getText(tag) for tag in item.child(resourceId='com.hpbr.bosszhipin:id/ll_skills').child(className='android.widget.TextView')]
            expect_salary = self.getText(item.child(resourceId='com.hpbr.bosszhipin:id/tv_position_salary'))
            
            company_groups = self.browser(resourceId='com.hpbr.bosszhipin:id/ll_work_companies').child(className='android.widget.LinearLayout')
            company_names = []
            companys = []
            for co_item in company_groups:
                compnanyItem = self.getCompanies(co_item)
                if co_item.child(resourceId='com.hpbr.bosszhipin:id/tv_year').exists and compnanyItem['experience_co'] not in company_names:
                    company_names.append(compnanyItem['experience_co'])
                    companys.append(compnanyItem)
                
            if len(companys):
             educate = companys.pop()
            else:
             educate = {
                 'experience_co': '',
                 'experience_period': '',
                 'experience_major': '',
             }
                        
            return {
                "name": name,
                "age": age[:-1] if age is not None else 0,
                "desc": desc,
                "tags": tags,
                "expect_salary": expect_salary,
                "companys": companys,
                "educate_level": level,
                "educate_school": educate['experience_co'],
                "educate_period": educate['experience_period'],
                "educate_major": educate['experience_major'],
                "job_type": self.getText(self.browser.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/tv_expect_position"]')),
                "job_id": self.findJobId() # fixme之后筛选通过jobId 12月6日起
            }
        else:
            return {}

    def confirmPopup(self):
        item = self.browser(resourceId="com.hpbr.bosszhipin:id/tv_positive")
        if item.exists:
            item.click()

    def exchanges(self):
        browser = self.browser
        browser(resourceId="com.hpbr.bosszhipin:id/ll_exchange_wechat").click()
        info = browser.toast.get_message(5.0)
        if info == '双方回复之后才能使用':
            browser(resourceId="com.hpbr.bosszhipin:id/iv_common_word").click()
            browser(resourceId="com.hpbr.bosszhipin:id/ll_text_views").click()
            browser.clear_text()
            browser.send_keys('方便发一份你的简历过来么？')
            browser(resourceId="com.hpbr.bosszhipin:id/tv_send").click()
            browser(resourceId="com.hpbr.bosszhipin:id/ll_exchange_wechat").click()
        time.sleep(1)
        self.confirmPopup()
        browser(resourceId="com.hpbr.bosszhipin:id/ll_exchange_phone").click()
        time.sleep(1)
        self.confirmPopup()
        browser(resourceId="com.hpbr.bosszhipin:id/ll_exchange_resume").click()
        time.sleep(1)
        self.confirmPopup()

    def isEnding(self):
        items = self.getItem()
        caches = self.infos
        keys = caches.keys()
        end_flag = True if items[0].child(text='以下是30天内的聊天记录').exists else False
        
        if self.checkInfo:
            if end_flag and ('asked' in keys or 'wx' in keys or 'phone' in keys):
                if end_flag:
                    caches['sex'] = self.sex()
                caches.update(self.getBaseInfo(items))
            elif end_flag:
                self.exchanges()
            return end_flag
        elif end_flag and 'asked' not in keys:
            self.exchanges()
            return True
        elif 'asked' in keys or 'phone' in keys or 'wx' in keys:
            return True
        
    def getInfo(self):
        return self.infos

    def saveDetail(self):
        info = self.getInfo()
        info['time'] = time.mktime(datetime.date.today().timetuple())
        self.mongo.insert_employees([info])

    def start(self):
        time.sleep(2)
        self.scroll()


if __name__ == "__main__":
    import uiautomator2 as u2

    d = u2.connect('127.0.0.1:7555')
    d.app_start('com.hpbr.bosszhipin')
    d.wait_timeout = 3.0
    detail = Detail(d)
    print(detail.getInfo())
    detail.saveDetail()
