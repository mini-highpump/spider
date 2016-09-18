#!/usr/bin/python
#coding: utf-8
import urllib2
import os
import shutil
import MySQLdb
import redis
import json
from datetime import datetime
from hashlib import md5
from counter import create_counter
from tool import get_sid


CHANNEL_URL = "https://api.douban.com/v2/fm/app_channels"
SONG_URL = "https://api.douban.com/v2/fm/playlist"


APP_NAME = "radio_android"
VERSION = 642


FILE_HASH_KEY = "file_hash"


def wrap_url(base_uri, **kwargs):
    if kwargs == {}:
        return base_uri
    r = ["=".join([str(key), str(value)]) for key,value in kwargs.iteritems()]
    return base_uri + "?" + "&".join(r)
    

def get(url, data = {}, type=1):
    '''
    @param type  1-json, 2-binary
    '''
    url = wrap_url(url, **data)
    # print url
    response = urllib2.urlopen(url)
    if type == 1:
        return json.loads(response.read())
    else:
        return response


class Spider(object):
    '''
    Douban FM spider.
    '''
    def __init__(self, basedir):
        if not basedir.endswith("/"):
            basedir += "/"
        self.basedir = basedir
        self.r = redis.Redis("localhost")
        self.db = MySQLdb.connect("localhost", "root", "a767813944", "highpump")
        self.db.set_character_set("utf8")
        create_counter("sid", 11)


    def __del__(self):
        self.db.close()

    
    def get_channel(self):
        data = {
                "app_name": APP_NAME, 
                "version": VERSION
            }
        channels = get(CHANNEL_URL, data)
        for group in channels["groups"]:
            for chls in group["chls"]:
                yield (chls["name"], chls["id"])


    def get_song(self, channel_id):
        while True:
            data = {
                    "app_name": APP_NAME, 
                    "version": VERSION, 
                    "channel": channel_id, 
                    "type": "n"
                }
            result = get(SONG_URL, data)
            if result["r"] != 0:
                raise Exception("Get song failed:%s" % result["err"])
            for song in result["song"]:
                yield song


    def download(self, url):
        response = get(url, type=2) # binary response
        tmpf = open("tmp.mp4", "wb")
        binary = response.read()
        tmpf.write(binary)
        fhash = md5(binary).hexdigest()
        # print "File Hash:%s" % fhash
        if not self.r.sismember(FILE_HASH_KEY, fhash):
            sid = get_sid(fhash)
            path = self.basedir + sid + ".mp4"
            shutil.copy("tmp.mp4", path)
            self.r.sadd(FILE_HASH_KEY, fhash)
            return sid
        return None


    def write_db(self, sid, name, artist, album, state, length):
        cursor = self.db.cursor()
        curtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into highpump.t_song_info (sid, name, artist, album, state, length, create_time, modify_time)  \
                values ('%s', '%s', '%s', '%s', %d, %d)" % (sid, name, artist, album, state, length, curtime, curtime)
        # print sql
        cursor.execute(sql)
        self.db.commit()


    def run(self):
        total = 0
        for name, channel_id in self.get_channel():
            sum = 0
            print "Preparing download %s channel songs." % name
            for s in self.get_song(channel_id):
                sid = self.download(s["url"])
                if sid is None:
                    continue
                self.write_db(sid, s["title"], s["artist"], s["albumtitle"], 0, s["length"])
                sum += 1
                total += 1
                print "    Complete %d songs of this channel. Total %d songs." % (sum, total)
                if sum > 300:
                    break


if __name__ == "__main__":
    spider = Spider("/data/song/")
    spider.run()
