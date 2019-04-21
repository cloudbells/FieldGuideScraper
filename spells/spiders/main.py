import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

#TODO: FORMAT OUTPUT------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MainSpider(scrapy.Spider):
    name = 'main'
    start_urls = ['http://classic.wowhead.com/abilities/class:8/']
    spell_urls = []

    def parse(self, response):
        options = Options()
        options.add_argument("--headless")
        _browser_profile = webdriver.FirefoxProfile()
        _browser_profile.set_preference("dom.webnotifications.enabled", False)
        self.driver = webdriver.Firefox(firefox_profile=_browser_profile, executable_path='geckodriver.exe', firefox_options=options)
        self.driver.get(response.url)
        foundFirstBtn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//button[contains(text(), 'Continue Using Site')]")
            )
        )
        if foundFirstBtn:
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
                time.sleep(3) # Needed because the second button scrolls up from bottom so Selenium can't "scroll to it".
                secondBtn = self.driver.find_element_by_xpath(
                    "//button[contains(text(), 'Got It!')]"
                )
                secondBtn.click()
                spells = self.driver.find_elements_by_xpath(
                    "//a[@class='listview-cleartext']"
                )
                lastSpell = self.driver.find_element_by_xpath(
                    "//a[@class='listview-cleartext q1']"
                )
                for spell in spells:
                    self.spell_urls.append(str(spell.get_attribute("href")))
                self.spell_urls.append(str(lastSpell.get_attribute("href")))
        if len(self.spell_urls) != 0:
            with open("test.txt", 'a', encoding='utf8') as f:
                f.write("FieldGuideMageSpells = {\n"
                for spell in self.spell_urls:
                    self.driver.get(spell)
                    # Get name.
                    nameText = self.driver.find_element_by_xpath(
                        "//h1[@class='heading-size-1']"
                    ).text
                    # Get level.
                    levelText = self.driver.find_element_by_xpath(
                        "//div[contains(text(), 'Level:')] | //div[contains(text(), 'Requires level')]"
                    ).text
                    # Get rank.
                    rankText = self.driver.find_element_by_xpath(
                        "//b[@class='q0']"
                    ).text
                    # Get texture.
                    textureText = self.driver.find_element_by_xpath(
                        "//span[@class='iconsmall']/.."
                    ).text
                    # Get spell ID (which is part of the URL, so slice it).
                    id = spell[34:]
                    # Conditionally slice level text (any level < 10 should only slice -1).
                    levelText = levelText[-2:] if " " not in levelText[-2:] else levelText[-1]
                    # Conditionally slice rank text (if rank > 10 then we need the last two, otherwise only last 1).
                    rankText = rankText[-2:] if len(rankText) > 6 else rankText[-1]
                # close root table \n}
            f.close()
        self.driver.close()