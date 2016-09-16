#!/usr/bin/python
#coding: utf-8
CounterDict = {}


class Counter(object):
    '''
    得到长度为N的一个计数器, 一次全局自增1    
    '''
    def __init__(self, n):
        self.max_num = n
        self.cnt = 0


    def count(self):
        self.cnt += 1
        if len(str(self.cnt)) > self.max_num:
            self.cnt = 0
        return self


    def __str__(self):
        return "%s" % (str(self.cnt).zfill(self.max_num))



def get_counter(key):
    if not CounterDict.has_key(key):
        raise Exception("Counter key %s doesn't exist." % key)
    return CounterDict[key]


def create_counter(key, n):
    if CounterDict.has_key(key):
        raise Exception("counter key %s has already existed." % key)
    CounterDict[key] = Counter(n)
    return CounterDict[key]
