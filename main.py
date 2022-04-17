import attack
import WebInfo
import yaml
import pandas


class LoginBrute:
    def __init__(
        self,
    ):
        print("bruteSpray attack started!\n\n")

        with open("config.yml", "r") as ymlfile:
            args = yaml.safe_load(ymlfile)

        args["url"]  = WebInfo.get_admin_page(args["url"])

        try:
            pass_user = pandas.read_csv(args["pass_user"])

        except IOError as e:
            print("File " + args["pass_user"] + " not found")
            return

        args["user_list"] = pass_user["Usernames"]
        args["passwords"] = pass_user["Passwords"]
        
        attack.brute(args) 


LoginBrute()
