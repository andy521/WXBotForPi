#!/usr/bin/env python
# coding: utf-8

import subprocess
import multiprocessing
import time
import re
from urlparse import urlparse
from wxBot.wxbot import *

class DownloadTask:

    WEBLIST = {'https://www.youtube.com', 'https://twitter.com', 'http://vk.com', 'https://vine.co', 'https://vimeo.com', 'http://vidto.me', 'http://videomega.tv', 'http://www.veoh.com', 'https://www.tumblr.com', 'http://www.ted.com', 'https://soundcloud.com', 'https://www.pinterest.com', 'http://en.musicplayon.com', 'http://www.mtv81.com', 'https://www.mixcloud.com', 'http://www.metacafe.com', 'http://www.magisto.com', 'https://www.khanacademy.org', 'http://www.jpopsuki.tv', 'https://archive.org', 'https://instagram.com', 'http://www.infoq.com/presentations', 'http://imgur.com', 'http://www.heavy-music.ru', 'https://plus.google.com', 'http://www.freesound.org', 'https://www.flickr.com', 'http://video.fc2.com', 'https://www.facebook.com', 'http://www.ehow.com', 'http://www.dailymotion.com', 'http://www.cbs.com', 'http://bandcamp.com', 'http://alive.in.th', 'http://7gogo.jp', 'http://www.nicovideo.jp', 'http://v.163.com', 'http://music.163.com', 'http://www.56.com', 'http://www.acfun.tv', 'http://tieba.baidu.com', 'http://www.baomihua.com', 'http://www.bilibili.com', 'http://www.dilidili.com', 'http://www.douban.com', 'http://www.douyutv.com', 'http://www.panda.tv', 'http://v.ifeng.com', 'http://www.fun.tv', 'http://www.iqiyi.com', 'http://www.joy.cn', 'http://www.ku6.com', 'http://www.kugou.com', 'http://www.kuwo.cn', 'http://www.le.com', 'http://www.lizhi.fm', 'http://www.miaopai.com', 'http://www.miomio.tv', 'https://www.pixnet.net', 'http://www.pptv.com', 'http://v.iqilu.com', 'http://v.qq.com', 'http://live.qq.com', 'http://qianmo.com', 'http://thvideo.tv', 'http://video.sina.com.cn', 'http://video.weibo.com', 'http://tv.sohu.com', 'http://www.dongting.com', 'http://www.tudou.com', 'http://www.xiami.com', 'http://www.isuntv.com', 'http://www.yinyuetai.com', 'http://www.youku.com', 'http://v.youku.com', 'http://www.cntv.cn', 'http://huaban.com', 'http://tvcast.naver.com', 'http://www.mgtv.com'}

    def __init__(self, user_id, url, format_option = "", callback = None):
        # pass
        self.user_id = user_id
        self.url = url
        self.format_option = format_option
        self.process = None
        self.callback = callback
        self.returncode = 0
        self.ret = ""

    def _runInBackground(self):
        print("runInBackground")

        # 判断域名是否在you-get支持范围中
        o = urlparse(self.url)
        domain = o.scheme + "://" + o.hostname
        if domain in self.WEBLIST:
            # 1. 是否指定了格式
            if self.format_option:
                # 2. 若指定格式，-i 返回的信息里匹配相应命令
                try:
                    ret = subprocess.check_output(["you-get", "-i", self.url])
                    match = re.search('you-get (--.*=' + self.format_option +') \[URL\]', ret)
                    if not match:
                        self.returncode = 1099
                        self.ret = "指定的格式不存在"
                        self.callback(self)
                        return
                except subprocess.CalledProcessError, e:
                    self.returncode = e.returncode
                    self.ret = e.output
                    self.callback(self)
                    return

                command = ["you-get", match.group(1), self.url]
            else:
                command = ["you-get", self.url]
            
        else:
            command = ["wget", self.url]
        # 3. 开始下载
        try:
            ret = subprocess.check_output(command, stderr=subprocess.STDOUT)
            self.callback(self)
            return
        except subprocess.CalledProcessError, e:
            self.returncode = e.returncode
            self.ret = e.output
            self.callback(self)
            return


    def start(self):
        self.process = multiprocessing.Process(target=self._runInBackground)
        self.process.start()


class MyWXBot(WXBot):

    # 检查哪种指令
    def _check_command(self, string):
        string = string.strip()

        # 1. 是否是链接加格式
        match = re.match('(http[s]?://[^\s<>]*)\s*(.*)', string)
        if match:
            return {
                "type": 1,
                "url": match.group(1),
                "format_option": match.group(2)
            }
        else:
            return {"type": 99}


    # 执行完后台任务时的回调方法
    def _callback(self, task):
        print("in callback.")
        # print "sleep 3s"
        # time.sleep(3)
        # print "finished"
        if task.returncode == 1099:
            self.send_msg_by_uid(task.ret, task.user_id)
        elif task.returncode:
            self.send_msg_by_uid(task.url + u"下载失败", task.user_id)
        else:
            self.send_msg_by_uid(task.url + u"下载成功啦亲！！！！！！！", task.user_id)

    # 消息处理方法
    def handle_msg_all(self, msg):
        print(msg)
        # 收到文字信息
        if msg['msg_type_id'] == 4 and msg['content']['type'] == 0:
            # print("check command type")
            command = self._check_command(msg["content"]["data"])
            if command["type"] == 1:
                # print("this is a download command")
                self.send_msg_by_uid(u'发现下载任务', msg['user']['id'])
                # 添加下载任务
                task = DownloadTask(msg['user']['id'], command["url"], command["format_option"], self._callback)
                task.start()
            else:
                self.send_msg_by_uid(u'不知道你在说什么，呵呵哒', msg['user']['id'])
            # print("after check.long sleep")

    # def schedule(self):
    #     # self.send_msg(u'void', u'测试')
    #     print("this is schedule. sleep 3s")
    #     time.sleep(3)
    #     print("after sleep")


def main():
    bot = MyWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'tty'
    bot.run()


if __name__ == '__main__':
    main()
