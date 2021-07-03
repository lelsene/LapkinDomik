from time import sleep

from django.test import TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from LapkinDomik.settings import CHROME_DRIVER


class OwnerTest(TestCase):
    def setUp(self):
        self.url = 'http://127.0.0.1:8000'
        self.driver = webdriver.Chrome(CHROME_DRIVER)
        self.login_url = self.url + reverse('login')
        self.registration_url = self.url + reverse('registration')
        self.logout_url = self.url + reverse('logout')
        self.profile_url = self.url + reverse('profile')
        self.sitters_url = self.url + reverse('sitters')
        self.applications_url = self.url + reverse('retreat_applications')

    def tearDown(self):
        self.driver.quit()

    def test_chain(self):
        self.driver.get(self.registration_url)
        self.driver.find_element(By.NAME, "Email").send_keys("test@test.com")
        self.driver.find_element(By.NAME, "Password").send_keys("123")
        self.driver.find_element(By.TAG_NAME, "button").send_keys(Keys.ENTER)
        sleep(0.5)

        if self.driver.current_url != self.url + reverse('profile'):
            self.driver.find_element(By.LINK_TEXT, "Войти").send_keys(Keys.ENTER)
            sleep(0.5)
            self.assertEqual(self.driver.current_url, self.login_url)
            self.driver.find_element(By.NAME, "Email").send_keys("test@test.com")
            self.driver.find_element(By.NAME, "Password").send_keys("123")
            self.driver.find_element(By.TAG_NAME, "button").send_keys(Keys.ENTER)
            sleep(0.5)
        self.assertEqual(self.driver.current_url, self.profile_url)

        name = self.driver.find_element(By.NAME, "name")
        if name.get_attribute('value') == "":
            self.driver.find_element(By.NAME, "name").send_keys("TestName")
            self.driver.find_element(By.NAME, "surname").send_keys("TestSurname")
            Select(self.driver.find_element_by_name('sex')).select_by_visible_text("Женский")
            self.driver.find_element_by_name('birthday').send_keys("27.10.1998")
            Select(self.driver.find_element_by_name('city')).select_by_visible_text("Ульяновск")
            self.driver.find_element_by_name('phone').send_keys("+7(900)-123-45-67")
            self.driver.find_element_by_name("profileSave").send_keys(Keys.ENTER)
            sleep(0.5)
            self.assertEqual(self.driver.find_element(By.NAME, "name").get_attribute('value'), "TestName")

        pets = self.driver.find_elements(By.CLASS_NAME, "col")
        if len(pets) == 0:
            self.driver.find_element_by_name("petAdd").send_keys(Keys.ENTER)
            sleep(0.5)
            self.driver.find_element_by_id("petName").send_keys("TestPetName")
            self.driver.find_element_by_id("petAge").send_keys(2)
            Select(self.driver.find_element_by_id('petSex')).select_by_visible_text("Женский")
            Select(self.driver.find_element_by_id('petType')).select_by_visible_text("Паук")
            self.driver.find_element_by_name("petSave").send_keys(Keys.ENTER)
            sleep(0.5)
            self.assertEqual(self.driver.find_element(By.ID, "petName").get_attribute('value'), "TestPetName")

        menu = self.driver.find_element(By.LINK_TEXT, "Найти ситтера")
        self.driver.get(menu.get_attribute('href'))
        sleep(0.5)

        self.assertEqual(self.driver.current_url, self.sitters_url)
        Select(self.driver.find_element_by_name('petTypes')).select_by_visible_text("Паук")
        self.driver.find_element_by_name("apply").send_keys(Keys.ENTER)
        sleep(0.5)

        application = self.driver.find_element_by_class_name("card-body")
        self.assertTrue('Паук' in application.text)

        self.driver.find_element_by_name('createApplication').send_keys(Keys.ENTER)
        sleep(0.5)

        self.driver.find_element_by_name('dateFrom').send_keys("20.12.2020")
        self.driver.find_element_by_name('dateTo').send_keys("22.12.2020")
        Select(self.driver.find_element_by_name('pets')).select_by_index(0)
        self.driver.find_element_by_name('refresh').send_keys(Keys.ENTER)
        price = self.driver.find_element_by_name("price").get_attribute('value')
        sleep(0.5)

        self.driver.find_element_by_name('createApplication').send_keys(Keys.ENTER)
        sleep(0.5)
        self.assertEqual(self.driver.current_url, self.applications_url)

        application = self.driver.find_element_by_class_name("list-group-item")
        self.assertTrue(price in application.text)
