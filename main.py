from datetime import datetime
from urllib import request
import attack1
import WebInfo
import pandas
import webParser
import logging
import sys
import json
import yaml
from attack import headless
from attack import htmlBrute
class LoginBrute:
    async def main():
    
        logging.basicConfig(
            filename="logs/" + datetime.now().strftime("%d-%m-%Y %H-%M") + ".log",
            filemode="w",
            level=logging.INFO,
        )

        try:

            with open("config.yml", "r") as ymlfile:
                args = yaml.safe_load(ymlfile)


            pass_user = pandas.read_csv(args["pass_user"])

        except IOError as e:
            logging.error(e)
            sys.exit()
        

        web_info = WebInfo.webInfo(args['url'])
        web_parser = webParser.webParser()
        await web_parser.getsource(args['url'], args['params_list'], pass_user)
        

        logging.info(json.dumps(args, indent=2, default=str))
        logging.info(json.dumps(web_parser.__dict__, indent=2, default=str))
        
        if web_info.type == 'javascript':
            headless1 = headless.headless(web_info.url, web_parser,  pass_user)
            await headless1.brute()
        else:
            html_brute = htmlBrute.htmlBrute(web_info.url, web_parser,  pass_user)
            html_brute.brute()

import asyncio
asyncio.run(LoginBrute.main())
