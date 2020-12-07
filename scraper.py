import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
from PIL import Image
import PIL.ImageOps
from twilio.rest import Client
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

chrome_options = webdriver.ChromeOptions()
chrome_options.headless = True

driver = webdriver.Chrome(executable_path = "C:\dev\Python\chromedriver.exe", options = chrome_options)
#insert user:password credentials below 
driver.get("http://user:password@192.168.100.2") 

#wait until the fuel level canvas loads
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tilesCanvas_fuelLevel')))

canvas = driver.find_element_by_id('tilesCanvas_fuelLevel')
canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)

driver.quit()

canvas_decoded = base64.b64decode(canvas_base64)

#save canvas to project directory
with open(r"canvas.png", 'wb') as f:
    f.write(canvas_decoded)

canvas_png = Image.open('canvas.png').convert('L')

width, height = canvas_png.size

#coordinates used to cut the fragment with numbers from canvas
left = 120
top = 50
right = 260
bottom = 130

croppedCanvas = canvas_png.crop((left, top, right, bottom))
croppedInverted = PIL.ImageOps.invert(croppedCanvas)

level = pytesseract.image_to_string(croppedInverted, config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')

#getting just the first line of str level. For whatever reason pytesseract sometimes adds '/n' to the numbers
level.split('\n', 1)[0]

status = ' W porządku'

if int(level) <= 20:
    status = ' ALARM'
    message = "ALARM \nKończy się pellet\nPoziom paliwa: {}%!".format(int(level))
    client = Client("ACCOUNTSID", "AUTHTOKEN")
    client.messages.create(to="RECIPIENTNUMBER", 
                       from_="SENDERNUMBER", 
                       body=message)

#Logging the fuel level check to a text file
file = open('log.txt', 'a')
timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
logMessage = " Poziom paliwa: {}%".format(int(level)) + status
file.write('\n' + timestamp + logMessage)
file.close()
