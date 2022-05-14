from Wappalyzer import Wappalyzer, WebPage


def get_admin_page(url):
    webpage = WebPage.new_from_url(url)
    wappalyzer = Wappalyzer.latest()
    wappalyzer = wappalyzer.analyze(webpage)
    if 'WordPress' in wappalyzer:
        if 'wp-login.php' not in url:
            url += '/wp-login.php' 
    elif 'Joomla' in wappalyzer:
        if 'index.php?option=com_users&lang=en&view=login' not in url:
            url += '/index.php?option=com_users&lang=en&view=login' 
    elif 'Drupal' in wappalyzer:
        url += 'user/login'
    return url