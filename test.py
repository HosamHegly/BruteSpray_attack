from lxml import html
from time import sleep
from urllib import request, response
from requests_html import HTMLSession
import requests
from xml.etree import ElementTree as et

request = requests.get('https://brokencrystals.com/api/auth/simple-csrf-flow')

cookies = {}
req_body = {'csrf':'lol','op':'csrf','user':'mohamadassi173@gmail.com','password':'astmamsh123'}
for cookie in request.cookies:
    cookies[cookie.name] = cookie.value

for item in cookies.keys():
    if item[1:] in req_body:
        req_body[item[1:]]= cookies[item]
    if item in req_body:
        req_body[item]= cookies[item]

print('cookies: ' + str(cookies) + '\n\n\n\n')
print('req_body: ' + str(req_body))

request = requests.post('https://brokencrystals.com/api/auth/login',data=req_body,cookies=cookies)
print('\n\n\n\n')
print(request.status_code)