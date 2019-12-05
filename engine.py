from boss_monogo import BossMongo
from job import Job
from detail import Detail
from boss_list import List 
import uiautomator2 as u2
import click
import time
import os
import json
import datetime
import pandas as pd

now = time.mktime(datetime.date.today().timetuple())

class Engine:
    def __init__(self):
        d = u2.connect('127.0.0.1:7555')
        d.app_start('com.hpbr.bosszhipin')
        d.wait_timeout = 3.0
        self.d = d
        # self.job = Job(d)
        # self.list = List(d)
        # self.detail = Detail(d)
        # self.db = BossMongo()

    def db_2_jobs(self, jobs):
        mongo = BossMongo()
        mongo.insert_jobs(jobs)

    def remove_jobs(self):
        job = Job(self.d)
        job.clean()
    
    def add_jobs(self):
        d = self.d
        job = Job(d)
        job.add_jobs()
        d.press("back")

    def get_filters(self):
        filter_list = []
        d = self.d
        d(resourceId="com.hpbr.bosszhipin:id/container").scroll.vert.toBeginning()
        d(resourceId="com.hpbr.bosszhipin:id/filter_tv").click()
        items = d(resourceId="com.hpbr.bosszhipin:id/chat_filter_name_tv", text="沟通职位").sibling(resourceId='com.hpbr.bosszhipin:id/chat_filter_name_rv').child(resourceId='com.hpbr.bosszhipin:id/cb_selector')
        filter_list = [item.get_text() for item in items if item.get_text() != '全部']
        d(resourceId="com.hpbr.bosszhipin:id/confirm").click()
        return filter_list
        
    def check_list(self, checkInfo):
        d = self.d
        mongo = BossMongo()
        filters = self.get_filters()
        print(filters)
        if len(filters):
            for filt in filters:
                lists = List(d, filt, '5de078141e7c2bb87fe6b44c', checkInfo=checkInfo)
                infos = lists.getInfos()
                if len(infos) and checkInfo:
                    mongo.insert_employees(infos)
                d.press("back")
                time.sleep(3)

    def export_2_excel(self):
        mongo = BossMongo()
        jobs = mongo.get_employees(now)
        for job in jobs:
            print(mongo.rename_columns(pd.DataFrame(job['employees'])))
            mongo.write_to_excel(job['title'], mongo.rename_columns(pd.DataFrame(job['employees'])))
        mongo.save_excel()


engine = Engine()
@click.group()
def cli():
    pass

@click.command()
def add_jobs():
    engine.add_jobs()

@click.command()
@click.option('--check', '-c', type=bool, default=False)
def boss_list(check):
    engine.check_list(check)
    # if check:
    #     engine.remove_jobs()

@click.command()
def export_excel():
    engine.export_2_excel()

@click.command()
@click.option('--input', '-f', default='jobs.json', type=click.File('r', 'utf-8'))
def import_jobs(input):
    engine.db_2_jobs(json.loads(input.read()))

cli.add_command(add_jobs)
cli.add_command(boss_list)
cli.add_command(export_excel)
cli.add_command(import_jobs)

if __name__ == "__main__":
    cli()