from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import uuid
import random
import imaplib
import email
import re
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException


GMAIL_USER = "testingacct404@gmail.com"
GMAIL_PASSWORD = ""     #16 letter App Password that I set for Mail

unique_suffix = uuid.uuid4().hex[:6]
test_email = f"testingacct404+{unique_suffix}@gmail.com"
test_password = "Nischal123$"

def generate_random_phone():
    restricted_prefixes = ['984', '985', '986', '976', '974', '975', '980', '981', '982', '970']
    while True:
        first_digit = '9'
        remaining = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        number = first_digit + remaining
        if not any(number.startswith(p) for p in restricted_prefixes):
            return int(number)

phone_number = generate_random_phone()

def human_typing(element, text):
    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(0.02, 0.04))

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://authorized-partner.netlify.app/login")
driver.maximize_window()
wait = WebDriverWait(driver, 15)
time.sleep(2)

try:
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign Up"))).click()
    print("Sign Up Link Clicked.")
except Exception as e:
    print(f"Error clicking Sign Up link: {e}")
time.sleep(random.uniform(1.5, 2.5))

try:
    wait.until(EC.element_to_be_clickable((By.ID, "remember"))).click()
    print("Checkbox Clicked.")
except Exception as e:
    print(f"Checkbox not found. {e}")
time.sleep(random.uniform(1, 1.5))

try:
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))).click()
    print("Continue Button Clicked.")
except Exception as e:
    print(f"Continue button not found. {e}")
time.sleep(random.uniform(2, 3))

try:
    human_typing(driver.find_element(By.NAME, "firstName"), "Nischal")
    time.sleep(random.uniform(0.5, 1))
    human_typing(driver.find_element(By.NAME, "lastName"), "Kunwar")
    time.sleep(random.uniform(0.5, 1))
    human_typing(driver.find_element(By.NAME, "email"), test_email)
    time.sleep(random.uniform(0.5, 1))
    human_typing(driver.find_element(By.NAME, "phoneNumber"), str(phone_number))
    time.sleep(random.uniform(0.5, 1))
    human_typing(driver.find_element(By.NAME, "password"), test_password)
    time.sleep(random.uniform(0.5, 1))
    human_typing(driver.find_element(By.NAME, "confirmPassword"), test_password)
    time.sleep(random.uniform(0.5, 1))
    print(f"Form Filled Successfully with phone number: {phone_number}")

    for btn in driver.find_elements(By.XPATH, "//button[@type='button' and contains(@class, 'eye')]"):
        btn.click()
        time.sleep(random.uniform(0.3, 0.6))
    print("Password visibility toggled.")

    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))).click()
    print("Next Button Clicked.")
    time.sleep(random.uniform(1, 1.5))

except Exception as e:
    print(f"Error filling the form: {e}")

otp_trigger_time = datetime.now()

def fetch_otp_from_gmail(timeout_seconds=60, poll_interval=5):
    otp_re = re.compile(r'\b\d{6}\b')
    end_time = datetime.now() + timedelta(seconds=timeout_seconds)
    while datetime.now() < end_time:
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GMAIL_USER, GMAIL_PASSWORD)
            mail.select('inbox')
            status, data = mail.search(None, 'UNSEEN')
            if status != 'OK':
                mail.logout()
                time.sleep(poll_interval)
                continue
            ids = data[0].split()
            for email_id in reversed(ids):
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                date_tuple = email.utils.parsedate_tz(msg['Date'])
                msg_time = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                if msg_time < otp_trigger_time:
                    continue

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        disp = str(part.get('Content-Disposition'))
                        if ctype == 'text/plain' and 'attachment' not in disp:
                            body = part.get_payload(decode=True).decode(errors='ignore')
                            break
                        elif ctype == 'text/html' and 'attachment' not in disp and not body:
                            body = part.get_payload(decode=True).decode(errors='ignore')
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')

                if body:
                    match = otp_re.search(body)
                    if match:
                        code = match.group(0)
                        try:
                            mail.store(email_id, '+FLAGS', '\\Seen')
                        except:
                            pass
                        mail.logout()
                        print(f"OTP found: {code}")
                        return code
            mail.logout()
        except Exception as e:
            print(f"Error accessing Gmail: {e}")
        time.sleep(poll_interval)
    print("Timeout reached. OTP not found.")
    return None

