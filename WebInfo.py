from Wappalyzer import Wappalyzer, WebPage
from builtwith import *


class webInfo:
    def __init__(self, url, technologies, is_javascript):
        """checks the web pages technology with the help of wappalyzer and builtwith libraries
        also provides the login page url based on the technology
        """
        webpage = WebPage.new_from_url(url)
        wappalyzer = Wappalyzer.latest()
        wappalyzer = wappalyzer.analyze_with_versions_and_categories(webpage)
        self.is_javascript = is_javascript
        self.url = url
        self.type = "javascript"

        # flag in order to run the attack with playwright.
        if "react" in builtwith(url):
            self.is_javascript = True

        for tech_key in wappalyzer:
            if tech_key in technologies.keys():
                self.type = "html"  # change the technology type to html based
                self.tech = tech_key
                self.techLoginPage = technologies[tech_key]

        if self.type == "html":
            if self.techLoginPage not in url:
                self.url += self.techLoginPage

        else:
            self.is_javascript = True
