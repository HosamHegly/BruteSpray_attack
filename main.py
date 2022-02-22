import argparse


import attack


class LoginBrute:

    __banner__ = '''
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
                            help='specify the parameters, Ex: username=$U&password=$P&submit=yes&action=/userinfo.php')
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
            username = 'alqlambara@gmail.com'

        if not pass_list and not password:
            password = 'bara12340'

        if not data: 
            pass
        import params_scraper
        user_param, password_param, submit, action, method = params_scraper.get_source(url)
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
