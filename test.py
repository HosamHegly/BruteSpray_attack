from time import sleep
from urllib import request, response
from requests_html import HTMLSession

for i in range(1):
    session =  HTMLSession()
    response = session.get('http://zero.webappsecurity.com/login.html')
    response.html.render(sleep=1)
    # input_tag=response.html.find('submit')
    # print(response.html.html)
    value = response.html.search('name="user_token" value="{}"')
    print(value[0])
    # output = input_tag['value']
    # print(input_tag)
    
