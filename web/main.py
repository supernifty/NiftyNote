# -*- coding: utf-8 -*-
'''
    main web interface
'''
import os
import re

import flask

import auth
import config
import proxy
import store

TERMINATOR = '== terminator =='
DEFAULT_NOTE = 'Put your note content here'
AUTHORIZED_URL = '/authorized'

app = flask.Flask(__name__, template_folder='templates')
app.wsgi_app = proxy.ReverseProxied(app.wsgi_app)
app.config.from_pyfile('config.py')
app.secret_key = 'ducks in space'

if config.AUTHENTICATE:
    authenticator = auth.GoogleAuth(app)
else:
    authenticator = auth.NoAuth(app)


@app.route('/help', methods=['GET'])
def help():
    return flask.render_template('help.html')

@app.route('/', methods=['GET', 'POST'])
def main():
    '''
        main entry point
    '''
    if config.AUTHENTICATE and not authenticator.is_auth(flask.session):
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('main.html', username=authenticator.username(flask.session))

@app.route('/list', defaults={'filter': None}, methods=['GET', 'POST'])
@app.route('/list/<filter>', methods=['GET', 'POST'])
def show_list(filter=None):
    if config.AUTHENTICATE and not authenticator.is_auth(flask.session):
        return None # shouldn't happen
    src = store.open_data_source(authenticator.username(flask.session))
    first = True
    content = None
    count = 0
    result = []
    for line in src:
        if first: # start of entry
            first = False
            if not filter or re.search(filter, line.strip('\n'), re.I) is not None:
                result.append([line.strip('\n'), None]) # title, content
                count += 1
                content = []
        elif line.strip('\n') == TERMINATOR: # end of entry
            first = True
            if content is not None:
                result[-1][1] = ''.join(content)
                content = None
        else:
            if content is not None:
                content.append(line)
    return flask.jsonify(data=result) 

@app.route('/item', defaults={'name': None}, methods=['GET', 'POST'])
@app.route('/item/<name>', methods=['GET', 'POST'])
def show_item(name):
    '''
      extracts content of a given entry
    '''
    if config.AUTHENTICATE and not authenticator.is_auth(flask.session):
        return None # shouldn't happen
    src = store.open_data_source(authenticator.username(flask.session))
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
    '''
      updates entry with new content
    '''
    if config.AUTHENTICATE and not authenticator.is_auth(flask.session):
        return None # shouldn't happen
    src = store.open_data_source(authenticator.username(flask.session))
    target = store.open_data_target(authenticator.username(flask.session))
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
    store.move_data_target(authenticator.username(flask.session))
    return "saved"

@app.route('/remove', defaults={'name': None}, methods=['POST'])
@app.route('/remove/<name>', methods=['POST'])
def remove_item(name):
    '''
      removes specified entry
    '''
    if config.AUTHENTICATE and not authenticator.is_auth(flask.session):
        return None # shouldn't happen
    src = store.open_data_source(authenticator.username(flask.session))
    target = store.open_data_target(authenticator.username(flask.session))
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
    store.move_data_target(authenticator.username(flask.session))
    return "removed"

@app.route('/create', defaults={'name': None}, methods=['POST'])
@app.route('/create/<name>', methods=['POST'])
def create_item(name):
    '''
      creates an empty entry
    '''
    if config.AUTHENTICATE and not authenticator.is_auth(flask.session):
        return None # shouldn't happen
    src = store.open_data_source(authenticator.username(flask.session))
    target = store.open_data_target(authenticator.username(flask.session))
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
        store.move_data_target(authenticator.username(flask.session))

    return "created"

### authentication logic ###
@app.route('/login')
def login():
    return authenticator.authorize()

@app.route('/logout')
def logout():
    authenticator.logout(flask.session)
    return flask.redirect(flask.url_for('help'))

# end up here after authentication
@app.route('/authorized')
def authorized():
    result = authenticator.authorized(flask.session)
    if result is None:
        return flask.redirect(flask.url_for('main'))
    else:
        return result # todo: error page

@authenticator.google.tokengetter
def get_google_oauth_token():
    return authenticator.token(flask.session)

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(port=5001)
