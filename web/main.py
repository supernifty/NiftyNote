# -*- coding: utf-8 -*-
'''
    main web interface
'''
import os
import re
import shutil

import flask

__APPNAME__ = 'NiftyNote'
TERMINATOR = '== terminator =='
DEFAULT_NOTE = 'Put your note content here'

app = flask.Flask(__name__, template_folder='templates')
app.config.from_pyfile('config.py')
app.secret_key = 'ducks in space'

def open_data_source():
    #write_log('reading notes...', log, verbose)
    appdir = os.path.expanduser(os.path.join("~", "." + __APPNAME__))
    appfile = os.path.join(appdir, 'notes.txt')
    if os.path.exists(appfile):
        #write_log('reading notes: file found', log, verbose)
        return open(appfile, 'r')
    else:
        #write_log('reading notes: no notes found', log, verbose)
        return []

def open_data_target():
    appdir = os.path.expanduser(os.path.join("~", "." + __APPNAME__))
    appfile = os.path.join(appdir, 'notes.new')
    if not os.path.exists(appdir):
        os.makedirs(appdir)
    return open(appfile, 'w')

def move_data_target():
    appdir = os.path.expanduser(os.path.join("~", "." + __APPNAME__))
    appfile = os.path.join(appdir, 'notes.txt')
    newfile = os.path.join(appdir, 'notes.new')
    oldfile = os.path.join(appdir, 'notes.old')
    if os.path.exists(appfile):
        shutil.move(appfile, oldfile)
    shutil.move(newfile, appfile)

@app.route('/', methods=['GET', 'POST'])
def main():
    '''
        main entry point
    '''
    return flask.render_template('main.html')

@app.route('/list', defaults={'filter': None}, methods=['GET', 'POST'])
@app.route('/list/<filter>', methods=['GET', 'POST'])
def show_list(filter=None):
    src = open_data_source()
    first = True
    count = 0
    result = []
    for line in src:
        if first:
            first = False
            if not filter or re.search(filter, line.strip('\n'), re.I) is not None:
                result.append(line.strip('\n'))
                count += 1
        elif line.strip('\n') == TERMINATOR:
            first = True
    return flask.jsonify(data=result) 

@app.route('/item', defaults={'name': None}, methods=['GET', 'POST'])
@app.route('/item/<name>', methods=['GET', 'POST'])
def show_item(name):
    src = open_data_source()
    first = True
    title = None
    is_match = False
    count = 0
    out = []
    for line in src:
        if first:
            first = False
            title = line
            if line.strip('\n') == name:
                is_match = True
                count += 1
        else:
            if line.strip('\n') == TERMINATOR:
                first = True
                is_match = False
            if is_match:
                out.append(line)
    return ''.join(out)

@app.route('/update', defaults={'name': None}, methods=['POST'])
@app.route('/update/<name>', methods=['POST'])
def save_item(name):
    src = open_data_source()
    target = open_data_target()
    found = False
    in_found = False
    first = True
    new_entry = ''
    # write everything except the entry of interest
    for line in src:
        if in_found:
            if line.strip('\n') == TERMINATOR:
                in_found = False
                first = True
            else:
                new_entry += line
        else:
            if first and line.lower().strip('\n') == name.lower(): # case insensitive match
                new_entry = line
                found = True
                in_found = True
                first = False
            else:
                target.write(line)
                if line.strip('\n') == TERMINATOR:
                    first = True
                else:
                    first = False

    # make changes or add new
    target.write('{0}\n'.format(name))
    target.write(flask.request.form["content"])
    target.write('\n{0}\n'.format(TERMINATOR))
    target.close()
    move_data_target()
    return "saved"

@app.route('/remove', defaults={'name': None}, methods=['POST'])
@app.route('/remove/<name>', methods=['POST'])
def remove_item(name):
    src = open_data_source()
    target = open_data_target()
    found = False
    in_found = False
    first = True
    new_entry = ''
    # write everything except the entry of interest
    for line in src:
        if in_found:
            if line.strip('\n') == TERMINATOR:
                in_found = False
                first = True
            else:
                new_entry += line
        else:
            if first and line.lower().strip('\n') == name.lower(): # case insensitive match
                new_entry = line
                found = True
                in_found = True
                first = False
            else:
                target.write(line)
                if line.strip('\n') == TERMINATOR:
                    first = True
                else:
                    first = False
    target.close()
    move_data_target()
    return "removed"

@app.route('/create', defaults={'name': None}, methods=['POST'])
@app.route('/create/<name>', methods=['POST'])
def create_item(name):
    src = open_data_source()
    target = open_data_target()
    found = False
    in_found = False
    first = True
    new_entry = ''
    # write everything except the entry of interest
    for line in src:
        if in_found:
            if line.strip('\n') == TERMINATOR:
                in_found = False
                first = True
            else:
                new_entry += line
        else:
            if first and line.lower().strip('\n') == name.lower(): # case insensitive match
                new_entry = line
                found = True
                in_found = True
                first = False
            else:
                target.write(line)
                if line.strip('\n') == TERMINATOR:
                    first = True
                else:
                    first = False

    if found:
        return "exists"
    else:
        new_entry = '{0}\n{1}\n{2}\n'.format(name, DEFAULT_NOTE, TERMINATOR)
        target.write(new_entry)
        target.close()
        move_data_target()

    return "created"

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(port=5001)