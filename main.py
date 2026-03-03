import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager



IMAGE_NAME = "CC Template"
FLAVOR_NAME = "g.medium"
NETWORK_NAME = "vlan9"


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


MODDLE_USERNAME = os.getenv('MODDLE_USERNAME')
MODDLE_PASSWORD = os.getenv('MODDLE_PASSWORD')


INSTANCE_NAME = f"cc_lab_{MODDLE_USERNAME}"

def enable_visual_click(driver):
    js_code = """
    document.addEventListener('click', function(e) {
        var circle = document.createElement('div');
        circle.setAttribute('style', 'position: absolute; width: 25px; height: 25px; border-radius: 50%; background: rgba(0, 255, 0, 0.5); border: 2px solid white; pointer-events: none; z-index: 10000; left: ' + (e.pageX - 12.5) + 'px; top: ' + (e.pageY - 12.5) + 'px;');
        document.body.appendChild(circle);
        setTimeout(function() { circle.remove(); }, 600);
    }, true);
    """
    driver.execute_script(js_code)

def type_text(by, value, text, description):
    try:
        element = wait.until(EC.presence_of_element_located((by, value)))
        element.clear()
        element.send_keys(text)
        print(f"[OK] {description}")
    except TimeoutException:
        fail_fast(f"Nu am găsit câmpul: {description}")

def selenium_action(driver, wait, by, locator, action_type, value=None, step_name=""):
    """Executa o actiune (click sau type) cu timeout de 15 secunde si raportare eroare."""
    try:
        if action_type == "click":
            element = wait.until(EC.element_to_be_clickable((by, locator)))
            element.click()
        elif action_type == "type":
            element = wait.until(EC.visibility_of_element_located((by, locator)))
            element.clear()
            element.send_keys(value)
    except Exception:
        print(f"\n[STOP] Scriptul s-a blocat la pasul: '{step_name}'")
        print(f"[X] Nu am gasit XPath-ul: {locator}")
        driver.quit()
        sys.exit(1)

def run_automation():
    if not MODDLE_USERNAME or not MODDLE_PASSWORD:
        print("Seteaza USERNAME si PASSWORD in environment!")
        return

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    wait = WebDriverWait(driver, 15)

    try:
        # --- LOGIN ---
        driver.get("https://cloud.grid.pub.ro/auth/login/?next=/project/instances/")
        driver.maximize_window()
        enable_visual_click(driver)

        selenium_action(driver, wait, By.XPATH, XPATH_SIGN_IN_OPEN_STACK_BTN, "click", step_name="Click Sign In")
        selenium_action(driver, wait, By.ID, "username", "type", MODDLE_USERNAME, "Type Moddle Username")
        selenium_action(driver, wait, By.ID, "password", "type", MODDLE_PASSWORD, "Type Moddle Password")
        selenium_action(driver, wait, By.ID, "kc-login", "click", step_name="Click Login")

        # --- AUTH & PROJECT ---
        print("[OTP] Te rog introdu codul manual.")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "context-project")))
        enable_visual_click(driver)
        
        # Pas 8 & 9 din log-ul tau: Selectare Proiect
        selenium_action(driver, wait, By.XPATH, XPATH_OPEN_STACK_CONTEXT_PROJECT, "click", step_name="Click Proiect")
        
        # Pas 10: Instances
        selenium_action(driver, wait, By.XPATH, XPATH_OPEN_STACK_PROJECT_INSTANCES_TAB, "click", step_name="Meniu Instances")

        # --- LANSARE VM ---
        # Pas 11: Launch Instance
        selenium_action(driver, wait, By.ID, "instances__action_launch-ng", "click", step_name="Buton Launch")

        # Pas 12: Name
        selenium_action(driver, wait, By.ID, "name", "type", INSTANCE_NAME, "Nume Instanta")

        # Pas 13: Tab Source
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_SOURCE_TAB_BTN, "click", step_name="Tab Source")

        # Pas 14 & 15: Search Source
        # Am curatat XPath-ul tau pentru a fi mai stabil
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_SEARCH_SOURCE_IMAGE_TXT_BOX, "type", "CC Template", "Search Source")
        time.sleep(2) # Timp pentru filtrare

        # Pas 16: Add Icon
        # Am scos 'ng-leave-prepare' care e instabila
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_SOURCE_IMAGE_BTN, "click", step_name="Add 'CC Template'")

        # Pas 17 & 18: Tab Flavor & Search
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_FLAVOR_TAB_BTN, "click", step_name="Tab Flavor")
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_SEARCH_FLAVOR_TXT_BOX, "type", "g.medium", "Search Flavor")
        time.sleep(2)

        # Pas 19: Add Icon Flavor
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_FLAVOR_BTN, "click", step_name="Add g.medium")

        # Pas 20 & 21: Networks
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_NETWORKS_TAB_BTN, "click", step_name="Tab Networks")
        time.sleep(2)
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_UPLOAD_TOPMOST_NETWORK_BTN, "click", step_name="Add vlan9")

        # Pas 23: Final Launch
        selenium_action(driver, wait, By.XPATH, XPATH_LAUNCH_INSTANCE_BTN, "click", step_name="Launch Final")

        print("\n[FINISH] Scriptul a fost executat complet.")

    except Exception as e:
        print(f"\n[EROARE NEASTEPTATA] {e}")
    finally:
        input("\nApasa Enter pentru inchidere...")
        driver.quit()

if __name__ == "__main__":
    run_automation()
