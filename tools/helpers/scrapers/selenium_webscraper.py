# -*- coding: utf-8 -*-
#  open source 2019
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from tools.logger import logger
from selenium import webdriver


class ExampleScraper:

    def __init__(self):
        self._driver: WebDriver
        self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            options = Options()
            options.headless = True
            self._driver = webdriver.Firefox(options=options)
        return self._driver

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def load_url(self, url):
        self._driver.get(url)

    def _do_something(self):
        driver = self.driver
        driver.get('http://codepad.org')

        text_area = driver.find_element_by_id('textarea')
        text_area.send_keys("This text is send using Python code.")
        logger.info(text_area)

    def start(self):
        try:
            self._do_something()
        finally:
            self.close()
