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
          
        self.container.scroll.toBeginning()
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
        # self.container.child_by_text('昨天', allow_scroll_search=True, className="com.hpbr.bosszhipin:id/tv_time")
        hasLastItem = self.browser(text='昨天').exists
        if bool(hasLastItem) is not True:
            self.container.scroll.vert.forward()
            self.scrollToEnd()

    def getItem(self):
        '''识别每一项'''
        return self.container.child(resourceId='com.hpbr.bosszhipin:id/mRootview')

class ListLastDay(ListAll):
    def __init__(self, browser):
        super().__init__(browser, None, True)

    def scrollToEnd(self):
        '''找到开始起点位置'''
        try:
            childs = self.getItem()
            lastChild = childs[len(childs) - 1].child(resourceId="com.hpbr.bosszhipin:id/tv_time")
            lastText = lastChild.get_text()
            if '月' not in lastText:
                self.container.scroll.vert.forward()
                self.scrollToEnd()
        except:
            print('ok')

if __name__ == "__main__":
    import uiautomator2 as u2

    d = u2.connect('127.0.0.1:7555')
    d.app_start('com.hpbr.bosszhipin')
    d.wait_timeout = 3.0

    ListLastDay(d)
