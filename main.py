import os
import time
from dotenv import load_dotenv
import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# VM Config Paramters
IMAGE = "CC Template"
FLAVOR = "g.medium"
NETWORK = "vlan9"



XPATH_SIGN_IN_OPEN_STACK_BTN = "//span[normalize-space()='Sign In']"
XPATH_OPEN_STACK_PROJECT_INSTANCES_TAB = "//a[normalize-space()='Instances']"
XPATH_OPEN_STACK_CONTEXT_PROJECT = "//span[@class='context-project']"

# Source TAB
XPATH_LAUNCH_INSTANCE_SOURCE_TAB_BTN = "//div[@class='col-xs-12 col-sm-3 wizard-navigation']//li[2]//a[1]"
XPATH_LAUNCH_INSTANCE_SEARCH_SOURCE_IMAGE_TXT_BOX = "//hz-dynamic-table[contains(@items, 'sourceItems')]//input[@placeholder='Click here for filters or full text search.']"
XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_SOURCE_IMAGE_BTN = "/html[1]/body[1]/div[1]/div[1]/div[1]/wizard[1]/div[1]/div[2]/div[2]/div[2]/div[2]/ng-include[1]/div[1]/div[1]/transfer-table[1]/div[1]/div[2]/div[2]/hz-dynamic-table[1]/hz-magic-search-context[1]/div[1]/table[1]/tbody[1]/tr[1]/td[8]/actions[1]/action-list[1]/button[1]"

# Flavor TAB
XPATH_LAUNCH_INSTANCE_FLAVOR_TAB_BTN = "//div[@class='col-xs-12 col-sm-3 wizard-navigation']//li[3]//a[1]"
XPATH_LAUNCH_INSTANCE_SEARCH_FLAVOR_TXT_BOX = "//hz-dynamic-table[@name='allocated-flavor']//input[@placeholder='Click here for filters or full text search.']"
XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_FLAVOR_BTN = "//tbody/tr[@class='ng-scope']/td[10]/actions[1]/action-list[1]/button[1]"


# Networks TAB
XPATH_LAUNCH_INSTANCE_NETWORKS_TAB_BTN = "//span[normalize-space()='Networks']"
# Nu am putut gasi un XPATH care sa functioneze pentru bara de search
# Upload vlan9
XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_NETWORK_BTN = "/html[1]/body[1]/div[1]/div[1]/div[1]/wizard[1]/div[1]/div[2]/div[2]/div[2]/div[4]/ng-include[1]/div[1]/transfer-table[1]/div[1]/div[2]/div[2]/hz-dynamic-table[1]/hz-magic-search-context[1]/div[1]/table[1]/tbody[1]/tr[1]/td[8]/actions[1]/action-list[1]/button[1]"

XPATH_LAUNCH_INSTANCE_BTN = "//button[contains(@class, 'btn-primary') and contains(., 'Launch Instance')]"




class SeleniumWebApp():
    def __init__(self, driver):
        self.driver = driver

    
    def enable_visual_click(self):
        js_code = """
        document.addEventListener('click', function(e) {
            var circle = document.createElement('div');
            circle.setAttribute('style', 'position: absolute; width: 25px; height: 25px; border-radius: 50%; background: rgba(0, 255, 0, 0.5); border: 2px solid white; pointer-events: none; z-index: 10000; left: ' + (e.pageX - 12.5) + 'px; top: ' + (e.pageY - 12.5) + 'px;');
            document.body.appendChild(circle);
            setTimeout(function() { circle.remove(); }, 600);
        }, true);
        """
        self.driver.execute_script(js_code)

    
    def type_in_textbox(self, wait, by, locator, text):
        element = wait.until(EC.visibility_of_element_located((by, locator)))
        element.clear()
        element.send_keys(text)



    def click_on(self, wait, by, locator):
        element = wait.until(EC.element_to_be_clickable((by, locator)))
        element.click()


def main():
    # Bring all environment variables from .env
    load_dotenv()


    MODDLE_USERNAME = os.getenv('MODDLE_USERNAME')
    MODDLE_PASSWORD = os.getenv('MODDLE_PASSWORD')


    if not MODDLE_USERNAME or not MODDLE_PASSWORD:
        print("Seteaza MODDLE_USERNAME si MODDLE_PASSWORD in environment!")
        sys.exit(1)

    INSTANCE_NAME = f"cc_lab_{MODDLE_USERNAME}"


    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    wait = WebDriverWait(driver, 15)

    selenium_webapp = SeleniumWebApp(driver)


    try:
        # --- LOGIN ---
        driver.get("https://cloud.grid.pub.ro/auth/login/?next=/project/instances/")
        driver.maximize_window()
        selenium_webapp.enable_visual_click()

        selenium_webapp.click_on(wait, By.XPATH, XPATH_SIGN_IN_OPEN_STACK_BTN)
        selenium_webapp.type_in_textbox(wait, By.ID, "username", MODDLE_USERNAME)
        selenium_webapp.type_in_textbox(wait, By.ID, "password", MODDLE_PASSWORD)
        selenium_webapp.click_on(wait, By.ID, "kc-login")

        # --- AUTH & PROJECT ---
        print("[OTP] Te rog introdu codul manual.")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "context-project")))
        selenium_webapp.enable_visual_click()
        
        # Pas 8 & 9 din log-ul tau: Selectare Proiect
        selenium_webapp.click_on(wait, By.XPATH, XPATH_OPEN_STACK_CONTEXT_PROJECT)
        
        # Pas 10: Instances
        selenium_webapp.click_on(wait, By.XPATH, XPATH_OPEN_STACK_PROJECT_INSTANCES_TAB)

        # --- LANSARE VM ---
        # Pas 11: Launch Instance
        selenium_webapp.click_on(wait, By.ID, "instances__action_launch-ng")

        # Pas 12: Name
        selenium_webapp.type_in_textbox(wait, By.ID, "name", INSTANCE_NAME)

        # Pas 13: Tab Source
        selenium_webapp.click_on(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_SOURCE_TAB_BTN)

        # Pas 14 & 15: Search Source
        # Am curatat XPath-ul tau pentru a fi mai stabil
        selenium_webapp.type_in_textbox(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_SEARCH_SOURCE_IMAGE_TXT_BOX, IMAGE)
        time.sleep(2)

        # Pas 16: Add Icon
        # Am scos 'ng-leave-prepare' care e instabila
        selenium_webapp.click_on(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_SOURCE_IMAGE_BTN)

        # Pas 17 & 18: Tab Flavor & Search
        selenium_webapp.click_on(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_FLAVOR_TAB_BTN)
        selenium_webapp.type_in_textbox(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_SEARCH_FLAVOR_TXT_BOX, FLAVOR)
        time.sleep(2)

        # Pas 19: Add Icon Flavor
        selenium_webapp.click_on(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_FLAVOR_BTN)

        # Pas 20 & 21: Networks
        selenium_webapp.click_on(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_NETWORKS_TAB_BTN)
        time.sleep(2)
        selenium_webapp.click_on(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_NETWORK_BTN)

        # Pas 23: Final Launch
        selenium_webapp.click_on(wait, By.XPATH, XPATH_LAUNCH_INSTANCE_BTN)

        print("\n[FINISH] Scriptul a fost executat complet.")

    except Exception as err:
        print(f"\n[EROARE NEASTEPTATA] {err}")
        raise err
    finally:
        input("\nApasa Enter pentru inchidere...")
        driver.quit()

if __name__ == "__main__":
    main()

