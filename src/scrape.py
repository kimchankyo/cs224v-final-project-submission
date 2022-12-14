import selenium.webdriver as wd
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import List, Tuple, Dict
from tqdm import tqdm
import time
import json
import warnings
warnings.filterwarnings("ignore")


# NOTE: Change the following lines depending on your machine
# Linux Chrome Executable Path
CHROME_EXECUTABLE_PATH = "/usr/bin/google-chrome-stable"    # This may be different depending on your machine
CHROME_DRIVER_PATH = "/usr/bin/chromedriver"                # This may be different depending on your machine

# MacOS Chrome Executable Path
# CHROME_EXECUTABLE_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# CHROME_DRIVER_PATH = "/opt/homebrew/bin/chromedriver"


def startChromeDriver() -> wd.Chrome:
  executablePath = CHROME_EXECUTABLE_PATH
  driverPath = CHROME_DRIVER_PATH
  
  # Create Browser Options
  options = wd.ChromeOptions()
  options.binary_location = executablePath
  
  # Create Browser Driver
  return wd.Chrome(executable_path=driverPath, chrome_options=options)


def checkElementExists(node: WebElement, xpath: str) -> Tuple[bool, WebElement]:
  try:
    elem = node.find_element(By.XPATH, xpath)
    return True, elem
  except:
    return False, None


def checkElementsExist(node: WebElement, xpath: str) -> Tuple[bool, List[WebElement]]:
  try:
    elems = node.find_elements(By.XPATH, xpath)
    return True, elems
  except:
    return False, None


def waitForElement(node: WebElement, xpath: str, nolimit: bool = True, 
                   iters: int = 10, interval: float = 0.1) -> Tuple[bool, WebElement]:
  if nolimit:
    for _ in range(iters):
      time.sleep(interval)
      ret, elem = checkElementExists(node, xpath)
      if ret: return ret, elem
    return False, None
  else:
    time.sleep(interval)
    ret, elem = checkElementExists(node, xpath)
    while not ret:
      time.sleep(interval)
      ret, elem = checkElementExists(node, xpath)
    return ret, elem


def waitForElements(node: WebElement, xpath: str, nolimit: bool = True, 
                    iters: int = 10, interval: float = 0.1) -> Tuple[bool, List[WebElement]]:
  if nolimit:
    for _ in range(iters):
      time.sleep(interval)
      ret, elems = checkElementsExist(node, xpath)
      if ret: return ret, elems
    return False, None
  else:
    time.sleep(interval)
    ret, elems = checkElementsExist(node, xpath)
    while not ret:
      time.sleep(interval)
      ret, elems = checkElementsExist(node, xpath)
    return ret, elems


def scrollToBottom(driver: wd.Chrome) -> None:
  total_height = int(driver.execute_script("return document.body.scrollHeight"))

  for i in range(1, total_height, 5):
      driver.execute_script("window.scrollTo(0, {});".format(i))


STRING_REPLACEMENTS = {
  "&amp;": "and",
  "\u2019": "'",
  "\u2013": ","
}


def cleanString(string: str) -> str:
  for key, val in STRING_REPLACEMENTS.items():
    string = string.replace(key, val)
  return string.strip().lower()


def removeSubstrings(string: str, items: List[str]) -> str:
  for item in items:
    string = string.replace(item, "")
  return string


def getItemInformation(driver: wd.Chrome, href: str) -> Dict:
  # Open Link to Item
  driver.get(href)

  # Determine Item Category
  categories = waitForElements(driver, ".//li[contains(@class, 'bc-breadcrumb__list-item')]")[1]
  category = "n/a"
  if len(categories) > 1:
    category = waitForElement(categories[1], ".//span")[1].get_attribute("innerHTML")
  category = cleanString(category)
  
  # Determine Item Price
  priceInt = float(waitForElement(driver, ".//span[contains(@class, 'pip-temp-price__integer')]")[1].text.replace(",", ""))
  priceDec = float(waitForElement(driver, ".//span[contains(@class, 'pip-temp-price__decimal')]")[1].text)
  price = priceInt + priceDec

  # Determine Item Name
  name = waitForElement(driver, ".//span[contains(@class, 'pip-header-section__title')]")[1].text

  # Determine Item Description
  description = waitForElement(driver, ".//span[contains(@class, 'pip-header-section__description-text')]")[1].text

  # Determine Item Rating
  review = waitForElement(driver, ".//button[contains(@class, 'pip-temp-price-module__ratings')]")[1].get_attribute("aria-label")
  rating, _, numReviews = [float(num) for num in removeSubstrings(review, ["Review:", "out of", "stars. Total reviews:"]).split()]
  numReviews = int(numReviews)

  # Determine Item Article Number
  identifier = waitForElement(driver, ".//span[contains(@class, 'pip-product-identifier__value')]")[1].text
  
  # Construct Item Database Description
  listing = "{}\tPrice: ${:.2f}\tRating: {:.1f}/5.0\tNumber of Reviews: {}\tArticle Number: [{}]\tDescription: {}".format(name, price, rating, numReviews, identifier, description)

  itemObj = {
    "name": name,
    "category": category,
    "price": price,
    "rating": rating,
    "numReviews": numReviews,
    "identifier": identifier,
    "description": description,
    "listing": listing
  }

  return itemObj


