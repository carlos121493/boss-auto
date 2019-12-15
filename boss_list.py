import time
import datetime
from base import Base
from detail import Detail
from boss_monogo import BossMongo
from uiautomator2.exceptions import UiObjectNotFoundError

now = time.mktime(datetime.date.today().timetuple())
class List(Base):

    def __init__(self, browser, name=None, checkInfo = False):
        self.browser = browser
        if name:
          browser(resourceId="com.hpbr.bosszhipin:id/filter_tv").click()
          browser(resourceId="com.hpbr.bosszhipin:id/cb_selector", text=name).click()
          browser(resourceId="com.hpbr.bosszhipin:id/confirm").click()
          
        if self.container is None:
          self.container = browser(resourceId='com.hpbr.bosszhipin:id/contact_ll')
          self.firstName = self.getFirstName()
          
        self.checked = []
        self.currentList = []
        self.lastList = []
        self.allList = []
        self.alldetails = []
        self.checkInfo = checkInfo
        self.time = now
        self.scrollToEnd()
        time.sleep(2)
        self.start()
        time.sleep(1)

    def scrollToEnd(self):
        self.container.scroll.vert.toEnd()

    def getFirstName(self):
        self.container.scroll.vert.toBeginning()
        items = self.getItem()
        try:
            first_item = items[0].child(resourceId='com.hpbr.bosszhipin:id/tv_name')
            return first_item.get_text() if first_item.exists else ''
        except:
            return ''

    def getItem(self):
        '''识别每一项'''
        return self.container.child(resourceId='com.hpbr.bosszhipin:id/rl_content_view')

    def scroll(self, start=True):
        self.checked = []
        super().scroll(start)

    def cleanCaches(self):
        self.allList.extend(self.currentList)
        self.lastList = self.currentList.copy()
        self.currentList = []

    def checkInvalide(self, name, item, force=False):
        if name is None or name in self.checked:
            return True

        self.checked.append(name)
        # 不是今天的数据不管
        timeInfo = item.child(resourceId='com.hpbr.bosszhipin:id/tv_time').get_text()
        if ':' not in timeInfo:
            return True

        # 最后一页会重复
        if name in self.allList:
            return True

        # 只看红点模式下不管
        child = item.child(resourceId='com.hpbr.bosszhipin:id/tv_not_read_count')
        if (force is False and self.checkInfo is False) and bool(child.exists) is False:
            return True
        return name in self.lastList or name in self.currentList

    def employeeDetail(self):
        try:
            detail = Detail(self.browser, self.checkInfo)
            info = detail.getInfo()
            if len(info.keys()):
                info['time'] = self.time
                self.alldetails.append(info)
        except UiObjectNotFoundError:
            return ''
     
    def getDetail(self):
        items = self.getItem()
        d = self.browser
        for item in items:
            if item.exists:
                name = self.getText(item.child(resourceId='com.hpbr.bosszhipin:id/tv_name'))
                if self.checkInvalide(name, item):
                    continue
                else:
                    if self.checkInfo is False:
                        print('name:{0}'.format(name))
                    self.currentList.append(name)
                    item.click()
                    time.sleep(1)
                    self.employeeDetail()
                    time.sleep(1)
                    d.press("back")
        self.cleanCaches()

    def isEnding(self):
        '''结束'''
        items = self.getItem()
        if len(items) == 0:
            return True
        return True if self.browser(text=self.firstName).exists else False

    def getInfos(self):
        return self.alldetails

    def start(self):
        self.scroll()


class ListAll(List):
    def __init__(self, browser, name, checkInfo=False): 
        self.container = browser(className='android.widget.ExpandableListView')
        # self.names = [stack['name'] for stack in list(mongo.employCollection.find({}, { '_id': 0, 'name': 1 }))]
        self.firstName = '筛选'
        super().__init__(browser, name, checkInfo)

    def checkInvalide(self, name, item):
        superCheck = super().checkInvalide(name, item, force=True)
        if superCheck:
            return True

        child = item.child(resourceId='com.hpbr.bosszhipin:id/tv_none_read')
        return self.checkInfo is False and bool(child.exists) is False
        
    def scrollToEnd(self):
        '''找到开始起点位置'''
        hasLastItem = self.browser(text='昨天').exists
        if bool(hasLastItem) is not True:
            self.container.scroll.vert.forward()
            self.scrollToEnd()

    def getItem(self):
        '''识别每一项'''
        return self.container.child(resourceId='com.hpbr.bosszhipin:id/mRootview')

if __name__ == "__main__":
    import uiautomator2 as u2

    d = u2.connect('127.0.0.1:7555')
    d.app_start('com.hpbr.bosszhipin')
    d.wait_timeout = 3.0
    # d(resourceId="com.hpbr.bosszhipin:id/ll_tab_3").click()

    # def init_items():
    #     filter_list = []
    #     d(resourceId="com.hpbr.bosszhipin:id/container").scroll.vert.toBeginning()
    #     d(resourceId="com.hpbr.bosszhipin:id/filter_tv").click()
    #     items = d(resourceId="com.hpbr.bosszhipin:id/chat_filter_name_tv", text="沟通职位").sibling(resourceId='com.hpbr.bosszhipin:id/chat_filter_name_rv').child(resourceId='com.hpbr.bosszhipin:id/cb_selector')
    #     filter_list = [item.get_text() for item in items if item.get_text() != '全部']
    #     d(resourceId="com.hpbr.bosszhipin:id/confirm").click()
    #     return filter_list

    # # 筛选后
    # filters = init_items()
    # print(filters)
    # if len(filters):
    #   for filter in filters:
    #       list = List(d, filter, '5de078141e7c2bb87fe6b44c')
    #       mongo = BossMongo()
    #       print(list.getInfos())
    #       mongo.insert_employees(list.getInfos())
    # d.press("back")
    
    # 只有红点
    # list = List(d, '项目经理', '5de078141e7c2bb87fe6b44c', checkInfo=False)

    # 所有
    # mongo = BossMongo()
    # list = ListAll(d, None, '5de078141e7c2bb87fe6b44c')
    # print(list.getInfos())
    # mongo.insert_employees(list.getInfos())
    # mongo = BossMongo()
    lists = ListAll(d, None, checkInfo=False)
    infos = lists.getInfos()
    print(len(infos))
    # print(len(infos))
    # if len(infos):
    #     mongo.insert_employees(infos)
    # d.press("back")