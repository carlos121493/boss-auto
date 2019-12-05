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
    执行
    jobs.json
    ```boss import-jobs -f jobs.json```

3. 早上执行boss add_jobs 将录入的职位加入, 会将数据库的职位加入到boss直聘中
    ``` boss add-jobs```

4. 每隔大概2~3个小时，批量检查小红点的用户是否发送要微信，手机号信息
    ``` boss boss-list```

5. 晚上将所有信息整理到数据库中（每天执行一次，因为用户以时间维度加入到数据库中，防止重复）
    ``` boss boss-list -c```

6. 数据录入好后导出到当前目录jobs.xlsx中
    ``` boss export-excel```
---

### 进阶
1. 如有兴趣可以安装
``` pip install weditor ```
可以查看android原生结构

2. 有兴趣可以安装mongo compass
可以查看数据结构