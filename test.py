from cgitb import text
import logging
from struct import pack
import sys
import time

import soupsieve
import re
import webParser
import requests
from bs4 import BeautifulSoup
from lxml import html
import asyncio
from playwright.async_api import async_playwright



def main():

    packet = {'uname' : 'assi', 'pass' : 'test'}
    res = requests.post("http://testphp.vulnweb.com/userinfo.php",data=packet)
    
    print(res.history[0].status_code)
   
# asyncio.run(main())
main()