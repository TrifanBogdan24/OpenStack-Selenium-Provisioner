import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

USERNAME = os.getenv('MODDLE_USERNAME')
PASSWORD = os.getenv('MODDLE_PASSWORD')

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

def smart_action(driver, wait, by, locator, action_type, value=None, step_name=""):
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
    if not USERNAME or not PASSWORD:
        print("Seteaza USERNAME si PASSWORD in environment!")
        return

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    wait = WebDriverWait(driver, 15)

    try:
        # --- LOGIN ---
        driver.get("https://cloud.grid.pub.ro/auth/login/?next=/project/instances/")
        driver.maximize_window()
        enable_visual_click(driver)

        smart_action(driver, wait, By.XPATH, "//span[normalize-space()='Sign In']", "click", step_name="Click Sign In")
        smart_action(driver, wait, By.ID, "username", "type", USERNAME, "Type Username")
        smart_action(driver, wait, By.ID, "password", "type", PASSWORD, "Type Password")
        smart_action(driver, wait, By.ID, "kc-login", "click", step_name="Click Login")

        # --- AUTH & PROJECT ---
        print("[OTP] Te rog introdu codul manual.")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "context-project")))
        enable_visual_click(driver)
        
        # Pas 8 & 9 din log-ul tau: Selectare Proiect
        smart_action(driver, wait, By.XPATH, "//span[@class='context-project']", "click", step_name="Click Proiect")
        
        # Pas 10: Instances
        smart_action(driver, wait, By.XPATH, "//a[normalize-space()='Instances']", "click", step_name="Meniu Instances")

        # --- LANSARE VM ---
        # Pas 11: Launch Instance
        smart_action(driver, wait, By.ID, "instances__action_launch-ng", "click", step_name="Buton Launch")

        # Pas 12: Name
        smart_action(driver, wait, By.ID, "name", "type", USERNAME, "Nume Instanta")

        # Pas 13: Tab Source
        smart_action(driver, wait, By.XPATH, "//a[contains(text(), 'Source')]", "click", step_name="Tab Source")

        # Pas 14 & 15: Search Source
        # Am curatat XPath-ul tau pentru a fi mai stabil
        source_search_xpath = "//hz-dynamic-table[contains(@items, 'sourceItems')]//input[@placeholder='Click here for filters or full text search.']"
        smart_action(driver, wait, By.XPATH, source_search_xpath, "type", "CC template", "Search Source")
        time.sleep(2) # Timp pentru filtrare

        # Pas 16: Add Icon
        # Am scos 'ng-leave-prepare' care e instabila
        smart_action(driver, wait, By.XPATH, "//tr[contains(., 'CC template')]//button[contains(@class, 'fa-arrow-up')]", "click", step_name="Add CC template")

        # Pas 17 & 18: Tab Flavor & Search
        smart_action(driver, wait, By.XPATH, "//a[contains(text(), 'Flavor')]", "click", step_name="Tab Flavor")
        flavor_search_xpath = "//hz-dynamic-table[@name='allocated-flavor']//input[@placeholder='Click here for filters or full text search.']"
        smart_action(driver, wait, By.XPATH, flavor_search_xpath, "type", "g.medium", "Search Flavor")
        time.sleep(2)

        # Pas 19: Add Icon Flavor
        smart_action(driver, wait, By.XPATH, "//tr[contains(., 'g.medium')]//button[contains(@class, 'fa-arrow-up')]", "click", step_name="Add g.medium")

        # Pas 20 & 21: Networks
        smart_action(driver, wait, By.XPATH, "//span[normalize-space()='Networks']", "click", step_name="Tab Networks")
        net_search_xpath = "//hz-dynamic-table[contains(@items, 'network')]//input[@placeholder='Click here for filters or full text search.']"
        # Daca XPath-ul de mai sus esueaza, Horizon foloseste adesea un input generic in Networks:
        try:
            smart_action(driver, wait, By.XPATH, net_search_xpath, "type", "vlan9", "Search Network")
        except:
            smart_action(driver, wait, By.XPATH, "//input[@placeholder='Click here for filters or full text search.']", "type", "vlan9", "Search Network Generic")
        
        time.sleep(2)

        # Pas 22: Add Icon Network
        smart_action(driver, wait, By.XPATH, "//tr[contains(., 'vlan9')]//button[contains(@class, 'fa-arrow-up')]", "click", step_name="Add vlan9")

        # Pas 23: Final Launch
        smart_action(driver, wait, By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Launch Instance')]", "click", step_name="Launch Final")

        print("\n[FINISH] Scriptul a fost executat complet.")

    except Exception as e:
        print(f"\n[EROARE NEASTEPTATA] {e}")
    finally:
        input("\nApasa Enter pentru inchidere...")
        driver.quit()

if __name__ == "__main__":
    run_automation()
