from time import sleep
from urllib import request, response
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
response = requests.get('https://defendtheweb.net/auth')

soup = BeautifulSoup(response.text)
inputs=soup.find("input", {"name": "token"})
print(inputs['value'])
# for i in range(1):
#     response = requests.get('https://defendtheweb.net/auth')
#     # input_tag=response.html.find('submit')
#     # print(response.html.html)
#     value = response.search('name="user_token" value="{}"')
#     print(value[0])
#     # output = input_tag['value']
#     # print(input_tag)
    
