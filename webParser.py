import logging
from tkinter import Button
from typing import Tuple
import urllib
from collections import defaultdict
from winsound import PlaySound
from lxml import html
import requests
from requests_html import HTMLSession
from playwright.async_api import async_playwright 
from bs4 import BeautifulSoup as bs
import time
class webParser:
        

    async def getsource(self, url, params_list):
        """
        find the username and password params in the body
        """
        p = await async_playwright().start()
        browser = await p.firefox.launch(headless=False)
            
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state()
            
        body = await page.content()
        soup = bs(body, 'html.parser')
        buttons = soup.findAll(attrs={'type' : 'submit'})
        form = self.findForm(buttons, params_list["ButtonList"])
        #loginButton = form.findChild(attrs={'type':'submit'})
        
        self.user_param, self.password_param = self.findUserPass(form, params_list["password_param"], params_list["user_param"])
                
        await self.getRequest(self.user_param, self.password_param, page)
        await browser.close()
        await p.stop()

        self.req_body_type = self.get_req_type()

        
    #picks the login form in page
    def pickForm(self, forms):
        input_list = []
        for form in forms:
            for b in form:
                print(str(b.get('value')))
            
            print(str(form))
            # for b in form.buttons:
            #     print(str(b))

    #identify the user and password params in the body
    def findUserPass(self, form, passwords, usernames):
        print('\n\n\n\n\n\n\n'+str(form))
        username = None
        password = None
        inputs = {}
        for input in form.findChildren('input'):
            if input['type'].lower() != 'submit':
                inputName = input['name']
                inputs[inputName] = ""
                if input['type'] == 'email':
                    username = inputName
                elif input['type'] == 'password':
                    password = inputName
        
        if not username:
            username = self.pick_param(inputs, usernames) 
            inputs.pop(username)
        if not password: 
            password = self.pick_param(inputs, passwords) 

        return username, password

    def jaccard_similarity(self, a, b):
        # convert to set
        a = set(a)
        b = set(b)
        # calucate jaccard similarity
        j = float(len(a.intersection(b))) / len(a.union(b))
        return j


    def similarity_value(self, param, usernames):
        if not param:
            return 0
        max = 0
        for uname in usernames:
            score = self.jaccard_similarity(param.lower(), uname)
            if score > max:
                max = score
        return max


    def pick_param(self, inputs, list):
        #param with max potetntial for being the username
        inputName = max(inputs, key=lambda x: self.similarity_value(x, list)) 
        return inputName

    def getRequestData(self, req):
        if req.method == 'POST': 
            self.post_data = req.post_data_json
            self.method = req.method
            self.headers = {k.lower(): v for k, v in req.headers.items()}
            print('headers: ', str(type(self.headers)))
            self.action = req.url

    
    def getResponse(self, response):
        self.status = response.status
        
        
    async def getRequest(self, username, password, page):

        await page.fill('input[name='+username+']', 'test')
        await page.fill('input[name='+password+']', 'test')
        page.once("request", lambda req: self.getRequestData(req))
        page.once("response", lambda res: self.getResponse(res))
        # response = await Promise.all([page.waitForResponse(str(self.url))
        # print(response.status)


        await page.locator('[type="submit"]:near(input[name='+ password+'])').click()
        print(str(self.status))
        
        

    def formScore(self, form, button, buttonList):
        print('button list: '+ str(buttonList))
        buttonValueScore = self.similarity_value(button['value'], buttonList)
        buttonTextScore = self.similarity_value(button.text, buttonList)
        print('lol: ' + str(buttonValueScore) + ' ' + str(buttonTextScore))
        score = max(buttonValueScore, buttonTextScore)
        if score == 1:
            return 10
        
        # check this later!
        for label in buttonList:
            if label in str(form.text).lower():
                score += 0.3

        inputs = []
        for inp in form.findChildren('input'):
            if inp['type'] == 'text' or inp['type'] == 'email' or inp['type'] == 'password' :
                inputs.append(inp)
                
        if len(inputs) < 2:
            return 0
        
        if len(form.findChildren('input', {'type' : 'password'})) == 1:
            score += 0.5
        if len(form.findChildren('input', {'type' : 'email'})) == 1:
            score += 0.3
        
    def findForm(self, buttons, buttonList):
        maxScore = 0
        for button in buttons:
            form = button.findParent('form')
            score = self.formScore(form, button, buttonList)
            if score > maxScore:
                maxScore = score
                pickedForm = form
                self.button = button
        
        return pickedForm


        
        # get content type from headers
    def get_req_type(self):
        type = self.headers["content-type"]

        if "json" in type:
            return "JSON"

        elif "xml" in type:
            import xmltodict
            
        elif "multipart" in type:
            return "multipart"

        else:
            import urllib

            return "URL_ENCODED"
