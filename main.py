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
            
        args['headers'] = {k.lower(): v for k, v in args['headers'].items()}
        for param in args['headers']:
            args['headers'][param] = str(args['headers'][param])
            
        url = args['headers']['referer']
        args["url"] = WebInfo.get_admin_page(url)
        args["type"] = "javascriapt"  #

        # remove content length and cookies from headers
        if 'cookie' in args['headers']:
            args['headers'].pop('cookie')
            
        if 'content-length' in args['headers']:
            args['headers'].pop('content-length')
        
        args = webParser.get_source(args, params_list)

        args.update(pass_user)

        logging.info(json.dumps(args, indent=2, default=str))

        attack.brute(args)


LoginBrute()
