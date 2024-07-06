import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import schedule

URL = "https://stadt.muenchen.de/terminvereinbarung_/terminvereinbarung_abh.html?cts=1000113"

def check_appointment():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(URL)
        print("Page loaded")

        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[name="appointment"]'))
        )
        driver.switch_to.frame(iframe)
        print("Switched to iframe")
    except Exception as e:
        print(f"Error loading page or switching to iframe: {e}")
        driver.quit()
        return False

    try:
        # Wait for the broader container that holds the select element to be present and visible
        container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#F00e214c9f52bf4cddab8ebc9bbb11b2b > fieldset'))
        )
        print("Container element found")
        
        # Now wait for the select element within the container
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[1]/div[2]/form/fieldset/ul/li/select'))
        )
        print("Select element found")
    except Exception as e:
        print(f"Error finding select element: {e}")
        driver.save_screenshot('error_screenshot.png')
        print("Screenshot taken")
        driver.quit()
        return False

    try:
        # Select the number of appointments
        print(f"Select element: {select_element.tag_name}, ID: {select_element.get_attribute('id')}")
        select = Select(select_element)
        select.select_by_value('1')  # Assuming you want to select 1 appointment
        print("Number of appointments selected")
    except Exception as e:
        print(f"Error selecting number of appointments: {e}")
        driver.quit()
        return False

    try:
        # Wait for the "Weiter" button to be clickable and click it using JavaScript
        weiter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@class="WEB_APPOINT_FORWARDBUTTON"]'))
        )
        print("Weiter button found and clickable")
        driver.execute_script("arguments[0].click();", weiter_button)
        print("Weiter button clicked using JavaScript")
    except Exception as e:
        print(f"Error clicking Weiter button: {e}")
        driver.quit()
        return False

    try:
        # Wait longer for the calendar page to load
        calendar_table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'nat_calendar'))
        )
        print("Calendar page loaded")

        # Extra wait to make sure all elements are fully loaded
        time.sleep(5)
    except Exception as e:
        print(f"Error loading calendar page: {e}")
        driver.save_screenshot('error_screenshot_calendar.png')
        print("Screenshot taken of calendar loading issue")
        driver.quit()
        return False

    try:
        # Check for available appointments
        available_dates = driver.find_elements(By.CLASS_NAME, 'nat_calendar')

        if available_dates:
            termin_frei = driver.find_elements(By.CLASS_NAME, 'termin-frei')
            if termin_frei:
                print("Appointment available!")
                termin_frei[0].click()  # Click on the first available date
                print("Clicked on an available date")
                driver.quit()
                return True
            else:
                print("No appointment available.")
                driver.quit()
                return False
        else:
            print("Calendar loaded but no available dates found.")
            driver.quit()
            return False
    except Exception as e:
        print(f"Error checking for available appointments: {e}")
        driver.quit()
        return False

def notify():
    if check_appointment():
        print("Notification sent.")

schedule.every(1).seconds.do(notify)

while True:
    schedule.run_pending()
    time.sleep(1)
