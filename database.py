#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author = 'orleven'

import os
import json
import warnings
from java.lang import Class
from java.sql import DriverManager, SQLException

# warnings.filterwarnings("ignore")

class Database(object):
    filepath = None

    def __init__(self, database=None):
        self.database = self.filepath if database is None else database
        self.database = "jdbc:sqlite:%s" % (database)
        self.connection = None
        self.cursor = None

    def connect(self, who="storage"):
        Class.forName("org.sqlite.JDBC").newInstance()
        self.connection = DriverManager.getConnection(self.database)
        self.connection.setAutoCommit(True)


    def disconnect(self):

        if self.connection:
            self.connection.close()

    def commit(self):
        self.connection.commit()


    def init(self):
        sql = '''
                create table if not exists param(
                id INTEGER  not null primary key AUTOINCREMENT,
                host varchar(100),
                param varchar(300) not null);
            '''
        prestmt = self.connection.prepareStatement(sql)
        prestmt.executeUpdate()

        sql = '''
                create table if not exists dir(
                id INTEGER  not null primary key AUTOINCREMENT,
                host varchar(100),
                dir varchar(300) not null);
            '''
        prestmt = self.connection.prepareStatement(sql)
        prestmt.executeUpdate()

        sql = '''
                create table if not exists path(
                id INTEGER  not null primary key AUTOINCREMENT,
                host varchar(100),
                path varchar(300) not null);
            '''
        prestmt = self.connection.prepareStatement(sql)
        prestmt.executeUpdate()

    def select_param(self,host,param):
        sql = "SELECT * FROM param WHERE host = ? and param =?"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        prestmt.setString(2, param)
        return  prestmt.executeQuery()

    def select_current_host_param(self,host):
        sql = "select * from param where host = ? "
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        return  prestmt.executeQuery()

    def select_current_domain_param(self,host):
        sql = "select *,count(*) as new_count from param where host like '%' || ? GROUP BY param ORDER BY new_count DESC"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        return  prestmt.executeQuery()

    def select_all_param(self):
        sql = "select *,count(*) as new_count from param  GROUP BY param ORDER BY new_count DESC"
        prestmt = self.connection.prepareStatement(sql)
        return  prestmt.executeQuery()

    def select_dir(self,host,dir):
        sql = "SELECT * FROM dir WHERE host = ? and dir =?"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        prestmt.setString(2, dir)
        return prestmt.executeQuery()

    def select_current_host_dir(self,host):
        sql = "select * from dir where host = ? "
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        return  prestmt.executeQuery()

    def select_current_domain_dir(self,host):
        sql = "select *,count(*) as new_count from dir where host like '%' || ? GROUP BY dir ORDER BY new_count DESC"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        return  prestmt.executeQuery()

    def select_all_dir(self):
        sql = "select *,count(*) as new_count from dir  GROUP BY dir ORDER BY new_count DESC"
        prestmt = self.connection.prepareStatement(sql)
        return  prestmt.executeQuery()

    def select_path(self,host,path):
        sql = "SELECT * FROM path WHERE host = ? and path =?"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        prestmt.setString(2, path)
        return prestmt.executeQuery()

    def select_current_host_path(self,host):
        sql = "select * from path where host = ? "
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        return  prestmt.executeQuery()

    def select_current_domain_path(self,host):
        sql = "select *,count(*) as new_count from path where host like '%' || ? GROUP BY path ORDER BY new_count DESC"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        return  prestmt.executeQuery()

    def select_all_path(self):
        sql = "select *,count(*) as new_count from path  GROUP BY path ORDER BY new_count DESC"
        prestmt = self.connection.prepareStatement(sql)
        return  prestmt.executeQuery()

    def insert_param(self, host,param):
        sql = "INSERT  OR IGNORE INTO param (host,param) VALUES (?, ?)"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        prestmt.setString(2, param)
        prestmt.executeUpdate()

    def insert_path(self, host,path):
        sql = "INSERT  OR IGNORE INTO path (host,path) VALUES (?, ?)"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        prestmt.setString(2, path)
        prestmt.executeUpdate()
        # prestmt.addBatch()
        # prestmt.executeBatch()
        # self.execute("INSERT  OR IGNORE INTO path (host,path) VALUES (?, ?)",(host,path))

    def insert_dir(self, host,dir):
        sql = "INSERT  OR IGNORE INTO dir (host,dir) VALUES (?, ?)"
        prestmt = self.connection.prepareStatement(sql)
        prestmt.setString(1, host)
        prestmt.setString(2, dir)
        prestmt.executeUpdate()


    # def update_param_count(self, host, param):
    #     sql = "UPDATE param set  count = count + 1 WHERE host = ? and param = ?"
    #     prestmt = self.connection.prepareStatement(sql)
    #     prestmt.setString(1, host)
    #     prestmt.setString(2, param)
    #     prestmt.executeUpdate()
    #
    #
    # def update_path_count(self, host, path):
    #     sql = "UPDATE path set  count = count + 1 WHERE host = ? and path = ?"
    #     prestmt = self.connection.prepareStatement(sql)
    #     prestmt.setString(1, host)
    #     prestmt.setString(2, path)
    #     prestmt.executeUpdate()
    #
    #
    # def update_dir_count(self, host, dir):
    #     sql = "UPDATE dir set  count = count + 1 WHERE host = ? and dir = ?"
    #     prestmt = self.connection.prepareStatement(sql)
    #     prestmt.setString(1, host)
    #     prestmt.setString(2, dir)
    #     prestmt.executeUpdate()


    def core_processor(self,dirlist, pathlist, paramlist):
        try:
            self.connect()
            self.init()
            print ("Save history to sqlite...")
            for dir in dirlist:
                # print(dir)
                host, dir = dir.split('\t')
                if not self.select_dir(host, dir).next():
                    self.insert_dir(host, dir)
            for path in pathlist:
                # print(path)
                host, path = path.split('\t')
                if not self.select_path(host, path).next() :
                    self.insert_path(host, path)
            for param in paramlist:
                # print(param)
                host, param = param.split('\t')
                if not self.select_param(host, param).next():
                    self.insert_param(host, param)
        except Exception as e:
            print(type(e).__name__)
        finally:
            print ("Saved history to sqlite.")
            self.disconnect()

    def select_processor(self, mode, host = ''):
        rslist = []
        rs = value = None
        try:
            self.connect()
            self.init()
            if mode == Mode.SELECT_ALL_DIR:
                rs = self.select_all_dir()
                value = 'dir'
            elif mode == Mode.SELECT_CURRENT_DOMAIN_DIR:
                rs = self.select_current_domain_dir(host)
                value = 'dir'
            elif mode == Mode.SELECT_CURRENT_HOST_DIR:
                rs = self.select_current_host_dir(host)
                value = 'dir'
            elif mode == Mode.SELECT_ALL_PATH:
                rs = self.select_all_path()
                value = 'path'
            elif mode == Mode.SELECT_CURRENT_DOMAIN_PATH:
                rs = self.select_current_domain_path(host)
                value = 'path'
            elif mode == Mode.SELECT_CURRENT_HOST_PATH:
                rs = self.select_current_host_path(host)
                value = 'path'
            elif mode == Mode.SELECT_ALL_PARAM:
                rs = self.select_all_param()
                value = 'param'
            elif mode == Mode.SELECT_CURRENT_DOMAIN_PARAM:
                rs = self.select_current_domain_param(host)
                value = 'param'
            elif mode == Mode.SELECT_CURRENT_HOST_PARAM:
                rs = self.select_current_host_param(host)
                value = 'param'
            while (rs.next()):
                rslist.append(rs.getString(value))
        except Exception as e:
            print(type(e).__name__)
        finally:
            self.disconnect()
        return rslist,value

class Mode:
    SELECT_ALL_DIR = 1
    SELECT_CURRENT_DOMAIN_DIR = 2
    SELECT_CURRENT_HOST_DIR = 3
    SELECT_ALL_PATH = 4
    SELECT_CURRENT_DOMAIN_PATH = 5
    SELECT_CURRENT_HOST_PATH = 6
    SELECT_ALL_PARAM = 7
    SELECT_CURRENT_DOMAIN_PARAM = 8
    SELECT_CURRENT_HOST_PARAM = 9