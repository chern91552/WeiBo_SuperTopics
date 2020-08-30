## 🎐WeiBo_SuperTopics

> 使用教程日后有时间更新，接口写了一点，可自行扩展功能
>
> 欢迎star✨，有问题可以提issue一起学习交流



### 🌍功能简介

- 关注超话签到
- 每日积分获取
- 超话打榜
- 喻言超话帖子评论转发点赞
- 任务中心查询积分
- 微信推送消息



### 🚀运作流程

##### 1、Secrets

```python
# 设置如下secrets字段:

COOKIE  # 通过登录https://m.weibo.cn/获取cookie
S  # 通过抓包微博国际版APP签到请求获取
PICK  # 设置自己打榜的超话名字,例如：喻言
SCKEY  # 通过https://sc.ftqq.com/3.version获取
```

##### 2、Schedule

```python
# 由于害怕未知情况下的微博api请求异常，因此设置早上6点和晚上10点中进行两次任务
# 五位数(空格分隔)分别为分钟、小时、天、月、一个星期的第几天
# 国际时与北京时的查询网站：http://www.timebie.com/cn/universalbeijing.php

schedule:
	- cron: 0 14,22 * * *
```

##### 3、DailyTask

```python
# 有能力可以自定义自己的每日任务(加入评论转发点赞等)
# self.log.append()是为了微信推送看上去更干净
# 每日超话签到+每日积分获取+超话打榜+喻言超话评论+任务中心

def daily_task(self, cookie, s, pick_name, sckey):
    self.set_cookie(cookies=cookie)
    ch_list = self.get_ch_list()
    print("获取个人信息")
    self.log.append("#### 💫‍User：")
    self.log.append("```")
    self.get_profile()
    self.log.append("```")
    print("开始超话签到")
    self.log.append("#### ✨CheckIn：")
    self.log.append("```")
    for i in ch_list:
        time.sleep(self.seconds)
        self.check_in(s, i)
    self.log.append("```")
    print("获取每日积分")
    self.log.append("#### 🔰DailyScore：")
    self.log.append("```")
    self.get_day_score()
    self.log.append("```")
    print("开始打榜")
    self.log.append("#### 💓Pick：")
    self.log.append("```")
    self.get_score_bang([i for i in ch_list if i["title"] == pick_name])
    self.log.append("```")
    print("喻言超话开始评论~~")
    self.log.append("#### ✅Post：")
    self.log.append("```")
    self.yu_yan([i["url"] for i in ch_list if i["title"] == "喻言"])
    self.log.append("```")
    print("查询任务中心")
    self.log.append("#### 🌈TaskCenter：")
    self.log.append("```")
    self.task_center()
    self.log.append("```")
    self.server_push(sckey)
```



<<<<<<< HEAD
### 🚧使用帮助

> 复杂的食用方式待更新

=======
### 🚧使用步骤

> 复杂的食用方式待更新

##### 1、cookie的获取方式

##### 2、s参数的获取方式

##### 3、sckey的获取方式

##### 4、fork本仓库到自己的库中

##### 5、设置screts字段

##### 6、修改README.md触发任务

>>>>>>> 8891e54... commit


### 🏍更新记录

<<<<<<< HEAD
=======
🧭2020/08/30：取消无意义的print打印，附赠一个成果图

>>>>>>> 8891e54... commit
**🎉2020/08/29：增加喻言超话评论，增加任务中心积分显示**

**💤2020/08/28：增加打榜计划，优化微信推送格式**

**🌈2020/08/27：第一次提交**



<<<<<<< HEAD
=======




### 🚁成果图

![](https://cdn.jsdelivr.net/gh/ReaJason/WeiBo_SuperTopics/Pictures/result.jpg)



### 🏝Tips

1. 代码完善得差不多了，关注喻言超话可自动评论转发点赞喻言超话第一页的帖子
2. 微博手机web版的cookie有效时间很长久，不像web端的登出就作废了
3. 有能力的可自行抓微博国际版app的签到请求(手机无root推荐mumu模拟器)



>>>>>>> 8891e54... commit
### ♻致谢

感谢[wxy1343/weibo_points](https://github.com/wxy1343/weibo_points)的获取每日积分接口参考