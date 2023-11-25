from pyvirtualdisplay import Display
from selenium import webdriver

with Display() as disp:
    driver = webdriver.Chrome()
    driver.get('https://www.tocode.co.il')
    print(driver.title)
    driver.close()
