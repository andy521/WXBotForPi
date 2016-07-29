#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import multiprocessing
import time
import re
import os
import pickle
from urlparse import urlparse
from wxBot.wxbot import *

import sys

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

    def dump_keys(self):
        d = {
            "uuid" : self.uuid,
            "redirect_uri" : self.redirect_uri,
            "base_uri" : self.base_uri,
            "skey" : self.skey,
            "sid" : self.sid,
            "uin" : self.uin,
            "pass_ticket" : self.pass_ticket,
            "device_id" : self.device_id,
            "base_request" : self.base_request,
            # "sync_key" : self.sync_key,
            # "sync_key_str" : self.sync_key_str,
            # "my_account" : self.my_account,
            "session" : self.session,
        }
        with open('dump.pickle', 'wb') as f:
            pickle.dump(d, f)

    def load_keys(self):
        if not os.path.exists('dump.pickle'):
            return False

        if time.time() - os.stat('dump.pickle').st_mtime < 600:
            with open('dump.pickle', 'rb') as f:
                d = pickle.load(f)
                self.uuid = d["uuid"]
                self.redirect_uri = d["redirect_uri"]
                self.base_uri = d["base_uri"]
                self.skey = d["skey"]
                self.sid = d["sid"]
                self.uin = d["uin"]
                self.pass_ticket = d["pass_ticket"]
                self.base_request = d["base_request"]
                # self.sync_key = d["sync_key"]
                # self.sync_key_str = d["sync_key_str"]
                # self.my_account = d["my_account"]
                self.session = d["session"]
                self.device_id = d["device_id"]
                print d
                return True
        return False

    # 更新self.sync_key和self.sync_key_str后写入文件
    def sync(self):
        print "[DEBUG]start syncing"
        dic = super(MyWXBot, self).sync()
        # self.dump_keys()    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        print "[DEBUG]finished syncing"
        return dic

    def myRun(self):

        if not self.load_keys():
            print "need new keys"
            
            self.get_uuid()
            self.gen_qr_code('qr.png')
            print '[INFO] Please use WeChat to scan the QR code .'

            result = self.wait4login()
            if result != SUCCESS:
                print '[ERROR] Web WeChat login failed. failed code=%s' % (result,)
                return

            if self.login():
                print "skey: " + self.skey
                print "sid: " + self.sid
                print "uin: " + self.uin
                print "pass_ticket: " + self.pass_ticket
                print '[INFO] Web WeChat login succeed .'
            else:
                print '[ERROR] Web WeChat login failed .'
                return


            
            self.dump_keys()
            print "get all keys, restart needed"
            return

            # self.dump_keys()
        else:
            print "loaded old keys"


        if self.init():
            print '[INFO] Web WeChat init succeed .'
        else:
            print '[INFO] Web WeChat init failed'
            return

        self.status_notify()
        self.get_contact()
        print '[INFO] Get %d contacts' % len(self.contact_list)
        print '[INFO] Start to process messages .'
        self.proc_msg()



        return




        self.get_uuid()                                         #self.uuid!!!
        self.gen_qr_code('qr.png')
        print '[INFO] Please use WeChat to scan the QR code .'

        result = self.wait4login()                             
        # window.code=200;
        # window.redirect_uri="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=A05EyS-DbkUHaF4P82XqXXvq@qrticket_0&uuid=gb5YInhL9Q==&lang=zh_CN&scan=1469770846";
        # 
        #self.redirect_uri!!! = redirect_uri    https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=A3tELgCrPZtsUJO_ZzzH5NG2@qrticket_0&uuid=4a5lWAvkXQ==&lang=zh_CN&scan=1469771097&fun=new
        #self.base_uri!!! = redirect_uri[:redirect_uri.rfind('/')]  https://wx2.qq.com/cgi-bin/mmwebwx-bin

        if result != SUCCESS:
            print '[ERROR] Web WeChat login failed. failed code=%s' % (result,)
            return

        if self.login():
            # <error>
            #     <ret>0</ret>
            #     <message>OK</message>
            #     <skey>@crypt_507a5261_db89646874932fbc98a15339bee371be</skey>
            #     <wxsid>lvjbN8rBXObQCGHH</wxsid>
            #     <wxuin>337808340</wxuin>
            #     <pass_ticket>QJpEPGYuoUsq6lJWnV9eoL1UtqGzyGALkGnfZWrVdqhM8TMTPVjB75fDlFpLYb8b</pass_ticket>
            #     <isgrayscale>1</isgrayscale>
            # </error>

            # if node.nodeName == 'skey':
            #     self.skey!! = node.childNodes[0].data
            # elif node.nodeName == 'wxsid':
            #     self.sid !!= node.childNodes[0].data
            # elif node.nodeName == 'wxuin':
            #     self.uin!! = node.childNodes[0].data
            # elif node.nodeName == 'pass_ticket':
            #     self.pass_ticket!! = node.childNodes[0].data

            # self.base_request = {
            #     'Uin': self.uin,
            #     'Sid': self.sid,
            #     'Skey': self.skey,
            #     'DeviceID': self.device_id,
            # }
            print "skey: " + self.skey
            print "sid: " + self.sid
            print "uin: " + self.uin
            print "pass_ticket: " + self.pass_ticket
            print '[INFO] Web WeChat login succeed .'
        else:
            print '[ERROR] Web WeChat login failed .'
            return





        if self.init():
            print '[INFO] Web WeChat init succeed .'
        else:
            print '[INFO] Web WeChat init failed'
            return
        self.status_notify()
        self.get_contact()
        print '[INFO] Get %d contacts' % len(self.contact_list)
        print '[INFO] Start to process messages .'
        self.proc_msg()


def main():
    bot = MyWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'tty'
    # bot.run()
    bot.myRun()


if __name__ == '__main__':
    # main()
    
    sys.setdefaultencoding("utf-8")
    # print u"你好吗".encode("utf-8")
    import locale
    locales = "Current locale: %s %s -- Default locale: %s %s" % (locale.getlocale() + locale.getdefaultlocale())
    print locales
    print (u"你好吗")
    time.sleep(5)
