from requests_html import HTMLSession
session = HTMLSession()

r = session.get('https://brokencrystals.com/userlogin')
r.html.render(sleep=1)


print(r.html.html)