def getTemplateItemInformation(driver: wd.Chrome, href: str) -> Dict:
  # Open Template Link
  print("Collecting Item Information From: {}".format(href))
  driver.get(href)
  scrollToBottom(driver)  # Load Page

  # Find Listing Items
  _, items = waitForElements(driver, ".//a[contains(@class, 'pub__shoppable-image__dot')]")
  itemLinks = [item.get_attribute("href") for item in items]

  # Items
  itemCollection = {}
  for itemLink in tqdm(itemLinks):
    try:
      itemObj = getItemInformation(driver, itemLink)
      itemList = itemCollection.get(itemObj.get("category"), [])
      itemList.append(itemObj)
      itemCollection[itemObj.get("category")] = itemList
    except:
      continue
  return itemCollection


def getTemplateDescription(driver: wd.Chrome, href: str) -> str:
  driver.get(href)
  title = waitForElement(driver, ".//h1[contains(@class, 'c1m1sl8e pub__h1 s1gshh7t')]")[1].text
  description = waitForElement(driver, ".//div[contains(@class, 'cpnz0ke')]")[1].text
  return cleanString("{}. {}".format(title, description.strip()))


def getTemplatesInformation(driver: wd.Chrome, href: str, code: str) -> List:
  # Open Templates List for Category
  driver.get(href)

  # Find Template List
  templateListing = waitForElement(driver, ".//div[contains(@data-pub-type, 'page-list')]")[1]
  templates = waitForElements(templateListing, ".//a[contains(@class, 'pub__card')]")[1]
  templateLinks = [template.get_attribute("href") for template in templates]

  templateList = []
  for i in range(len(templateLinks)):
    templateCode = "{}{}".format(code, i)
    templateLink = templateLinks[i]
    templateItems = getTemplateItemInformation(driver, templateLink)
    templateDescription = getTemplateDescription(driver, templateLink)
    templateList.append((templateCode, templateItems, templateDescription))

  return templateList


if __name__ == "__main__":
  galleries = {
    "bedroom": {"code": "b", "link": "https://www.ikea.com/us/en/rooms/bedroom/gallery"},
    "living": {"code": "l", "link": "https://www.ikea.com/us/en/rooms/living-room/gallery"},
    "kitchen": {"code": "k", "link": "https://www.ikea.com/us/en/rooms/kitchen/gallery"},
    "office": {"code": "o", "link": "https://www.ikea.com/us/en/rooms/home-office/gallery"},
    "bathroom": {"code": "r", "link": "https://www.ikea.com/us/en/rooms/bathroom/gallery"},
    "children": {"code": "c", "link": "https://www.ikea.com/us/en/rooms/childrens-room/gallery"},
    "dining": {"code": "d", "link": "https://www.ikea.com/us/en/rooms/dining/gallery"},
    "outdoor": {"code": "u", "link": "https://www.ikea.com/us/en/rooms/outdoor/gallery"},
    "hallway": {"code": "h", "link": "https://www.ikea.com/us/en/rooms/hallway/gallery"}
  }

  driver = startChromeDriver()

  templates = {}
  products = {}

  for room, obj in galleries.items():
    roomDescriptions = []
    for code, items, description in getTemplatesInformation(driver, obj.get("link"), obj.get("code")):
      roomDescriptions.append({"code": code, "description": description})
      products[code] = items
    templates[room] = roomDescriptions

  with open("data/templates.json", "w") as f:
    json.dump(templates, f, indent=2)

  with open("data/products.json", "w") as f:
    json.dump(products, f, indent=2)