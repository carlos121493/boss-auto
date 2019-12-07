
from uiautomator2.exceptions import UiObjectNotFoundError
import time

class Base:
    container = None
    browser = None

    def getText(self, item):
        try:
            if item.exists:
                return item.get_text()
        except UiObjectNotFoundError:
            return ''

    def getDetail(self):
        '''识别每一项'''
        pass

    def isEnding(self):
        '''结束'''
        return ''

    def scroll(self, start=True):
        try:
            self.getDetail()
            ending = self.isEnding()
            self.container.scroll.vert.backward(steps=60)
            time.sleep(3)
            if ending is not True:
                return self.scroll(start=False)
            elif start is not True:
                return self.getDetail()  # 如果是一页的话，需要考虑
        except UiObjectNotFoundError:
            cancel = self.browser(resourceId="com.hpbr.bosszhipin:id/tv_cancel")
            if cancel.exists:
                cancel.click()
                time.sleep(1)
            self.scroll(start=False)
