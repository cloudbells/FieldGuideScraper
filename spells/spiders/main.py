# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

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
                (By.XPATH, "//button[contains(text(), 'Got It!')]")
            )
        )
        if foundFirstBtn:
            firstBtn = self.driver.find_element_by_xpath(
                "//button[contains(text(), 'Got It!')]"
            )
            firstBtn.click()
            time.sleep(3) # Needed because the second button scrolls up from bottom so Selenium can't "scroll to it".
            foundSecondBtn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[contains(text(), 'Continue Using Site')]")
                )
            )
            if foundSecondBtn:
                secondBtn = self.driver.find_element_by_xpath(
                    "//button[contains(text(), 'Continue Using Site')]"
                )
                secondBtn.click()
                spells = self.driver.find_elements_by_xpath(
                    "//a[@class='listview-cleartext']"
                )
                for spell in spells:
                    print(spell.get_attribute("href"))
                    self.spell_urls.append(spell.get_attribute("href"))