print("Waiting for OTP in Gmail...")
otp_code = fetch_otp_from_gmail(timeout_seconds=60, poll_interval=5)

if otp_code:
    try:
        otp_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-input-otp='true']")))
        otp_input.clear()
        time.sleep(0.5)
        human_typing(otp_input, otp_code)
        print("OTP entered in the input field.")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Verify')]"))).click()
        print("Verify Button Clicked.")
        time.sleep(random.uniform(1, 1.5))
    except Exception as e:
        print(f"Error entering OTP: {e}")
else:
    print("Failed to retrieve OTP from Gmail.")

try:
    human_typing(wait.until(EC.presence_of_element_located((By.NAME, "agency_name"))), "Kunwar Global Education")
    time.sleep(random.uniform(0.5, 1))
    human_typing(wait.until(EC.presence_of_element_located((By.NAME, "role_in_agency"))), "Founder")
    time.sleep(random.uniform(0.5, 1))
    human_typing(wait.until(EC.presence_of_element_located((By.NAME, "agency_email"))),
                 f"testingacct404+agency{unique_suffix}@gmail.com")
    time.sleep(random.uniform(0.5, 1))
    human_typing(wait.until(EC.presence_of_element_located((By.NAME, "agency_website"))), "www.kunwarglobaledu.com")
    time.sleep(random.uniform(0.5, 1))
    human_typing(wait.until(EC.presence_of_element_located((By.NAME, "agency_address"))), "Basundhara, Kathmandu")
    time.sleep(random.uniform(0.5, 1))
   
    region_dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']")))
    region_dropdown_btn.click()
    time.sleep(random.uniform(0.8, 1.2))

    
    dropdown_options = wait.until(EC.visibility_of_all_elements_located(
        (By.XPATH, "//div[contains(@class,'min-h') or contains(@class,'item') or @role='option']")))

    selected = False
    for option in dropdown_options:
        if "Nepal" in option.text:
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            time.sleep(0.3)
            option.click()
            selected = True
            print("Region 'Nepal' selected successfully.")
            break

    if not selected:
        print("Nepal option not found in dropdown.")
        
    
    time.sleep(random.uniform(0.8, 1.2))
    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]")))
    next_btn.click()
    print("Next Button Clicked after selecting Nepal.")
    time.sleep(random.uniform(1.0, 1.5))

except Exception as e:
    print(f"Error filling Agency Details: {e}")

def human_typing(element, text, delay_range=(0.05, 0.15)):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

