import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

driver = webdriver.Chrome("C:\dev\Python\chromedriver.exe")
#insert user:password credentials below 
driver.get("http://user:password@192.168.100.2") 

#wait until the fuel level canvas loads
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'tilesCanvas_fuelLevel')))

canvas = driver.find_element_by_id('tilesCanvas_fuelLevel')
canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)

canvas_decoded = base64.b64decode(canvas_base64)

#save canvas to project directory
with open(r"canvas.png", 'wb') as f:
    f.write(canvas_decoded)

canvas_png = Image.open('canvas.png').convert('L')

width, height = canvas_png.size

#coordinates used to cut the fragment with numbers from canvas
left = 150
top = 0
right = 260
bottom = height

croppedCanvas = canvas_png.crop((140, top, right, bottom))
text = pytesseract.image_to_string(croppedCanvas, config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789')
print(text)