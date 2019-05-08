#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author = 'orleven'

import re
import os
import json
import time
from urlparse import urlparse
from database import Database
from database import Mode
from burp import IBurpExtender
from burp import IExtensionStateListener
from burp import IContextMenuFactory
from javax.swing import JMenuItem
from javax.swing import JMenu

class BurpExtender(IBurpExtender, IExtensionStateListener, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):

        # Set extension's name
        callbacks.setExtensionName('Burp Collector')

        self._callbacks = callbacks

        # retrieve the context menu factories
        '''
        Burp 的作者在设计上下文菜单功能中采用了工厂模式的设计模式，扩展可以实现此接口，
        然后调用 IBurpExtenderCallbacks.registerContextMenuFactory() 注册自定义上下文菜单项的工厂。
       '''
        callbacks.registerContextMenuFactory(self)

        # register ourselves as an Extension listener
        '''
        扩展可以实现此接口，然后调用 IBurpExtenderCallbacks.registerExtensionStateListener() 注册一个扩展的状态监听器。
        在扩展的状态发生改变时，监听器将会收到通知。
        注意：任何启动后台线程或打开系统资源（如文件或数据库连接）的扩展插件都应该注册一个监听器，并在被卸载后终止线程/关闭资源。
       '''
        callbacks.registerExtensionStateListener(self)

    #
    # implement IContextMenuFactory
    #

    def createMenuItems(self, invocation):
        self.mymessage = invocation.getSelectedMessages()


        mainMenu = JMenu('BurpCollect')

        subMenu = JMenuItem('History To Sqlite',
                             actionPerformed=self.history_to_sqlite_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Param',
                            actionPerformed=self.export_param_desc_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Current Host Param Desc ',
                            actionPerformed=self.export_current_host_param_desc_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Current *.Domain Param Desc ',
                            actionPerformed=self.export_current_domain_param_desc_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Path',
                            actionPerformed=self.export_path_desc)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Current Host Path Desc',
                            actionPerformed=self.export_current_host_path_desc_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Current *.Domain Path Desc ',
                            actionPerformed=self.export_current_domain_path_desc_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Dir',
                            actionPerformed=self.export_dir_desc_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Current Host Dir Desc',
                            actionPerformed=self.export_current_host_dir_desc_on_click)
        mainMenu.add(subMenu)

        subMenu = JMenuItem('Export Current *.Domain Dir Desc ',
                            actionPerformed=self.export_current_domain_dir_desc_on_click)
        mainMenu.add(subMenu)


        return [mainMenu]

    def extensionUnloaded(self):
        de = DataExtractor(self._callbacks)
        de.core_processor()
        Database('burpcollect.db').core_processor(de.dirlist, de.pathlist, de.paramlist)


    def history_to_sqlite_on_click(self, event):
        de = DataExtractor(self._callbacks)
        de.core_processor()
        Database('burpcollect.db').core_processor(de.dirlist, de.pathlist, de.paramlist)

    def export_param_desc_on_click(self, event):
        mode = Mode.SELECT_ALL_PARAM
        rs, mytype = Database('burpcollect.db').select_processor(mode)
        self.print_data(rs, mytype)

    def export_current_host_param_desc_on_click(self, event):
        de = DataExtractor(self._callbacks,self.mymessage)
        mode = Mode.SELECT_CURRENT_HOST_PARAM
        host = de.get_current_host()
        rs, mytype = Database('burpcollect.db').select_processor(mode,host)
        self.print_data(rs, mytype,host)

    def export_current_domain_param_desc_on_click(self, event):
        de = DataExtractor(self._callbacks,self.mymessage)
        mode = Mode.SELECT_CURRENT_DOMAIN_PARAM
        host = de.get_current_host()
        host = self.get_domain(host)
        rs, mytype = Database('burpcollect.db').select_processor(mode,host)
        self.print_data(rs, mytype,host)

    def export_path_desc(self, event):
        mode = Mode.SELECT_ALL_PATH
        rs, mytype = Database('burpcollect.db').select_processor(mode)
        self.print_data(rs, mytype)

    def export_current_host_path_desc_on_click(self, event):
        de = DataExtractor(self._callbacks,self.mymessage)
        mode = Mode.SELECT_CURRENT_HOST_PATH
        host = de.get_current_host()
        rs, mytype = Database('burpcollect.db').select_processor(mode,host)
        self.print_data(rs, mytype,host)

    def export_current_domain_path_desc_on_click(self, event):
        de = DataExtractor(self._callbacks,self.mymessage)
        mode = Mode.SELECT_CURRENT_DOMAIN_PATH
        host = de.get_current_host()
        host = self.get_domain(host)
        rs, mytype = Database('burpcollect.db').select_processor(mode,host)
        self.print_data(rs, mytype,host)

    def export_dir_desc_on_click(self, event):
        mode = Mode.SELECT_ALL_DIR
        rs, mytype = Database('burpcollect.db').select_processor(mode)
        self.print_data(rs, mytype)

    def export_current_host_dir_desc_on_click(self, event):
        de = DataExtractor(self._callbacks,self.mymessage)
        mode = Mode.SELECT_CURRENT_HOST_DIR
        host = de.get_current_host()
        rs, mytype = Database('burpcollect.db').select_processor(mode,host)
        self.print_data(rs, mytype,host)

    def export_current_domain_dir_desc_on_click(self, event):
        de = DataExtractor(self._callbacks,self.mymessage)
        mode = Mode.SELECT_CURRENT_DOMAIN_DIR
        host = de.get_current_host()
        host = self.get_domain(host)
        rs,mytype = Database('burpcollect.db').select_processor(mode,host)
        self.print_data(rs, mytype,host)

    def print_data(self,rslist, mytype, host = ''):
        host = host if host == '' else host + '-'
        currentTime = time.strftime('%Y%m%d%H%M%S', time.localtime())
        tempfile = '{host}{mytype}-{time}.txt'.format(host = host,mytype = mytype,time = currentTime)
        print("Save data to " + tempfile)
        with open (tempfile,'w+') as f:
            for rs in rslist:
                # print(rs)
                f.write(rs + '\r\n')

    def get_domain(self,domain):
        suffix = {'.com', '.la', '.io', '.co', '.cn', '.info', '.net', '.org', '.me', '.mobi', '.us', '.biz', '.xxx',
                  '.ca', '.co.jp', '.com.cn', '.net.cn', '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
                  '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br', '.name', '.live', '.news', '.bz',
                  '.tech', '.pub', '.wang', '.space', '.top', '.xin', '.social', '.date', '.site', '.red', '.studio',
                  '.link', '.online', '.help', '.kr', '.club', '.com.bz', '.net.bz', '.cc', '.band', '.market',
                  '.com.co', '.net.co', '.nom.co', '.lawyer', '.de', '.es', '.com.es', '.nom.es', '.org.es', '.eu',
                  '.wiki', '.design', '.software', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
                  '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms', '.com.mx', '.nl', '.nu', '.co.nz',
                  '.net.nz', '.org.nz', '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw', '.hk', '.co.uk',
                  '.me.uk', '.org.uk', '.vg'}

        domain = domain.lower()
        names = domain.split(".")
        if len(names) >= 3:
            if ("." + ".".join(names[-2:])) in suffix:
                return ".".join(names[-3:])
            elif ("." + names[-1]) in suffix:
                return ".".join(names[-2:])
        else:
            return domain


