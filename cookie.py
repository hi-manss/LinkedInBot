import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Manually log in to LinkedIn
driver.get('https://www.linkedin.com/login')
input("Please log in manually and press Enter to continue...")

# Save cookies to a file
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
driver.quit()
