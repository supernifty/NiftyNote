#!/usr/bin/env python

import hashlib
import shutil
import os

import config

def _get_target(username):
    '''
      returns file
    '''
    appdir = os.path.expanduser(config.ROOT)
    if not os.path.exists(appdir):
        os.makedirs(appdir)
    if username is None:
        filename = config.DEFAULT_USER
    else:
        filename = hashlib.sha256(username.encode('utf-8')).hexdigest()

    return os.path.join(appdir, filename)


def open_data_source(username):
    appfile = '{}.txt'.format(_get_target(username))
    if os.path.exists(appfile):
        return open(appfile, 'r')
    else:
        return []

def open_data_target(username):
    appfile = '{}.new'.format(_get_target(username))
    return open(appfile, 'w')

def move_data_target(username):
    appdir = os.path.expanduser(os.path.join("~", "." + config.APPNAME))
    prefix = _get_target(username)
    appfile = '{}.txt'.format(prefix)
    newfile = '{}.new'.format(prefix)
    oldfile = '{}.old'.format(prefix)
    if os.path.exists(appfile):
        shutil.move(appfile, oldfile)
    shutil.move(newfile, appfile)