try:
    print("Waiting for Step 3 to load...")
    time.sleep(random.uniform(1.0, 1.5))

    step3_heading = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Professional Experience')]"))
    )
    print("Step 3 is active and loaded.")

    retries = 3
    for attempt in range(retries):
        try:
            exp_dropdown_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", exp_dropdown_btn)
            time.sleep(random.uniform(0.3, 0.6))
            exp_dropdown_btn.click()
            time.sleep(random.uniform(0.8, 1.2))
            first_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='option' or self::option][1]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", first_option)
            time.sleep(random.uniform(0.3, 0.6))
            first_option.click()
            print("Experience Level option selected.")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to select dropdown option: {e}")
            time.sleep(1)
    else:
        print("Failed to select Experience Level after retries.")

    time.sleep(random.uniform(0.8, 1.2))

    students_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "number_of_students_recruited_annually"))
    )
    human_typing(students_input, "78")
    print("Entered number of students recruited annually.")
    time.sleep(random.uniform(0.5, 1.0))

    focus_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "focus_area"))
    )
    human_typing(focus_input, "Under Grad admissions to Australia")
    print("Entered focus area.")
    time.sleep(random.uniform(0.5, 1.0))

    success_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "success_metrics"))
    )
    human_typing(success_input, "92")
    print("Entered success metrics.")
    time.sleep(random.uniform(0.5, 1.0))

    service_labels = ["Career Counseling", "Admission Applications", "Visa Processing", "Test Prepration"]
    for label in service_labels:
        try:
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//label[contains(text(),'{label}')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
            time.sleep(random.uniform(0.3, 0.6))
            checkbox.click()
            print(f"Selected service: {label}")
        except Exception as ce:
            print(f"Could not find checkbox for {label}: {ce}")

    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Next')]"))
    )
    time.sleep(random.uniform(0.8, 1.2))
    next_btn.click()
    print("Next Button Clicked on Step 3. Proceeding to Step 4.")
    time.sleep(2)  

    print("Waiting for Step 4 to fully load...")
    step4_heading = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h3[contains(text(),'Provide Business Details and Set Preferences')]")
        )
    )
    time.sleep(random.uniform(1.5, 2.5))

    reg_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "business_registration_number"))
    )
    human_typing(reg_input, "BRN-123456")
    print("Entered Business Registration Number.")

    country_dropdown_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", country_dropdown_btn)
    time.sleep(random.uniform(0.3, 0.6))
    country_dropdown_btn.click()
    time.sleep(random.uniform(0.5, 1.0))

    first_country_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='flex cursor-pointer items-center justify-between p-2 space-y-1 hover:bg-accent'][1]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", first_country_option)
    time.sleep(random.uniform(0.3, 0.6))
    first_country_option.click()
    print("Selected 'Australia' as Preferred Country.")
    time.sleep(random.uniform(1.0, 1.5))

    checkboxes = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//button[@role='checkbox']"))
    )
    for i, cb in enumerate(checkboxes[:2]):
        driver.execute_script("arguments[0].scrollIntoView(true);", cb)
        driver.execute_script("arguments[0].click();", cb)
        print(f"Selected checkbox {i+1}")
        time.sleep(0.5)

    cert_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "certification_details"))
    )
    human_typing(cert_input, "Nischal Resume")
    print("Entered Certification Details.")

    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
    file_input.send_keys(r"C:\Users\Nischal\Desktop\Nischal_Resume.pdf")
    print("Uploaded business document.")
    time.sleep(random.uniform(1.0, 2.0))  

    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Submit')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    driver.execute_script("arguments[0].click();", submit_btn)
    print("Submit Button Clicked. Step 4 completed successfully.")

except Exception as e:
    print(f"Error in Step 3/4: {e}")

try:
    success_msg = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'successfully submitted')]"))
    )
    print("Form submitted successfully! Success message detected.")
except:
    print("Submit clicked, but no success message detected.")


try:
    dashboard_container = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'dashboard') or contains(@class,'w-full')]"))
    )
    print("Dashboard loaded.")
except:
    print("Dashboard did not load in time, continuing anyway.")

try:
    driver.execute_script("""
        let totalHeight = document.body.scrollHeight;
        let step = 150;
        let delay = 0;
        for(let pos = 0; pos < totalHeight; pos += step){
            setTimeout(()=>{window.scrollTo(0,pos);}, delay);
            delay += 150;
        }
    """)
    time.sleep(1)  
    print("Scrolling completed.")
except Exception as e:
    print(f"Scrolling failed: {e}")


try:
    print("Forcing click on sidebar Logout...")
    footer = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-sidebar='footer']"))
    )
    logout_div = footer.find_element(By.XPATH, ".//div[text()='Logout']")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", logout_div)
    driver.execute_script("arguments[0].click();", logout_div)
    print("Sidebar Footer Logout clicked")

    print("Waiting for popup Logout button...")
    popup_logout = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Logout')]"))
    )
    driver.execute_script("arguments[0].click();", popup_logout)
    print("Popup Logout confirmed.")

    WebDriverWait(driver, 20).until(EC.url_contains("/login"))
    print("Successfully logged out and redirected to /login.")

except Exception as e:
    print(f"Logout flow failed: {e}")
