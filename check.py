import time
import datetime
import re

import requests


class WeiBo:

    def __init__(self):
        self.profile_url = "https://m.weibo.cn/profile/info"
        self.config_url = "https://m.weibo.cn/api/config"
        self.get_ch_url = "https://m.weibo.cn/api/container/getIndex?containerid=100803_-_followsuper&since_id={}"
        self.check_url = "https://api.weibo.cn/2/page/button"
        self.web_check_url = "https://weibo.com/p/aj/general/button"
        self.day_score_url = "https://huati.weibo.cn/aj/super/receivescore"
        self.get_super_score_url = "https://huati.weibo.cn/aj/super/getscore"
        self.task_center_url = "https://huati.weibo.cn/aj/super/taskcenter"
        self.pick_url = "https://huati.weibo.cn/aj/super/picktop"
        self.report_story_url = "https://m.weibo.cn/api/statuses/repost"
        self.comment_story_url = "https://m.weibo.cn/api/comments/create"
        self.star_story_url = "https://m.weibo.cn/api/attitudes/create"
        self.seconds = 5
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36 ",
            "cookie": ""
        }
        self.gsid = ""
        self.log = []

    def set_cookie(self, cookies):
        """
        配置类对象的cookie和gsid参数
        :param cookies: 通过 https://m.weibo.cn/ 登陆获取cookie
        :return: None
        """
        self.headers['cookie'] = cookies
        self.gsid = re.findall("SUB=(.*?);", cookies)[0]

    def get_profile(self):
        """
        获取个人信息
        :return: user_dict
        """
        profile_response = requests.get(self.profile_url, headers=self.headers)
        user = profile_response.json()["data"]["user"]
        user_dict = {
            "profile_id": user["id"],
            "profile_name": user["screen_name"],
            "profile_description": user["description"] if user["description"] else "nothing",
            "profile_avatar": user["avatar_hd"],
            "profile_gender": "fmale" if user["gender"] == "f" else "male",
            "statuses_count": user["statuses_count"],
            "follow_count": user["follow_count"],
            "followers_count": user["followers_count"],
            "profile_url": user["profile_url"],
            "all_container_id": profile_response.json()["data"]["more"].split("/")[-1]
        }
        self.log.append(f"""ID: {user["id"]}
用户名: {user["screen_name"]}
简介: {user["description"] if user["description"] else "这个人很懒，什么也没有"}
微博数: {user["statuses_count"]}
关注数: {user["follow_count"]}
粉丝数: {user["followers_count"]}
        """)
        print(f"User:{user['screen_name']}")
        # print(f"User:{user['screen_name']}")
        return user_dict

    def get_ch_list(self):
        """
        获取超话关注列表
        :return: ch_list(列表套字典)
        """
        ch_list = []
        since_id = ""
        while True:
            ch_res = requests.get(
                url=self.get_ch_url.format(since_id),
                headers=self.headers
            )
            ch_json = ch_res.json()["data"]["cards"][0]["card_group"]
            for ch in ch_json:
                if ch["card_type"] == "8":
                    ch_dict = {
                        "title": ch["title_sub"],
                        "level": ch["desc1"][-1],
                        "status": ch["buttons"][0]["name"],
                        "url": ch["scheme"],
                        "id": re.findall('[0-9a-z]{38}', ch["scheme"])[0]
                    }
                    # msg = '标题：{}，等级：{}级，签到状态：{}'.format(ch_dict["title"], ch_dict["level"], ch_dict["status"])
                    # print(msg)
                    ch_list.append(ch_dict)
            since_id = ch_res.json()["data"]["cardlistInfo"]["since_id"]
            if since_id == "":
                ch_list.sort(key=lambda x: x["level"], reverse=True)
                return ch_list

    def get_story_list(self, ch_url):
        """
        获取超话微博（第一页）获取多页设置最后if count == 1:中的 1 即可
        :param ch_url: 超话url
        :return: story_list（列表套字典）
        """
        count = 0
        since_id = ""
        story_list = []
        while True:
            index_url = f"https://m.weibo.cn/api/container/getIndex?{ch_url.split('?')[-1]}&since_id={since_id}"
            index_res = requests.get(index_url, headers=self.headers)
            cards = index_res.json()["data"]["cards"]
            scheme_list = []
            for card_group in cards:
                if card_group["itemid"] == "":
                    for card in card_group["card_group"]:
                        if card["card_type"] == "9":
                            scheme_list.append(card["scheme"])
            for scheme in scheme_list:
                show_url = f"https://m.weibo.cn/statuses/show?id={re.findall('[0-9a-zA-Z]{9}', scheme)[0]}"
                detail_res = requests.get(show_url, headers=self.headers)
                story_dict = {
                    "user": detail_res.json()["data"]["user"]["screen_name"],
                    "mid": detail_res.json()["data"]["id"]
                }
                story_list.append(story_dict)
            since_id = index_res.json()["data"]["pageInfo"]["since_id"]
            count = count + 1
            if count == 1:
                return story_list

    def check_in(self, s, ch_dict):
        """
        微博国际版APP签到接口
        :param s: 特定的数字，抓包获取
        :param ch_dict: 超话信息字典,具体格式请看get_ch_list函数中
        :return:
        """
        check_data = {
            "c": "weicoabroad",
            "s": s,
            "wm": "2468_1001",
            "gsid": self.gsid,
            "from": "1299295010",
            "source": "4215535043",
            "lang": "zh_CN",
            'ua': "Redmi+K20+Pro+Premium+Edition_10_WeiboIntlAndroid_3610",
            "request_url": f"http%3A%2F%2Fi.huati.weibo.com%2Fmobile%2Fsuper%2Factive_checkin%3Fpageid%3D{ch_dict['id']}",
        }
        check_res = requests.get(
            url=self.check_url,
            params=check_data,
        )
        # print(check_res.text)
        errmsg = check_res.json().get('errmsg')
        if errmsg:
            msg = f'TopicName：{ch_dict["title"]}  s参数设置有误'
            # print(msg)
            self.log.append(msg)
            return msg

        else:
            c_msg = check_res.json()["msg"].replace("\n", "/")
            msg = f'TopicName：{ch_dict["title"]}\nLevel：{ch_dict["level"]}\nMessage：{c_msg}'
            # print(msg)
            self.log.append(msg)
            return msg

    def get_day_score(self):
        """
         超话每日积分领取
        :return:
        """
        day_score_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://huati.weibo.cn'
        }
        day_score_headers.update(self.headers)
        score_data = {
            'type': 'REQUEST',
            'user_score': 999
        }
        day_score_res = requests.post(
            url=self.day_score_url,
            headers=day_score_headers,
            data=score_data
        )
        if day_score_res.json()["code"] == 100000:
            msg = f'今日签到积分获取：{day_score_res.json()["data"]["add_score"]}分'
            # print(msg)
            self.log.append(msg)
            return msg
        elif day_score_res.json()["code"] == 386011:
            msg = f'{day_score_res.json()["msg"]}'
            self.log.append(msg)
            return msg
        elif day_score_res.json()["code"] == 100002:
            msg = f'{day_score_res.json()["msg"]}'
            self.log.append(msg)
            return msg

    def get_score_bang(self, ch):
        """
        超话打榜
        :param ch_dict: 超话信息字典,具体格式请看get_ch_list函数中
        :return:
        """
        if ch:
            ch_dict = ch[0]
            referer_url = f"https://huati.weibo.cn/aj/super/getscore?page_id={ch_dict['id']}&aid=&from={re.findall('WEIBOCN_FROM=(.*?);', self.headers['cookie'])[0]}"
            get_score_headers = {
                "Referer": referer_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
                "cookie": self.headers.get("cookie"),
                "X-Requested-With": "XMLHttpRequest"
            }
            score_res = requests.get(referer_url, headers=get_score_headers)
            topic_name = score_res.json()["data"]["topic_name"]
            score = score_res.json()["data"]["score"]
            rank = score_res.json()["data"]["rank"]
            # print(score_res.json())
            if score_res.json()["data"]["user_total_score"] > 100:
                while True:
                    time.sleep(self.seconds)
                    pick_data = {
                        "topic_name": ch_dict["title"],
                        "page_id": ch_dict["id"],
                        "score": score_res.json()["data"]["user_total_score"],
                        "is_pub": "0",
                        "cur_rank": score_res.json()["data"]["rank"],
                        "ctg_id": score_res.json()["data"]["ctg_id"],
                        "topic_score": score_res.json()["data"]["score"],
                        "index": "select256",
                        "user_score": score_res.json()["data"]["user_total_score"],
                        "aid": "",
                        "device": '{"timezone":"Asia/Shanghai","lang":"zh","plat":"Win32",'
                                  '"ua":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                  ' Chrome/84.0.4147.105 Safari/537.36","screen":"864*1536","aid":"","from":"1110006030"}',
                        "param": score_res.json()["data"]["encryption_param"]
                    }
                    pick_res = requests.post(self.pick_url, headers=get_score_headers, data=pick_data)
                    if pick_res.json()["code"] == 402001:
                        continue
                    elif pick_res.json()["code"] == 302001:
                        print(pick_res.json()["msg"])
                        return pick_res.json()["msg"]
                    else:
                        msg = f"TopicName：{topic_name}\nRank：{rank}/{score}分\nMsg：{pick_res.json()['data']['add_int_msg']}"
                        self.log.append(msg)
                        # print(msg)
                        return msg
            else:
                msg = f'TopicName：{topic_name}\nRank：{rank}/{score}分\n' \
                      f'Message：积分少于100，暂不打榜（太少不加经验）'
                self.log.append(msg)
                # print(msg)
                return msg
        else:
            msg = "未关注该超话，请确认并重新设置打榜超话名"
            print(msg)
            self.log.append(msg)

    def task_center(self):
        task_headers = {
            "Referer": "https://huati.weibo.cn/super/taskcenter?aid=&from=1110006030",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
            "cookie": self.headers.get("cookie"),
            "X-Requested-With": "XMLHttpRequest"
        }
        task_res = requests.get(self.task_center_url, headers=task_headers)
        if task_res.json()["code"] == 100000:
            task_dict = {
                "total_score": task_res.json()["data"]["total_score"],
                "day_score": task_res.json()["data"]["task_per_day"]["request"],
                "be_comment": task_res.json()["data"]["task_per_day"]["be_comment"],
                "lclient_day": task_res.json()["data"]["task_per_day"]["lclient_day"],
                "topic_check": task_res.json()["data"]["task_per_day"]["checkin"],
                "simple_comment": task_res.json()["data"]["task_per_day"]["simple_comment"],
                "simple_repost": task_res.json()["data"]["task_per_day"]["simple_repost"]
            }
            msg = f"""当前积分：{task_dict["total_score"]}分
每日积分：已获取{task_dict["day_score"]}分/{task_res.json()["data"]["request_desc"]}
超话签到：已签到{task_dict["topic_check"]}次/每日上限8次
超话帖子评论：已获取{task_dict["simple_comment"]}分/每日上限12分
超话帖子转发：已获取{task_dict["simple_repost"]}分/每日上限4分
"""
            self.log.append(msg)
            # print(msg)
            return task_dict

    def yu_yan(self, yu):
        if yu:
            story_list = self.get_story_list(yu[0])
            contents = "喻言@THE9-喻言"
            report_count = 0
            comment_count = 0
            start_count = 0
            for story in story_list:
                time.sleep(8)
                if story["user"] != "喻言官方反黑站":
                    st = self.get_st()
                    if self.comment_story(story["mid"], st, contents):
                        comment_count += 1
                    if self.report_story(story["mid"], st, contents):
                        report_count += 1
                    if self.star_story(story["mid"], st):
                        start_count += 1
            msg = f"转发成功：{report_count}条、评论成功：{comment_count}条、点赞成功：{start_count}条"
            # print(msg)
            self.log.append(msg)
        else:
            msg = f"未关注喻言，暂不评论转发点赞，因各超话评论风格不一，所以只写了喻言的，" \
                  f"如果需要请自定义，如果仅是想获取积分则关注喻言超话即可"
            # print(msg)
            self.log.append(msg)

    def get_st(self):
        """
        获取st参数,用于转发评论与点赞
        :return: st
        """
        st_response = requests.get(self.config_url, headers=self.headers)
        if st_response.json()["ok"] == 1:
            if str(st_response.json()["data"]["login"]) == "True":
                st = st_response.json()["data"]["st"]
                return st
            else:
                return ""
        else:
            return ""

    def report_story(self, mid, st, content):
        """
         转发微博
        :param mid: 微博mid
        :param st: get_st()获取
        :param content: 评论内容
        :return:
        """
        report_data = {
            "id": mid,
            "content": content,
            "mid": mid,
            "st": st,
            "_spr": "screen:411x731"
        }
        report_headers = {
            "referer": f"https://m.weibo.cn/compose/repost?id={mid}"
        }
        report_headers.update(self.headers)
        report_res = requests.post(self.report_story_url, headers=report_headers, data=report_data)
        if report_res.json()["ok"] == 1:
            # msg = f"转发微博MID：{mid} {report_res.json()['data']['created_at']} " \
            #       f"{content} 转发成功 转发后微博MID: {report_res.json()['data']['id']}"
            # print(msg)
            return True
        else:
            msg = f"{mid} {report_res.json()['msg']}/转发失败"
            return False

    def comment_story(self, mid, st, content):
        """
        评论微博
        :param mid: 微博mid
        :param st: get_st()获取
        :param content: 转发描述
        :return:
        """
        comment_data = {
            "content": content,
            "mid": mid,
            "st": st,
            "_spr": "screen:411x731"
        }
        comment_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        comment_headers.update(self.headers)
        comment_res = requests.post(self.comment_story_url, headers=comment_headers, data=comment_data)
        if comment_res.json()["ok"] == 1:
            # msg = f"评论微博MID：{mid} {comment_res.json()['data']['created_at']} {content} 评论成功"
            # print(msg)
            return True
        else:
            msg = f"{comment_res.json()['msg']}评论失败"
            return False

    def star_story(self, mid, st):
        """
        点赞微博
        :param mid: 微博mid
        :param st: get_st()获取
        :return:
        """
        star_data = {
            "id": mid,
            "attitudes": "heart",
            "st": st,
            "_spr": "screen:411x731"
        }
        star_headers = {
            "referer": f"https://m.weibo.cn/detail/{mid}"
        }
        star_headers.update(self.headers)
        star_response = requests.post(url=self.star_story_url, headers=star_headers, data=star_data)
        if star_response.json()["ok"] == 1:
            # msg = f"点赞微博MID：{mid} {star_response.json()['data']['created_at']} 点赞成功"
            msg = f"{mid} 点赞成功"
            print(msg)
            return True
        else:
            msg = "点赞失败"
            print(msg)
            return False

    def server_push(self, sckey):
        """
        Sever酱推送
        :param sckey: 微信推送key，通过 https://sc.ftqq.com/3.version 获取
        :return:
        """
        now_time = datetime.datetime.now()
        bj_time = now_time + datetime.timedelta(hours=8)
        test_day = datetime.datetime.strptime('2020-12-19 00:00:00', '%Y-%m-%d %H:%M:%S')
        date = (test_day - bj_time).days
        text = f"微博超话打卡---{bj_time.strftime('%H:%M:%S')}"
        desp = f"""
------
#### 🚁Now：
```
{bj_time.strftime("%Y-%m-%d %H:%M:%S %p")}
```
{self.get_log()}

#### 🚀Deadline:
```
考研倒计时--{date}天
```

>
> [GitHub项目地址](https://github.com/ReaJason/WeiBo_SuperTopics) 
>
>期待你给项目的star✨
"""
        server_push_headers = {
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        send_url = f"https://sc.ftqq.com/{sckey}.send"
        params = {
            "text": text,
            "desp": desp
        }
        response = requests.post(send_url, data=params, headers=server_push_headers)
        return response.json()["errmsg"]

    def get_log(self):
        """
        获取日志信息
        :return: log_str
        """
        return "\n".join(self.log)

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


def test():
    cookie = "******"
    s = "******"
    pick = "喻言"
    sckey = "*******"
    check = WeiBo()
    check.daily_task(cookie=cookie, s=s, sckey=sckey, pick_name=pick)


if __name__ == '__main__':
    # test()
    cookie = input()
    s = input()
    pick = input()
    sckey = input()
    check = WeiBo()
    check.daily_task(cookie=cookie, s=s, pick_name=pick, sckey=sckey)
