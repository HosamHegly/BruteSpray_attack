from Wappalyzer import Wappalyzer, WebPage
from builtwith import *
class webInfo:
    
    def __init__(self, url, technologies, is_javascript):
        '''checks the web pages technology with the help of wappalyzer and builtwith libraries 
           also provides the login page url based on the technology
        '''
        webpage = WebPage.new_from_url(url)
        wappalyzer = Wappalyzer.latest()
        wappalyzer = wappalyzer.analyze_with_versions_and_categories(webpage)
        self.is_javascript = is_javascript
        self.url = url
        self.type = 'javascript'

        # flag in order to run the attack with the appropriate tool (playwright in this case)
        if "react" in builtwith(url):
            self.is_javascript = True 
        
        for tech_key in wappalyzer:
            if tech_key in technologies:
                self.type = "html"
                self.tech = tech_key
                    
        if self.type == "html":
            if self.tech == 'WordPress':
                if 'wp-login.php' not in url:
                    self.url += 'wp-login.php' 
            elif self.tech == 'Joomla':
                if 'index.php?option=com_users&lang=en&view=login' not in url:
                    self.url += '/index.php?option=com_users&lang=en&view=login' 
            elif self.tech == 'Drupal':
                self.url += 'user/login'
                
        else:
            self.is_javascript = True
        