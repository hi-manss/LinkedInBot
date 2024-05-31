from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import os
import pickle
import pandas as pd

# Function to login to LinkedIn
# def login_to_linkedin(driver, username, password):
#     driver.get('https://www.linkedin.com/login')
#     time.sleep(2)

#     username_field = driver.find_element(By.ID, 'username')
#     username_field.send_keys(username)

#     password_field = driver.find_element(By.ID, 'password')
#     password_field.send_keys(password)
#     password_field.send_keys(Keys.RETURN)
#     time.sleep(2)

#     # Wait for manual intervention in case of CAPTCHA
#     input("Please complete the CAPTCHA or security check and press Enter to continue...")

# Function to search and filter profiles
def search_profiles(driver, search_query):
    search_box = driver.find_element(By.XPATH, '//input[contains(@placeholder, "Search")]')
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    # Click on the 'People' filter to ensure we're only looking at profiles
    people_filter = driver.find_element(By.XPATH, '//button[text()="People"]')
    people_filter.click()
    time.sleep(5)

# Function to extract profile links from a page
# def extract_profile_links(driver):
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     profile_links = []
#     if soup.find_all(''):
#         profile_name_links = soup.select('span.entity-result__title-text a')
    
#     for profile in profile_name_links:
#         profile_url = profile['href']
#         if profile_url not in profile_links:
#             profile_links.append(profile_url)
    
#     return profile_links

# Function to navigate to next page
def go_to_next_page(driver):
    try:
        next_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Next")]')
        next_button.click()
        return True
    except:
        return False

# Function to load cookies
def load_cookies(driver):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)


# Function to check if the profile is a connection
def is_non_connection(button_text):
    return button_text in ['Connect', 'Follow']


# Function to scroll down the page
def scroll_down_page(driver, scroll_pause_time=1, scrolls=1):
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)


# Function to extract profile links from a page and filter non-connections
def extract_non_connection_profile_links(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    profile_links = []
    profiles = soup.select('span.entity-result__title-text a')
    for profile in profiles:
        profile_url = profile['href']
        button = profile.find_next('button')
        if button and is_non_connection(button.text.strip()):
            if not profile_url.startswith('https://'):
                profile_url = 'https://www.linkedin.com' + profile_url
            profile_links.append(profile_url)
    return profile_links

# Function to navigate to next page
def go_to_next_page(driver):
    try:
        scroll_down_page(driver)
        print("land on the next page function")
        next_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Next")]')
        next_button.click()
        return True
    except:
        return False

# Function to save profiles to CSV
def save_profiles_to_csv(profiles, filename='visited_profiles.csv'):
    df = pd.DataFrame(profiles, columns=['Profile URL'])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, mode='w', header=True, index=False)


# Main function
def main():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        driver.get('https://www.linkedin.com')
        load_cookies(driver)
        driver.refresh()

        search_queries = ['Talent Acquisition', 'IT recruiter']
        for search_query in search_queries:
            search_profiles(driver, search_query)

            scroll_down_page(driver)

            all_profile_links = []

            for page in range(1):
                profile_links = extract_non_connection_profile_links(driver)
                all_profile_links.extend(profile_links)
                if not go_to_next_page(driver):
                    break
                time.sleep(5)  # Wait for the next page to load

            # Remove duplicates
            all_profile_links = list(set(all_profile_links))
            # print(all_profile_links)
            visited_profiles = []

            # Visit each profile link
            for profile_url in all_profile_links:
                try:
                    if not profile_url.startswith('https://'):
                        profile_url = 'https://www.linkedin.com' + profile_url
                    print(f"Visiting: {profile_url}")
                    driver.get(profile_url)
                    time.sleep(5)  # Simulate viewing the profile
                    visited_profiles.append(profile_url)
                    time.sleep(5)  # Simulate viewing the profile
                except Exception as e:
                    print(f"An error occurred while visiting {profile_url}: {e}")
                finally:
                    # Save visited profiles to CSV in case of error
                    save_profiles_to_csv(visited_profiles)
                    visited_profiles = []  # Reset list after saving to prevent duplicates

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
