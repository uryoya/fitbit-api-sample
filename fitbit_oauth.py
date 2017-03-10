from flask import Flask, redirect, request, jsonify
from urllib.parse import urlencode
import requests
import base64
import pickle
import os

app = Flask(__name__)
app.debug = True
authorization_url = 'https://www.fitbit.com/oauth2/authorize'
access_token_url = 'https://api.fitbit.com/oauth2/token'
client_secret = 'b2a1b298d81cf7d4893974c1c9eedb98'
client_id = '2284BG'

# Get from access token request
access_token = ''
expires_in = 0
refresh_token = ''
token_type = ''
user_id = ''
if os.path.exists('access_token.pkl'):
    with open('access_token.pkl', 'rb') as f:
        data = pickle.load(f)
    access_token, expires_in, refresh_token, token_type, user_id = data


@app.route('/')
def index():
    return "<a href=/login>login</a>"


@app.route('/login')
def login():
    """ Authorization Pageへリダイレクト """
    params = urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'heartrate',
        'redirect_url': 'http://localhost:5000/login/authorized',
    })
    return redirect(authorization_url + '?' + params)


@app.route('/login/authorized')
def authorized():
    """ codeを取得してaccess tokenと交換 """
    code = request.args.get('code')
    # exchange the authorization code for an access code
    r = requests.post(
        access_token_url,
        headers={
            'Authorization': authorization_header(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
             'code': code,
             'grant_type': 'authorization_code',
             'client_id': client_id,
             }
    )
    if r.status_code == 200:
        data = r.json()
        global access_token, expires_in, refresh_token, token_type, user_id
        access_token = data['access_token']
        expires_in = data['expires_in']
        refresh_token = data['refresh_token']
        token_type = data['token_type']
        user_id = data['user_id']
        with open('access_token.pkl', 'wb') as f:
            pickle.dump((access_token,
                         expires_in,
                         refresh_token,
                         token_type,
                         user_id),
                        f,
                        pickle.HIGHEST_PROTOCOL)
        return '<p>code: {}</p><p>access token: {}</p>'.format(code,
                                                               access_token)
    else:
        return """<h1>failed</h1>
        <h2>request url</h2> <p>{}</p>
        <h2>status</2> <p>{}</p>
        <h2>body</h2> <p>{}</p>
        """.format(r.url, r.status_code, r.text)


@app.route('/userpage')
def userpage():
    resource_url = 'https://api.fitbit.com/1/user/{}/activities/heart/date/today/1d.json'.format(user_id)
    r = requests.get(resource_url,
                     headers={'Authorization': 'Bearer ' + access_token})
    if r.status_code == 200:
        return jsonify(r.json())
    else:
        return 'failed'


@app.route('/heartrate')
def heartrate():
    resource_url = 'https://api.fitbit.com/1/user/{}/activities/heart/date/2017-01-28/1d/1sec/time/00:00/23:59.json'.format(user_id)
    r = requests.get(resource_url,
                     headers={'Authorization': 'Bearer ' + access_token})
    if r.status_code == 200:
        return jsonify(r.json())
    else:
        return 'failed'


@app.route('/revoke')
def revoke():
    r = requests.post('https://api.fitbit.com/oauth2/revoke',
                      headers={
                          'Authorization': authorization_header(),
                          'Content-Type': 'application/x-www-form-urlencoded'
                      },
                      data={'token': access_token})
    if r.status_code == 200:
        return 'revoke success'
    else:
        return '<p>revoke failed</p><p>{}</p>'.format(r.text)


def authorization_header():
    authorization = base64.b64encode(
        '{}:{}'.format(client_id, client_secret).encode()
    ).decode()
    return 'Basic {}'.format(authorization)


if __name__ == '__main__':
    app.run()
