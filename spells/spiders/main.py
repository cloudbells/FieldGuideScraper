import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

# Represents a spell.
class Spell:

    def __init__(self, level, name, rank, texture, id):
        self.level = level
        self.name = name
        self.rank = rank
        self.texture = texture
        self.id = id

class MainSpider(scrapy.Spider):
    name = 'main'
    start_urls = ["http://classic.wowhead.com/abilities/class:8/"]
    spell_urls = []
    spellCollection = []

    def parse(self, response):
        options = Options()
        #options.add_argument("--headless")
        _browser_profile = webdriver.FirefoxProfile()
        _browser_profile.set_preference("dom.webnotifications.enabled", False)
        self.driver = webdriver.Firefox(firefox_profile=_browser_profile, executable_path='geckodriver.exe', firefox_options=options)
        self.driver.get(response.url)
        self.clickCookies()
        self.parsePage()
        self.parseSpells()
        self.writeToFile()
    
     # Finds and clicks all cookies buttons.
    def clickCookies(self):
        foundFirstBtn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//button[contains(text(), 'Continue Using Site')]")
            )
        )
        if foundFirstBtn:
            print("Found first button, sleeping...")
            firstBtn = self.driver.find_element_by_xpath(
                "//button[contains(text(), 'Continue Using Site')]"
            )
            time.sleep(3) # Needed because the second button scrolls up from bottom so Selenium can't "scroll to it".
            firstBtn.click()
            foundSecondBtn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[contains(text(), 'Got It!')]")
                )
            )
            if foundSecondBtn:
                print("Found second button, sleeping...")
                time.sleep(3)
                secondBtn = self.driver.find_element_by_xpath(
                    "//button[contains(text(), 'Got It!')]"
                )
                secondBtn.click()

    # Finds all spells on the current page and puts them in a table.
    def parsePage(self):
        spells = self.driver.find_elements_by_xpath(
            "//a[@class='listview-cleartext'] | //a[@class='listview-cleartext q1']"
        )
        for spell in spells:
            self.spell_urls.append(str(spell.get_attribute("href")))
        self.driver.get("https://classic.wowhead.com/abilities/class:8#100+2+1")
        spells = self.driver.find_elements_by_xpath(
            "//a[@class='listview-cleartext'] | //a[@class='listview-cleartext q1']"
        )
        for spell in spells:
            self.spell_urls.append(str(spell.get_attribute("href")))
    
    def parseSpells(self):
        if len(self.spell_urls) != 0:
            for spell in self.spell_urls:
                self.driver.get(spell)
                print("Getting name of spell...")
                # Get name.
                nameText = self.driver.find_element_by_xpath(
                    "//h1[@class='heading-size-1']"
                ).text
                print("Getting level of spell...")
                # Get level.
                levelText = self.driver.find_element_by_xpath(
                    "//div[contains(text(), 'Level:')] | //div[contains(text(), 'Requires level')]"
                ).text
                print("Getting rank of spell...")
                # Get rank.
                try:
                    rankText = self.driver.find_element_by_xpath(
                        "//b[@class='q0']"
                    ).text
                except NoSuchElementException:
                    rankText = "1" # If no rank on the spell, just put a 1.
                print("Getting texture of spell...")
                # Get texture.
                textureText = self.driver.find_element_by_xpath(
                    "//span[@class='iconsmall']/.."
                ).text
                # Get spell ID (which is part of the URL, so slice it).
                id = spell[34:]
                # Any level < 10 should only slice -1.
                levelText = levelText[-2:] if " " not in levelText[-2:] else levelText[-1]
                # If rank > 10 then we need the last two, otherwise only last 1.
                rankText = rankText[-2:] if len(rankText) > 6 else rankText[-1]
                self.spellCollection.append(Spell(levelText, nameText, rankText, textureText, id))
            self.driver.close()

    # Formats each spell and outputs it to a file.
    def writeToFile(self):
        with open("test.txt", 'a', encoding='utf8') as f:
            print("Outputting to file...")
            f.write("FieldGuideMageSpells = {\n")
            index = 1
            lastLevel = 2
            f.write("\t[" + str(lastLevel) + "] = {\n")
            for spell in self.spellCollection:
                if int(spell.level) > lastLevel:
                    f.write("\t},\n") # Close level table.
                    lastLevel = int(spell.level)
                    f.write("\t[" + str(lastLevel) + "] = {\n") # Open level table.
                    index = 1
                f.write("\t\t[" + str(index) + "] = {\n") # Open spell table.
                f.write("\t\t\t[\"name\"] = \"" + spell.name + "\",\n")
                f.write("\t\t\t[\"rank\"] = " + spell.rank + ",\n")
                f.write("\t\t\t[\"cost\"] = 0,\n")
                f.write("\t\t\t[\"texture\"] = \"Interface/ICONS/" + spell.texture + "\",\n")
                f.write("\t\t\t[\"id\"] = " + spell.id + "\n")
                f.write("\t\t},\n") # Close spell table.
                index += 1
            f.write("\t},\n") # Close last level table.
            f.write("}") # Close root table.
        f.close()