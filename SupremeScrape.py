# This program uses Selenium for web scraping and PyTesseract for captcha solving.
# The default values scrape the data for 1-5 diaries for each year from 2000 to 2020.
# Change the limits as desired, the program should work fine as all types of cases are handled.
# Output file is named "supreme.csv", after the URL of the Supreme Court of India.
#The program creates a single image file called "shot.png" for captcha solving.

import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
import csv

# path to the WebDriver used with Selenium
path_to_chromedriver = 'C:/Users/vishnuch/AppData/Roaming/npm/chromedriver.exe'

# initial year and diary values
year = 2000
diary = 1

# Opening the URL in a Google Chrome window
browser = webdriver.Chrome(executable_path=path_to_chromedriver)
url = 'https://main.sci.gov.in/case-status'
browser.get(url)

# Header for the output CSV file
with open('supreme.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Diary No.', 'Case No.', 'Present/Last Listed On', 'Status/Stage', 'Disp.Type', 'Category', 'Act',
                     'Petitioner(s)', 'Respondent(s)', 'Pet. Advocate(s)', 'Resp. Advocate(s)', 'U/Section'])

# Scraping the data each diary and year
while year <= 2020 and diary <= 5:
    try:
        captcha = browser.find_element_by_id('cap')
        # Taking a screenshot of the captcha element
        captcha.screenshot("shot.png")
        image = Image.open("shot.png")

        # Cropping the screenshot to just the numbers' part
        image_crop = image.crop((260, 0, 325, 38))

        pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
        # Converting Captcha screenshot to string using PyTesseract
        result = pytesseract.image_to_string(image_crop)

        # Because captcha is always 4 numbers in this URL
        captcha_input = browser.find_element_by_name("ansCaptcha")
        captcha_input.send_keys(result[:4])

        # Giving diary number input
        browser.find_element_by_id("CaseDiaryNumber").clear()
        browser.find_element_by_id("CaseDiaryNumber").send_keys(str(diary))

        # Selecting year input
        select_year = Select(browser.find_element_by_id("CaseDiaryYear"))
        select_year.select_by_value(str(year))

        # Clicking submit
        browser.find_element_by_id("getCaseDiary").click()

        # Waiting until the webpage for this specific case loads
        WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "container_cs")))
        table = browser.find_element_by_id("DNdisplay").find_element_by_class_name("container_cs").find_element_by_id(
            "accordion").find_element_by_class_name("panel-default").find_element_by_id(
            "collapse1").find_element_by_class_name("table-responsive").find_element_by_tag_name('table')
        with open('supreme.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            x = []

            # Traversing the table and appending each text to a list
            for row in table.find_elements_by_css_selector('tr'):
                x.append(str(row.find_elements_by_tag_name('td')[1].text).replace('\n', ' '))

            # Writing the text data into CSV file
            writer.writerow(x)

        # Incrementing diary value for next case
        diary += 1

        # For 5 entries in each year. Change the below limit according to the requirement (Desired number of entries per year +1)
        if diary == 6:
            year += 1
            diary = 1

            # Appending an extra blank line after each year's entries
            with open('supreme.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow("\n")

        # Refreshing the page for a new captcha
        browser.refresh()

    # If PyTesseract is unable to decipher the captcha image properly
    except UnexpectedAlertPresentException:

        # Optional error message in the console
        print('Captcha error. Trying again.')

    # Handling "Case not found" case from the URL
    except TimeoutException:
        with open('supreme.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([str(diary)+"/"+str(year),"Case not found"])
        diary += 1
        if diary == 6:
            year += 1
            diary = 1
            with open('supreme.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow("\n")
        browser.refresh()
