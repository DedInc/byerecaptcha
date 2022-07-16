<h1 align="center">byerecaptcha - Google Recaptcha solver with selenium.</h1>

<h2>Model and some codes takes from <a href="https://github.com/embium/solverecaptchas">embium's repository</a></h2>

<h1 align="center"> -Installation- </h1>

```sh
pip install byerecaptcha
```

<h1 align="center"> -How to use- </h1>

```python
from selenium import webdriver
from selenium_utilities import getChromeDriver
from byerecaptcha import solveRecaptcha

options = webdriver.ChromeOptions()
options.add_argument('--lang=en-US') #need for recaptcha be in english

driver = webdriver.Chrome(executable_path=getChromeDriver(), chrome_options=options)
driver.get('https://www.google.com/recaptcha/api2/demo')
solveRecaptcha(driver) #FOR PREDICTION ON YOUR PC

solveRecaptcha(driver, server="https://myserver.com") #FOR PREDICTION IN YOUR SERVER (check server.py)

solveRecaptcha(driver, invisible=True) #FOR PREDICTION INVISIBLE CAPTCHA
```