class DataExtractor():
    def __init__(self, callbacks,messages = None):

        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.pathlist = []
        self.dirlist = []
        self.paramlist = []
        self.messages = messages

    def get_current_host(self):
        http_service = self.messages[0].getHttpService()
        host = http_service.getHost()
        return host

    def core_processor(self):

        with open(os.path.join(os.path.dirname(os.path.abspath('__file__')),'config.ini'))as config_f:
            self._config = json.load(config_f)

        all_history_message = self._callbacks.getSiteMap(None)

        # processing each message
        for history_message in all_history_message:

            http_service = history_message.getHttpService()
            request_info = self._helpers.analyzeRequest(http_service, history_message.getRequest())
            host = http_service.getHost()
            try:
                url = str(request_info.getUrl())
            except:
                continue
            path = urlparse(url).path
            dir, path = self.format_pathe(path)

            # invoke host filter
            if not self.filter_host(host):
                continue

            # invoke path filter
            if not self.filter_path(path):
                continue

            # invoke dir filter
            if not self.filter_dir(dir):
                continue

            try:
                current_path = '{}\t{}'.format(host, path)
            except:
                continue

            if path and current_path not in self.pathlist:
                # print(current_path)
                self.pathlist.append(current_path)

            try:
                current_dir = '{}\t{}'.format(host, dir)
            except:
                continue
            if dir and current_dir not in self.dirlist:
                # print(current_dir)
                self.dirlist.append(current_dir)

            # parameters to log
            params_object = request_info.getParameters()
            params = self.process_params_object(params_object)
            for param in params:
                try:
                    current_param = '{}\t{}'.format(host, param)
                except:
                    continue
                if current_param not in self.paramlist:
                    # print(current_param)
                    self.paramlist.append(current_param)

    # format path and file
    def format_pathe(self, path):

        sepIndex = path.rfind('/')

        # EX: http://xxx/?id=1
        if path == '/':
            file = ''
            path = ''

        # EX: http://xxx/index.php
        # file = index.php
        elif sepIndex == 0:
            file = path[1:]
            path = ''

        # EX: http://xxx/x/index.php
        # path = /x/
        # file = index.php
        else:
            file = path[sepIndex + 1:]
            path = path[:sepIndex + 1]

        return path, file

    def filter_host(self, host):
        black_hosts = self._config.get('blackHosts')
        for black_host in black_hosts:
            if host.endswith(black_host):
                return False
        return True

    def filter_dir(self,dir):
        if 'https://' in dir.lower() or 'http://' in dir.lower():
            return False
        return True

    def filter_path(self, path):

        balck_paths = self._config.get('blackExtension')
        pattern = re.compile(r'^\d+$')

        if '=' in path or ',' in path:
            return False
        elif pattern.match(path):
            return False

        for balck_path in balck_paths:
            if path.endswith(balck_path):
                return False

        return True

    def process_params_object(self, params_object):

        # get parameters
        params = []
        for param_object in params_object:

            # don't process Cookie's Pamrams
            if param_object.getType() == 2:
                continue
            param = param_object.getName()
            if param.strip()  == '' or param.startswith('_'):
                continue

            params.append(param)
        return params