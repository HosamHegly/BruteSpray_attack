import argparse

from colored import fg, bg, attr, stylize

import attack


class LoginBrute:
    default = fg(246)
    green = fg(34) + attr('bold')
    yellow = fg(221)
    reset = attr('reset')

    error = fg('red') + '[!] ' + default
    detail = fg(220) + '[*] ' + default
    fail = fg('red') + '[-] ' + default
    success = fg('green') + '[+] ' + default
    event = fg(26) + '[*] ' + default
    debug = '[+]--- '
    notification = fg(246) + '[-] ' + default

    creds_found = 0
    __banner__ = green + '''
#########################################
 __________                __          
\______   \_______ __ ___/  |_  ____  
 |    |  _/\_  __ \  |  \   __\/ __ \ 
 |    |   \ |  | \/  |  /|  | \  ___/ 
 |______  / |__|  |____/ |__|  \___  >
        \/                         \/ 

##########################################
    '''

    def __init__(self, ):
        print(self.__banner__ + "\n")
        params = self.get_parameters(self.get_args())
        attack.brute(params)

    def get_args(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-U', '--user', type=str, help='specify the user name for the login')
        parser.add_argument('-u', '--userList', type=str, help='specify the wordlist for the username')
        parser.add_argument('-P', '--password', type=str, help='specify the password for the login')
        parser.add_argument('-p', '--passList', type=str, help='specify the wordlist for the password')
        parser.add_argument('-d', '--data', type=str,
                            help='specify the parameters, '
                                 'Ex: username=User@password=pwd@submit=yes@action=/userinfo.php@method=post')
        parser.add_argument('-l', '--url', type=str, help='specify the url to the form', required=True)
        parser.add_argument('-t', '--failTxt', type=str, help='provide a text that appears when login fails')

        return parser.parse_args()

    def get_parameters(self, args):
        username = args.user
        user_list = args.userList
        password = args.password
        pass_list = args.passList
        data = args.data
        url = args.url
        fail_text = args.failTxt
        if pass_list:
            try:
                pass_list = open(pass_list, 'rb').readlines()
            except IOError as e:
                print(fg('red') + 'File' + pass_list + ' not found')

        if user_list:
            try:
                user_list = open(user_list, 'rb').readlines()
            except IOError as e:
                print(fg('red') + 'File' + user_list + 'not found')

        if not user_list and not username:
            username = 'test'

        if not pass_list and not password:
            password = 'test'

        if  data:
            if 'username' not in data or 'password' not in data or 'method' not in data or 'submit' not in data or 'action' not in data:
                print(self.error + 'invalid html parameters input\n')
                exit(1)
            try:
                params = data.split('@')
            except IOError as e:
                print(self.error + 'invalid html parameters input\n')
                exit(1)
            for param in params:
                i = param.rfind('=')
                p = param[i+1]
                if 'username' in param:
                    user_param = p
                elif 'password' in param:
                    password_param = p
                elif 'submit' in param:
                    submit = p
                elif 'action' in param:
                    action = p
                elif 'method' in param:
                    method = p

        else:
            import scraper1
            user_param, password_param, submit, action, method = scraper1.get_source(url)
        print(user_param,password_param,submit,method,action)


        if 'http' not in action:
            i = url.rfind('/')
            url = url[0:i + 1]
            url = url + action
        else:
            url = action

        return {
            'username': username,
            'user_list': user_list,
            'password': password,
            'password_list': pass_list,
            'user_param': user_param,
            'password_param': password_param,
            'method': method,
            'url': url,
            'fail_text': fail_text,

        }


LoginBrute()
