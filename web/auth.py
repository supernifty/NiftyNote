import types

import flask
import flask_oauthlib.client

import config

def dummy(_):
    pass

class NoAuth (object):
    def __init__(self, app):
        self.google = types.SimpleNamespace(tokengetter=dummy)

    def is_auth(self, session):
        return True

    def username(self, session):
        return None

class GoogleAuth (object):
    def __init__(self, app):
        self.oauth = flask_oauthlib.client.OAuth(app)
        self.google = self.oauth.remote_app(
            'google',
            consumer_key=config.GOOGLE_ID,
            consumer_secret=config.GOOGLE_SECRET,
            request_token_params={
                'scope': 'email'
            },
            base_url='https://www.googleapis.com/oauth2/v1/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
        )

    def is_auth(self, session):
        authed = 'google_token' in session 
        return authed

    def username(self, session):
        return session['google_email']

    def authorize(self):
        return self.google.authorize(callback=flask.url_for('authorized', _external=True))

    def logout(self, session):
        session.clear()

    def authorized(self, session):
        resp = self.google.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session['google_token'] = (resp['access_token'], '')
        me = self.google.get('userinfo')
        session['google_email'] = me.data['email']
        return None 

    def token(self, session):
        return flask.session.get('google_token')
