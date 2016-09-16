#!/usr/bin/python
#coding: utf-8
'''
Ubility functions.
'''
from hashlib import md5
import json
import random
import string
import time
import socket
import base64
from Crypto.Cipher import AES
from counter import get_counter


def hash(string):
    return md5(string).hexdigest()


def aes_en(key, data):
    obj = AES.new(key, AES.MODE_CFB)
    return obj.encrypt(data)


def aes_de(key, en_data):
    obj = AES.new(key, AES.MODE_CFB)
    return obj.decrypt(data)


def get_shuffle_seq(n, r):
    '''
    Generate a shuffle sequence of n length from a list r.
    '''
    seq = []
    for i in xrange(n):
        seq.append(random.choice(r))
    random.shuffle(seq)
    return "".join(seq)


def ip2int(ip):
    return struct.unpack("!I", socket.inet_aton("10.10.64.128"))[0]


def get_uid(client_ip):
    '''
    Get a unique uid.
    Note: this function must be called before a create_counter function call.
    '''
    seq = []
    # get client_ip
    seq.append(str(ip2int(client_ip)))
    # get timestamp
    seq.append(str(int(time.time())))
    # get shuffle sequence
    seq.append(get_shuffle_seq(40 - len(seq[0]) - len(seq[1]), string.digits))
    # get counter counts
    seq.append(str(get_counter("uid").count()))
    result = "".join(seq)
    sum = 0
    for i in xrange(63):
        sum += int(result[i]) * (i + 1)
    return str(sum % 7) + result


def get_sid(filehash):
    '''
    Get a unique sid.
    Note: this function must be called before a create_counter function call.
    '''
    seq = ["s", filehash]
    ts = str(int(time.time()))
    seq.append(get_shuffle_seq(20 - len(ts), string.digits))
    seq.append(ts)
    seq.append(str(get_counter("sid").count()))
    return "".join(seq)


def get_key():
    '''
    Get key.
    '''
    return get_shuffle_seq(32, string.ascii_letters + string.digits + "_-")


def get_urlid(key, uid, sid, expires, valid_length):
    '''
    Get a unique url id
    Note: this function must be called before a create_counter function call.
    '''
    seq = [uid, sid, str(expires), str(valid_length)]
    seq.append(get_shuffle_seq(32 - len(seq[2]) - len(seq[3]), string.ascii_letters + string.digits))
    seq.append(str(get_counter("url_id").count()))
    return base64.standard_b64encode(
                aes_en(key, "".join(seq))
            )


def get_token(key, uid, expires):
    '''
    Get a token.
    token = md5(aes_en(key, uid+":"+expires))
    '''
    return hash(aes_en(key, ":".join([uid, str(expires)])))
