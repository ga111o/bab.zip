from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import sqlite3
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from db import save_restaurant

def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    os.environ['DISPLAY'] = ':0'
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def get_unknown_place_ids():
    conn = sqlite3.connect('bab.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT place_id FROM restaurants WHERE name = 'Unknown'")
    place_ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return place_ids

def main():
    place_ids = get_unknown_place_ids()
    
    if not place_ids:
        print("No places with 'Unknown' name found in the database.")
        return
    
    print(f"Found {len(place_ids)} places with 'Unknown' name.")
    
    driver = setup_chrome_driver()
    driver.implicitly_wait(10)
    
    try:
        while True:
            for place_id in place_ids:
                url = f"https://map.naver.com/p/search/ㅇㅇ/place/{place_id}?isCorrectAnswer=true"
                url_info = f"https://map.naver.com/p/search/ㅇㅇ/place/{place_id}?c=15.00,0,0,0,dh&placePath=/information&isCorrectAnswer=true"
                print(f"Opening URL: {url}")
                driver.get(url)
                
                time.sleep(5)
                
                name_text = None
                theme_text = None
                address_text = None
                phone_text = None
                description_text = None
                
                try:
                    name_text = "Unknown"
                    theme_text = None
                    address_text = None
                    phone_text = None
                    description_text = None
                    
                    print("Switching to entryIframe")
                    iframe = driver.find_element(By.ID, "entryIframe")
                    driver.switch_to.frame(iframe)
                    
                    print("Finding element with class name GHAhO")
                    name = driver.find_element(By.CLASS_NAME, "GHAhO")
                    theme = driver.find_element(By.CLASS_NAME, "lnJFt")
                    address = driver.find_element(By.CLASS_NAME, "LDgIH")
                    phone = driver.find_element(By.CLASS_NAME, "xlx7Q")

                    image_url = None

                    image_url = driver.find_element(By.ID, "ibu_1")
                    image_url = image_url.get_attribute('src')
                    print(f"Image URL: {image_url}")
                    
                    try:
                        click_workhour_element = driver.find_element(By.CSS_SELECTOR, ".w9QyJ.vI8SM.DzD3b")
                        print("Found clickable element, clicking...")
                        click_workhour_element.click()
                        time.sleep(2)
                        
                        try:
                            workhour_container = driver.find_element(By.CSS_SELECTOR, ".gKP9i.RMgN0")

                            workhour_elements = workhour_container.find_elements(By.CLASS_NAME, "A_cdD")
                            
                            if len(workhour_elements) > 1:
                                workhour_elements = workhour_elements[1:]
                            
                            workhour_texts = [elem.text for elem in workhour_elements if elem.text.strip()]
                            workhour = "\n".join(workhour_texts)
                            
                            print(f"Workhour information retrieved: {workhour}")
                        except NoSuchElementException:
                            print("Could not find workhour container with class 'gKP9i RMgN0'")
                            workhour = None
                    except NoSuchElementException:
                        print("Could not find element with class 'w9QyJ vI8SM DzD3b' to click")
                        workhour = None
                    
                    name_text = name.text
                    theme_text = theme.text
                    address_text = address.text
                    phone_text = phone.text
                    workhour_text = workhour

                    print(f"{name_text} / {theme_text} / {address_text} / {phone_text}")
                    driver.switch_to.default_content()

                    driver.get(url_info)
                    time.sleep(3)

                    try:
                        print("Switching to entryIframe")
                        iframe = driver.find_element(By.ID, "entryIframe")
                        driver.switch_to.frame(iframe)
                        info = None
                        info = driver.find_element(By.CLASS_NAME, "T8RFa")
                        description_text = info.text if info else None

                    except NoSuchElementException:
                        print(f"Element with class T8RFa or iframe not found for place_id: {place_id}")

                    save_restaurant(
                        place_id=place_id,
                        name=name_text,
                        address=address_text,
                        phone=phone_text,
                        theme=theme_text,
                        description=description_text,
                        business_hours=workhour_text,
                        title_image_url=image_url
                    )
                    
                    if place_id in place_ids:
                        place_ids.remove(place_id)

                except NoSuchElementException:
                    print(f"Element with class GHAhO or iframe not found for place_id: {place_id}")

                time.sleep(1)
    
    except KeyboardInterrupt:
        print("Script stopped by user.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
