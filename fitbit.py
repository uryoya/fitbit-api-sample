from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

fitbit = oauth.remote_app(
    'fitbit',
    consumer_key='2284BG',
    consumer_secret='b2a1b298d81cf7d4893974c1c9eedb98',
    base_url='https://api.fitbit.com/',
    request_token_url='https://api.fitbit.com/oauth2/token',
    access_token_method='POST',
    access_token_url='https://api.fitbit.com/oauth2/token',
    authorize_url='https://www.fitbit.com/oauth2/authorize',
)


@app.route('/')
def index():
    if 'fitbit_token' in session:
        me = fitbit.get('user')
        return jsonify(me.data)
#    return redirect(url_for('login'))
    return 'hoge'


@app.route('/login')
def login():
    return fitbit.authorize(callable=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('fitbit', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = fitbit.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['fitbit_token'] = (resp['access_token'], '')
    me = fitbit.get('user')
    return jsonify(me.data)


@fitbit.tokengetter
def get_fitbit_oauth_token():
    return session.get('fitbit_token')


if __name__ == '__main__':
    app.run()
