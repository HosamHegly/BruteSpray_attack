# **Advanced Brute Force Project**
## **Project Goal**

A joint project with CYE, a cyber security company, aims to develop a hacking tool for password spray, credentials brute force, and an admin enumerating the login interfaces

## **Project Solution Description**

**About The Algorithm**

The user is only required to enter the websites URL and the program will automatically locate the admin's login page based on the website's technology and perform the attack with a given username/password lists.

**Project Structure:**

|--- README.md  
|--- main.py  
|  
|--- attack  
|||||| --- headless.py  
|||||| --- htmlBrute.py  
|  
|--- web_parser  
|||||| --- webParser  
|||||| --- webInfo  
|  
|--- utils.py // Check's login function  
|--- config.yml // Configuration File  
|--- pass\_user.csv // Usernames and passwords list  
|--- dockerfile  
|--- requiremenets.txt  

### **Run Without Docker:**

- Clone the project:
```
$ git clone https://github.com/tank351/BruteSpray\_attack.git
```
- Go to the project directory:
```
$ cd BruteSpray\_attack
```
- Install required python libraries:
```
$ pip install -r requirements.txt
```
- Install playwright browser drivers:
```
$ playwright install && playwright install-deps
```
- Add username and password list in pass\_user.csv file, then run:
```
$ python main.py -u WEBSITE-URL.COM
```
**Run With Docker:**

- Clone the project:
```
$ git clone https://github.com/tank351/BruteSpray\_attack.git
```
- Go to the project directory:
```
$ cd BruteSpray\_attack
```
- Build the image:
```
$ docker build -t advanced-brute-force .
```
- Run the project container:
```
$ docker run \

-v PATH\_TO\_SAVE\_LOGFILE:/code/logs/ \

advanced-brute-force \

-u WEBSITE-URL.COM
```
**Arguments explanation:**

**-u :** Specify the url. (required)

**-p:** Submit each username with the parallel password in the file.

**-j :** Initiate the attack with headless browser.

## **Classes Explanation**

**Main Class:**

This class takes the information provided by the Webinfo (the technology, if it was built with javascript etc…) it then chooses the appropriate tool to perform the attack, for instance if the website technology was built with wordpress then the main class chooses the HtmlBrute class to perform the attack and if the technology was built with javascript then it chooses the Headless class to perform the attack because it is required to run the javascript code.

**WebInfo Class:**

This class's main job is to provide the web page's technology with the help of "wappalyzer" and "builtwith" libraries. These libraries identify the page's technology by checking a long list of patterns and regular expressions for each technology. For instance it identifies if the page if built with "Wordpress" by checking if it contains elementors with patterns and expression used mostly by "Wordpress". By identifying the page's technology, we then are able to locate the admin's login page ur extension which is provided in the config yaml(contains a list of technologies, each technology is mapped to it's admin's page url extension), for instance if the page's technology is identified as "Wordpress" then the admin's login page url extension is "wp-login.php". This way we can automatically locate the admin's login page without the user being required to provide additional info other than the website's url.

**WebParser Class:**

This class is responsible for parsing the login page's html, locating the login form, locating the input fields for the username and password, locating the login button and fetching information about the login request and response packets such as status codes, headers ,body and length. All of this is done with the help of Playwright's headless browser and "beautifulsoup4".

- First of all playwright go's to the login page and fetches the page's html

- After parsing the html with "beautifulsoup4" the program then gathers all of the forms in the html and each form is given a score based on it's structure, texts contained in it, the button's id, name and value and finally the input fields types etc...

- After choosing the form with the highest potential of being the login form the program then extracts the input fields and gives each field a score, this score is based on jaccard's similarity function, it compares each fields name attribute to a list of username field names and password field names in the config yaml file and the score is given based on the string similarity. As a result we are able to identify which fields have the highest potential to be the username fields or password fields.

- Similar to the input fields, this class locates the login button also based to jacquard's similarity function. The program compares the name, id, value of each button contained in the login form to a list of strings in the config yaml file and the button with the highest score has the highest potential of being the login button's.
- Builds and provides a string for the login button css locator with the button's attributes, This is required in the headless class in order to locate the button with playwright in each login attempt.
- After gathering all the required information to perform a login attempt with playwright, this class attempts two failed login attempts by choosing two random usernames and generating two random passwords, this is done two times in order to calculate the average content length of the page after a failed login attempt, in addition the program fetches the login request packet and it's response packet, This is required in order to helps us understand the structure of the request packet which required in the HtmlBrute class, It also helps us check if the login was successful in each attempt after initiating the attack in the htmlBrute class and the headless class.

**HtmlBrute Class:**

this class performs the attack with the requests library by forging login post request packets containing and only works with pages written with html not javascript but it's much faster than the headless class which uses a headless browser to perform the attack. Since the login post request packet is provided by the webParser class, we are able to forge the exact same packet but each attempt we replace the username and password and tokens. The tokens are replaced by checking if there is an input in the request's body that matches a field name that is contained in the login form, if it does then the value of this input is changed to the value of the input field in the html of the login form. Same thing if the page's get response contains cookies, the class checks if there are similar keys in the request packets body and in the cookies and changes them accordingly each attempt after refreshing the page.

HtmlBrute also checks whether the login was successful after each attempt, This is done by comparing the status codes, content lengths and the page's htmls of each login attempt and the one's provided by the webParser's intentional faild login attempts.

**Headless Class:**

This class main purpose is to perform the attack with a playwright's headless browser, it does so with the help of the information provided by the webParser class such as password and username fields, button css locator string, response status code and length:

- It initiates a new playwright instance with firefox web driver.

- goes through the usernames and passwords in the user\_pass.csv file and each attempt it fill the username name and password fields that were provided by the webParser class.

- locates the login button with the help of the css locator string that was built and provided by the webParser class.

- waits for a response for the login request and compares this response with the failed response's information provided by the webParser class such as the status code, content length, html similarity.
  
  
  
  
### **Made By:** Mohamad Assi, Hossam Abu Hejly

### **Supervised By:** Dr Amit Dvir, Gil Cohen, Eyal Greenberg
![image](https://user-images.githubusercontent.com/57872327/185535972-a80cf8c0-90ac-48c5-8d9d-a64310ce0ea4.png)
