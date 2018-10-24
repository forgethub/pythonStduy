#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import os.path
from datetime import date, timedelta, datetime
import re
from fnmatch import fnmatch
from xml.dom import minidom
import gzip

prefix = "/data/www/devel/wms/"
today = date.today()


class Log(object):

    def __init__(self, filename, keep_day=60, zip_day=10):
        self.filename = filename
        self.zip_day = timedelta(zip_day)
        self._time = timedelta(days=keep_day)

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time

    def process(self):
        mtime = os.path.getmtime(self.filename)
        last_modified_date = date.fromtimestamp(mtime)

        if (today - self._time < last_modified_date < today - self.zip_day and fnmatch(self.filename, '*.log')):
            print("compressing {0}".format(self.filename))
            self.compress()
        elif today - self._time >= last_modified_date:
            print("deleting {0}".format(self.filename))
            self.delete()
        else:
            print("the file name is {0}".format(self.filename))

    def delete(self):
        try:
            os.remove(self.filename)
        except PermissionError as e:
            print(e)

    def compress(self):
        gz_compress(self.filename)


def get_nodevalue(node, index=0):
    return node.childNodes[index].nodeValue if node else ''


def get_xmlnode(node, name):
    return node.getElementsByTagName(name) if node else []


def get_xml_data(filename='log.xml'):
    doc = minidom.parse(filename)
    root = doc.documentElement
    dir_nodes = get_xmlnode(root, 'dir')
    log_list = {}

    for dir_node in dir_nodes:
        scanner_nodes = get_xmlnode(dir_node, 'scanner_dir')
        scanner_dir = get_nodevalue(scanner_nodes[0])
        log_nodes = get_xmlnode(dir_node, 'log')
        log_sub_list= {}
        for node in log_nodes:
            node_name = get_xmlnode(node, 'name')
            node_limit = get_xmlnode(node, 'save_limit_time')
            node_zip_time = get_xmlnode(node, 'zip_limit_time')
            log_name = get_nodevalue(node_name[0])
            log_limit = get_nodevalue(node_limit[0])
            log_zip_time = get_nodevalue(node_zip_time[0])
            
            log_array ={}
            log_array = dict((('limit', int(log_limit)),  ('zip_time', int(log_zip_time))))
            log_sub_list[log_name.encode('utf-8')]=log_array
        log_list[scanner_dir] = log_sub_list
    return log_list

def gz_compress(filename, keep_original=False):

    with open(filename, 'rb') as f_in:
        with gzip.open(''.join([filename, '.gz']), 'wb') as f_out:
            f_out.writelines(f_in)

    if not keep_original:
        try:
            os.remove(filename)
        except PermissionError as e:
            print(e)


def gen_find(top, regex=''):
    pat = re.compile(regex)
    for path, dirlist, filelist in os.walk(top):
        for file in filter(pat.search, filelist):
            full_path = os.path.join(path, file)
            yield os.path.normpath(os.path.abspath(full_path))


def main():
    print("{0}:\tstarting log rotate ...".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    log_list = get_xml_data()
    for key, value in log_list.items():
        for file in gen_find(prefix + key, r'(log|gz|xz)$'):
            print file
            for key1,value1 in value.items():
                if fnmatch(file, '*/' + key1 + '/*'):
                    log = Log(file, keep_day=value1['limit'], zip_day=value1['zip_time'])
            log = Log(file)
                log.process()

    print("{0}:\tend log rotate ...".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

if __name__ == '__main__':
    main()
