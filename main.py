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

        # init logging and create log file with "date filename"
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
            "-l", "--url", type=str, help="specify the url to the form", required=True
        )
        url = parser.parse_args().url

        # retrieve login page technology for example: wordpress, wix...
        web_info = WebInfo.webInfo(url)
        web_parser = webParser.webParser()
        await web_parser.getsource(url, args["params_list"], pass_user)

        logging.info(json.dumps(args, indent=2, default=str))
        logging.info(json.dumps(web_parser.__dict__, indent=2, default=str))

        # check if page is written in javascript/typescript and use the proper attack accordingly
        if web_info.type == "javascript":  # needs to modify this later!!!!!!
            headless1 = headless.headless(web_info.url, web_parser, pass_user)
            await headless1.brute()
        else:
            html_brute = htmlBrute.htmlBrute(web_info.url, web_parser, pass_user)
            html_brute.brute()


import asyncio

asyncio.run(LoginBrute.main())
