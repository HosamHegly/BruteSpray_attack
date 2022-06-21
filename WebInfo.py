from Wappalyzer import Wappalyzer, WebPage

class webInfo:
    
    def __init__(self, url):
        webpage = WebPage.new_from_url(url)
        print(str(webpage))
        wappalyzer = Wappalyzer.latest()
        wappalyzer = wappalyzer.analyze(webpage)
        # wappalyzer = Wappalyzer.analyze_with_categories(webpage)
        self.url = url
        if 'WordPress' in wappalyzer:
            if 'wp-login.php' not in url:
                self.url += '/wp-login.php' 
        elif 'Joomla' in wappalyzer:
            if 'index.php?option=com_users&lang=en&view=login' not in url:
                self.url += '/index.php?option=com_users&lang=en&view=login' 
        elif 'Drupal' in wappalyzer:
            self.url += 'user/login'
        
        print('tech: ' + str(wappalyzer))
        self.type = 'javascripts'
