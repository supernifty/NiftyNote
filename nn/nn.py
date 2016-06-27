#!/usr/bin/env py
# -*- coding: utf-8 -*-
'''
    nifty note
'''


__VERSION__ = '1.0'
__APPNAME__ = 'NiftyNote'

TERMINATOR = '== terminator =='
DEFAULT_NOTE = 'Put your note content here'

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

def write_log(msg, fh, verbose=False):
    if verbose:
        fh.write('{0}\n'.format(msg))

def open_data_source(log, verbose):
    write_log('reading notes...', log, verbose)
    appdir = os.path.expanduser(os.path.join("~", "." + __APPNAME__))
    appfile = os.path.join(appdir, 'notes.txt')
    if os.path.exists(appfile):
        write_log('reading notes: file found', log, verbose)
        return open(appfile, 'r')
    else:
        write_log('reading notes: no notes found', log, verbose)
        return []

def open_data_target(log, verbose):
    appdir = os.path.expanduser(os.path.join("~", "." + __APPNAME__))
    appfile = os.path.join(appdir, 'notes.new')
    if not os.path.exists(appdir):
        os.makedirs(appdir)
    return open(appfile, 'w')

def move_data_target(log, verbose):
    write_log('save new notes...', log, verbose)
    appdir = os.path.expanduser(os.path.join("~", "." + __APPNAME__))
    appfile = os.path.join(appdir, 'notes.txt')
    newfile = os.path.join(appdir, 'notes.new')
    oldfile = os.path.join(appdir, 'notes.old')
    if os.path.exists(appfile):
        shutil.move(appfile, oldfile)
    shutil.move(newfile, appfile)
    write_log('save new notes: done', log, verbose)

def edit(args, out, log):
    '''
        add or edit
    '''
    write_log('edit: starting...', log, args.verbose)
    src = open_data_source(log, args.verbose)
    target = open_data_target(log, args.verbose)
    found = False
    in_found = False
    first = True
    new_entry = ''
    for line in src:
        if in_found:
            if line.strip('\n') == TERMINATOR:
                in_found = False
                first = True
            else:
                new_entry += line
        else:
            if first and line.strip('\n') == args.title:
                write_log('edit: note "{0}" exists'.format(args.title), log, args.verbose)
                new_entry = line
                found = True
                in_found = True
                first = False
            else:
                target.write(line)
                if line.strip('\n') == TERMINATOR:
                    first = True

    if not found:
        new_entry = '{0}\n{1}\n'.format(args.title, DEFAULT_NOTE)

    # make changes or add new
    write_log('edit: opening entry for editing...', log, args.verbose)
    editor = os.environ.get('EDITOR','vim')
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".tmp") as tf:
        tf.write(new_entry)
        tf.flush()
        subprocess.call([editor, tf.name])
        with open(tf.name) as tfr:
            found = False
            for line in tfr:
                found = True
                target.write(line)
            if found:
                target.write('{0}\n'.format(TERMINATOR))

    target.close()
    move_data_target(log, args.verbose)
    write_log('edit: done', log, args.verbose)

def show_list(args, out, log):
    write_log('list: starting...', log, args.verbose)
    src = open_data_source(log, args.verbose)
    first = True
    count = 0
    for line in src:
        if first:
            first = False
            if not args.pattern or re.search(args.pattern, line.strip('\n'), re.I) is not None:
                out.write(line)
                count += 1
        elif line.strip('\n') == TERMINATOR:
            first = True
    write_log('list: done. Found {0}'.format(count), log, args.verbose)

def rm(args, out, log):
    write_log('rm: starting...', log, args.verbose)
    src = open_data_source(log, args.verbose)
    target = open_data_target(log, args.verbose)
    first = True
    in_remove = False
    count = 0
    pattern = '^{0}$'.format(args.pattern) # force full match
    for line in src:
        if first:
            first = False
            if re.search(pattern, line.strip('\n'), re.I) is not None:
                count += 1
                write_log('rm: removing {0}: matches {1}'.format(line.strip('\n'), pattern), log, args.verbose)
                in_remove = True
            else:
                write_log('rm: keeping {0}: did not match {1}'.format(line.strip('\n'), pattern), log, args.verbose)
                target.write(line)
        else:
            if in_remove:
                if line.strip('\n') == TERMINATOR:
                    in_remove = False
            else:
                target.write(line)
            if line.strip('\n') == TERMINATOR:
                first = True
    
    target.close()
    move_data_target(log, args.verbose)
    write_log('rm: done removing {0} notes'.format(count), log, args.verbose)

def find(args, out, log):
    write_log('find: starting...', log, args.verbose)
    src = open_data_source(log, args.verbose)
    first = True
    title = None
    is_match = False
    count = 0
    for line in src:
        if first:
            first = False
            title = line
            if re.search(args.pattern, line.strip('\n'), re.I) is not None:
                is_match = True
                out.write(line)
                count += 1
        else:
            if re.search(args.pattern, line.strip('\n'), re.I) is not None:
                if not is_match:
                    out.write(title)
                    is_match = True
                    count += 1
                out.write('> {0}'.format(line))

        if line.strip('\n') == TERMINATOR:
            first = True
            is_match = False
    write_log('find: done. Found {0}'.format(count), log, args.verbose)

def view(args, out, log):
    write_log('view: starting...', log, args.verbose)
    src = open_data_source(log, args.verbose)
    first = True
    title = None
    is_match = False
    count = 0
    for line in src:
        if first:
            first = False
            title = line
            if re.search(args.pattern, line.strip('\n'), re.I) is not None:
                is_match = True
                out.write(line)
                count += 1
        else:
            if line.strip('\n') == TERMINATOR:
                first = True
                is_match = False
            if is_match:
                out.write('  {0}'.format(line))

    write_log('view: done. Found {0}'.format(count), log, args.verbose)

def main():
    parser = argparse.ArgumentParser(description='Manage a set of notes')
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(__VERSION__))
    parser.add_argument('--verbose', action='store_true', default=False, help='log progress to stderr')

    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    edit_sub = subparsers.add_parser('edit', help='edit note')
    edit_sub.add_argument('title', help='add or edit note matching title')
    edit_sub.set_defaults(func=edit)

    list_sub = subparsers.add_parser('list', help='list of notes')
    list_sub.add_argument('pattern', nargs='?', default=None, help='list notes with titles matching this regular expression')
    list_sub.set_defaults(func=show_list)

    rm_sub = subparsers.add_parser('rm', help='remove note')
    rm_sub.add_argument('pattern', help='remove notes with titles matching this regular expression')
    rm_sub.set_defaults(func=rm)

    find_sub = subparsers.add_parser('find', help='find notes matching expression')
    find_sub.add_argument('pattern', help='search term')
    find_sub.set_defaults(func=find)

    view_sub = subparsers.add_parser('view', help='view note')
    view_sub.add_argument('pattern', help='view notes matching expression')
    view_sub.set_defaults(func=view)

    args = parser.parse_args()
    args.func(args, out=sys.stdout, log=sys.stderr)

if __name__ == '__main__':
    main()
