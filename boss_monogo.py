# coding=utf-8

from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from util import CachedCalled, decTime
import time
import json
import os
import datetime
import pandas as pd

lastDay = time.mktime((datetime.date.today() - datetime.timedelta(1)).timetuple())
now = time.mktime(datetime.date.today().timetuple())
root = os.getcwd()


class BossMongo:
    def __init__(self):
        client = MongoClient(host='127.0.0.1', port=27017)
        db = client['employ']
        self.jobsCollection = db['jobs']
        self.employCollection = db['employees']

    def insert_jobs(self, jobs):
        self.jobsCollection.insert_many(jobs)

    def update_job(self, query, new):
        self.jobsCollection.update_one(query, {'$set': new})

    def insert_employees(self, employees):
        try:
          self.employCollection.insert_many(employees)
        except BulkWriteError:
          print(str(employees))

    def get_employees(self, time):
        return self.jobsCollection.aggregate([{  
           '$addFields': {
                'titles': {
                    '$cond': {
                        'if': {'$ifNull': ['$sub_title', False]},
                        'then': {'$concatArrays': [['$title'], '$sub_title']},
                        'else': ['$title']
                    }
                }
           },
        },{
          '$lookup': {
                'from': 'employees',
                'let': {'end_type': '$endType', 'titles': '$titles'},
                'pipeline': [{
                    '$match': {
                        '$expr': {
                            '$and': [
                                {'$eq': ['$time', time]},
                                {'$or': [{'$eq': ['$job_type', '$$end_type']}, {'$in': ['$job_type', '$$titles']}]}
                            ]
                        }
                    }
                    },
                    {
                        '$project': {
                            '_id': 0,
                            'name': 1,
                            'sex': 1,
                            'age': 1,
                            'wx': 1,
                            'phone': 1,
                            'desc': 1,
                            'expect_salary': 1,
                            'educate_school': 1,
                            'educate_period': 1,
                            'educate_major': 1,
                            'tagInfo': {
                                '$reduce': {
                                    'input': '$tags',
                                    'initialValue': '',
                                    'in': {'$concat': ['$$value', ' ' ,'$$this']}
                                }
                            },
                            'companyInfo': {
                                '$reduce': {
                                    'input': '$companys',
                                    'initialValue': '',
                                    'in': { '$concat': ['$$value', '', '$$this.experience_co', '/', '$$this.experience_major', '/', '$$this.experience_period']}
                                }
                            }
                        }
                    }
                ],
                'as': 'employees'
                }
        }])

    def rename_columns(self, data):
        return data.rename(columns={"name": "姓名", "sex": "性别", "age": "年龄", "tagInfo": "标签", "wx": "微信", "phone": "手机", "desc": "描述", "expect_salary": "期望薪资", "companyInfo": "职业经历", "educate_school": "毕业院校", "educate_period": "上学时间", "educate_major": "主修专业", "educate_level": "最高学历"})

    def save_excel(self, f, datas):
        excelPath = os.path.join(root, 'jobs-{0}.xlsx'.format(f))
        writer = pd.ExcelWriter(excelPath)
        for (sheetName, data) in datas:
            print(sheetName, data)
            data.to_excel(writer, sheet_name=sheetName, startcol=0, index=False)
        writer.save()

    def find_last(self):
        return self.employCollection.find({'time': now, 'asked': True, 'job_type': {'$ne': 'Java'}}, { 'job_id': 0, 'time':0, 'asked': 0, '_id': 0})

    def find_jobs(self):
        return list(self.jobsCollection.find())

    @decTime
    @CachedCalled()
    def find_job(self, endType):
        return list(self.jobsCollection.find({'endType': endType}))

    def output(self, data):
      # writer
      pd.DataFrame(list(data))


if __name__ == "__main__":
    mongo = BossMongo()
    # 保存到excel
    # jobs = mongo.get_employees(now)
    # for job in jobs:
    #     print(mongo.rename_columns(pd.DataFrame(job['employees'])))
    #     mongo.write_to_excel(job['title'], mongo.rename_columns(pd.DataFrame(job['employees'])))
    # mongo.save_excel()
    
    # 插入jobs
    # jobFile = os.path.relpath('jobs.json', '.')
    # with open(jobFile, encoding='utf-8') as f:
    #     jobs = json.loads(f.read())
    #     mongo.insert_jobs(jobs)
