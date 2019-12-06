import time
import random
import math
import re
from boss_monogo import BossMongo
from uiautomator2.exceptions import UiObjectNotFoundError


class Job:
    monogo = BossMongo()

    def __init__(self, browser):
        self.browser = browser

    def delete_item(self, job):
        browser = self.browser
        job.click()
        time.sleep(1)
        browser(resourceId='com.hpbr.bosszhipin:id/btn_reset').click()
        pos = browser(resourceId="com.hpbr.bosszhipin:id/tv_positive")
        if pos.exists:
            pos.click()
            browser.press('back')
            return
        time.sleep(1)
        browser(resourceId="com.hpbr.bosszhipin:id/mNestScrollView").scroll.vert.toEnd()
        browser(resourceId="com.hpbr.bosszhipin:id/btn_confirm").click()
        browser(resourceId="com.hpbr.bosszhipin:id/tv_positive").click()

    def filter_job(self, job, job_name):
        job_keys = job.keys()
        if 'sub_title' in job_keys and job_name in job['sub_title']:
            return True
        return job['title'] == job_name 

    def clean(self):
        browser = self.browser
        try:
            db_jobs = self.get_jobs_from_db()
            browser(resourceId="com.hpbr.bosszhipin:id/ll_tab_4").click()
            browser(resourceId="com.hpbr.bosszhipin:id/tv_sub_title", text="管理职位").click()
            time.sleep(2)
            jobs = browser(resourceId='com.hpbr.bosszhipin:id/lv_ptr').child(className='android.view.ViewGroup')
            for job in jobs:
                time.sleep(4)
                job_title = job.child(resourceId="com.hpbr.bosszhipin:id/tv_job_name").get_text()
                # 获取job 信息
                job_db_item = list(filter(lambda j: self.filter_job(j, job_title), db_jobs))
                if len(job_db_item) != 0:
                    job_db_item = job_db_item[0]
                else:
                    job_db_item = {}
                if 'hot' in job_db_item.keys() and job_db_item['hot']:
                    continue
                self.delete_item(job)
        except UiObjectNotFoundError:
            browser.press('back')

    def get_jobs_from_db(self):
        lists = list(self.monogo.find_jobs())
        return lists

    def update_jobs(self, types, resource):
        if 'type' not in resource.keys():
            [jobType, subType, endType] = types
            self.monogo.update_job({'title': resource['title']}, {'type': jobType, 'subType': subType, 'endType': endType})

    def update_prices(self, resource):
        salaries = d(resourceId="com.hpbr.bosszhipin:id/tv_salary_content").get_text()
        self.monogo.update_job({'title': resource['title']}, {'salaries': salaries})

    def choose_loc(self, resource):
        d = self.browser
        locate = d(resourceId="com.hpbr.bosszhipin:id/content", text="请选择工作地点")
        province = '上海'
        keywords = '千樱'
        details = '1号楼303室'
        if 'location' in resource.keys() and len(resource['location']) == 3:
            province = resource['location'][0]
            keywords = resource['location'][1]
            details = resource['location'][2]
        if locate.exists:
            d(resourceId="com.hpbr.bosszhipin:id/content", text="请选择工作地点").click()
            d(resourceId="com.hpbr.bosszhipin:id/content").click()
            d(resourceId="com.hpbr.bosszhipin:id/tv_city").click()
            d(text=province).click()
            d(resourceId="com.hpbr.bosszhipin:id/et_input").click()
            d.clear_text()
            d.send_keys(keywords)
            d.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/rv_address"]/android.view.ViewGroup[1]').click()
            d(resourceId="com.hpbr.bosszhipin:id/et_house_number").click()
            d.clear_text()
            d.send_keys(details)
            d(resourceId="com.hpbr.bosszhipin:id/btn_confirm").click()
            
    def scrollToItem(self, item, steps, forward):
        for i in range(steps):
            if forward:
                item.scroll.vert.forward()
            else:
                item.scroll.vert.backward()
    
    def find_salary(self, source):
        d = self.browser
        keys = source.keys()
        low = source['low'] if 'low' in keys else None
        high = source['high'] if 'high' in keys else None
        mid = 10
        low_sa = round(int(low) / 1000) if low != None else random.randint(2,4) + 10
        high_sa = round(int(high) / 1000) - low_sa if high != None else random.randint(1,4)

        self.scrollToItem(d(resourceId="com.hpbr.bosszhipin:id/wv_left_wheel"), math.floor(abs(low_sa-mid) / 4), low_sa > 10)
        self.scrollToItem(d(resourceId="com.hpbr.bosszhipin:id/wv_right_wheel"), math.floor(high_sa / 4), True)
    
    def choose_select(self, source):
        d = self.browser
        d(resourceId="com.hpbr.bosszhipin:id/tv_exp_content").click()
        time.sleep(1)
        d(resourceId="com.hpbr.bosszhipin:id/wv_wheelview").scroll.vert.toEnd()
        d.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/wesTabContainer"]/android.widget.FrameLayout[2]').click()
        time.sleep(1)
        d(resourceId="com.hpbr.bosszhipin:id/wv_wheelview").scroll.vert.toBeginning()
        d(resourceId="com.hpbr.bosszhipin:id/wv_wheelview").scroll.vert.toBeginning()
        time.sleep(1)
        d.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/wesTabContainer"]/android.widget.FrameLayout[3]').click()
        keys = source.keys()
        self.find_salary(source)
        
        days_select = d(resourceId="com.hpbr.bosszhipin:id/wv_month_number")
        if days_select.exists:
            months = random.randint(1, 2)
            for k in range(0, months):
                d(resourceId="com.hpbr.bosszhipin:id/wv_month_number").scroll.vert.forward()
        d(resourceId="com.hpbr.bosszhipin:id/iv_ok").click() 

    def getSubType(self, name):
        d = self.browser
        d(resourceId="com.hpbr.bosszhipin:id/et_input").click()
        d.clear_text()
        d.send_keys(name)
        time.sleep(1)
        item = d(resourceId="com.hpbr.bosszhipin:id/rv_list").child(className='android.view.ViewGroup')[0]
        desc_item = item.child(resourceId="com.hpbr.bosszhipin:id/tv_job_desc")
        if desc_item.exists is not True:
            d.press('back')
            item.click()
            return ['', '', '']
        desc = desc_item.get_text()
        item.click()
        return [name.strip() for name in re.split(r' > ', desc)]

    def add_keywords(self, title):
        d = self.browser
        d(resourceId="com.hpbr.bosszhipin:id/content", text="被选中的关键词将突出展示给牛人").click()
        d(className='android.widget.ScrollView').scroll.vert.toEnd()
        time.sleep(1)
        customize = d(text='+ 自定义')
        time.sleep(2)
        if customize.exists:
            customize.click()
            d(resourceId="com.hpbr.bosszhipin:id/et_input").click()
            d.clear_text()
            d.send_keys(title)
            d(resourceId="com.hpbr.bosszhipin:id/btn_positive").click()
        d.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/cl_title"]/android.view.ViewGroup[2]').click()

    def intra_info(self):
        d = self.browser
        intra = d(resourceId="com.hpbr.bosszhipin:id/content", text="请填写实习要求")
        if intra.exists:
            intra.click()
            time.sleep(1)
            d(resourceId="com.hpbr.bosszhipin:id/mComplete").click()
            time.sleep(1)
            
    def add_job(self, resource):
        d = self.browser
        if d(text=resource['title']).exists:
            return    
        d(resourceId="com.hpbr.bosszhipin:id/btn_post_job").click()
        time.sleep(3)
        negative = d(text='重新发布')
        if negative.exists:
            negative.click()
            time.sleep(1)
        # 填写职位名称
        d(resourceId="com.hpbr.bosszhipin:id/content", text="请填写职位名称").click()
        time.sleep(1)
        types = self.getSubType(resource['title'])
        self.update_jobs(types, resource)
        time.sleep(2)
        popup_ben = d(resourceId='com.hpbr.bosszhipin:id/tv_positive')
        if popup_ben.exists:
            popup_ben.click()
        time.sleep(1)
        self.choose_select(resource)
        time.sleep(1)
        self.update_prices(resource)
        # 职位描述
        d(resourceId="com.hpbr.bosszhipin:id/content", text="请填写职位描述").click()
        time.sleep(1)
        d(resourceId="com.hpbr.bosszhipin:id/et_input").click()
        d.clear_text()
        d.send_keys(resource['desc'])
        d.send_keys(u'\n\n')
        d.send_keys(resource['need'])
        d.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/cl_title"]/android.view.ViewGroup[2]').click()
        time.sleep(1)
        # 选择地址
        self.choose_loc(resource)
        time.sleep(1)
        # 滚动到下方
        d(className='android.widget.ScrollView').scroll.vert.toEnd()
        time.sleep(2)
        # 关键词
        self.add_keywords(resource['title'])
        time.sleep(1)
        # 保存
        # 如果是实习生
        self.intra_info()
        d(resourceId="com.hpbr.bosszhipin:id/btn_complete").click()
        time.sleep(2)
        confirm = d(resourceId="com.hpbr.bosszhipin:id/btn_hire")
        if confirm.exists:
            confirm.click()
            time.sleep(4)
            return self.add_jobs()
        payed = d(resourceId="com.hpbr.bosszhipin:id/btn_hire")
        if payed.exists:
            d.press("back")
            time.sleep(2)
            d.press("back")
            time.sleep(2)
        start_btn = d(resourceId='com.hpbr.bosszhipin:id/tv_start_recruit')
        if start_btn.exists:
            start_btn.click()
            time.sleep(2)
        d(resourceId="com.hpbr.bosszhipin:id/tv_continue").click()
        time.sleep(2)

    def add_template_job(self, job, title):
        j = job.copy()
        j['title'] = title
        self.add_job(j)

    def add_jobs(self):
        browser = self.browser
        browser(resourceId="com.hpbr.bosszhipin:id/ll_tab_4").click()
        browser(resourceId="com.hpbr.bosszhipin:id/tv_sub_title", text="管理职位").click()
        time.sleep(3)
        jobs = self.get_jobs_from_db()
        for job in jobs:
            self.add_job(job)
            if 'sub_title' in job.keys():
                subs_jobs = job['sub_title']
                for sub_title in subs_jobs:
                    cp_job = job.copy()
                    cp_job['title'] = sub_title
                    self.add_job(cp_job)    

if __name__ == "__main__":
    import uiautomator2 as u2

    d = u2.connect('127.0.0.1:7555')
    d.app_start('com.hpbr.bosszhipin')
    d.wait_timeout = 3.0
    # 清除jobs
    job = Job(d)
    # 删除jobs
    # job.clean()
    # 增加jobs
    job.add_jobs()
    d.press("back")
