### 准备

1. 安装python，git（注意配置好环境变量）
2. 安装vscode，这样vscode.env就会生效，否则pycharm要另外配
3. 安装mumu，并在mumu上安装boss直聘并登录
4. 安装adb (https://pan.baidu.com/s/10wDZNTS8Ak8PdRyaTkPLaA) 从这里下载并添加到环境变量里。
5. 安装mongodb

---

### 开始
1. ``` adb connect 127.0.0.1:7555 ```

> cd 到目录
2. ``` pip install -r requirements.txt ```
3. ``` pip install -e . ```

> 所有操作在模拟器上均有操作，可等待模拟器操作完成后验证代码执行是否有效
4. 接到新职位和职位内容 参考jobs.json中已有字段
    以json格式录入到jobs.json中
    输入title 并保证 title要在boss直聘上找得到
    保证下拉列表里有内容
    ![]('select.jpg')

    ['jobs.json解释']('https://github.com/carlos121493/boss-auto#jobs.json%E8%A7%A3%E9%87%8A')
    ```boss import-jobs -f jobs.json```

5. 早上执行boss add_jobs 将录入的职位加入, 会将数据库的职位加入到boss直聘中
    ``` boss add-jobs```

6. 每隔大概2~3个小时，批量检查小红点的用户是否发送要微信，手机号信息
    ``` boss boss-list```

7. 晚上将所有信息整理到数据库中（每天执行一次，因为用户以时间维度加入到数据库中，防止重复）
    ``` boss boss-list -c```

8. 数据录入好后导出到当前目录jobs.xlsx中
    ``` boss export-excel```

---

### jobs.json解释

1. title 应聘职位
2. desc 应聘说明
3. need 应聘要求
4. from 需求来源
5. low 最低工资（可选）
6. high 最高工资 (可选)
7. location （可选,默认不写千樱信息总部, 填写可写成列表location: ['省市', '区', '详细地址']如 location: ['上海', '浦东新区', '2-1-302']）
8. hot 是否是热门职位（要付费，不删除）

---

### 进阶
1. 如有兴趣可以安装
``` pip install weditor ```
可以查看android原生结构

2. 有兴趣可以安装mongo compass
可以查看数据结构