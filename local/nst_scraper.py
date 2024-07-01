"""
This module contains a script to scrape data from a website using Selenium and BeautifulSoup.
"""

import time
import logging
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_table_with_bs4(driver):
    """Scrape table data using BeautifulSoup."""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table', {'id': 'players'})

    headers = [th.text.strip() for th in table.find_all('th')]
    rows = [[td.text.strip() for td in tr.find_all('td')] for tr in table.find_all('tr')[1:] if tr.find_all('td')]

    return pd.DataFrame(rows, columns=headers)

def main():
    """Main function to execute the script."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Firefox(options=options)

    driver.get('https://www.naturalstattrick.com/playerteams.php?stdoi=g')

    select_from_dropdown = Select(driver.find_element(By.ID, "fromseason"))
    year_options = [option.text for option in select_from_dropdown.options if option.text >= "2008-2009"]

    season_types = ["Regular Season", "Playoffs"]

    for year in year_options:
        for season_type in season_types:
            select_from_dropdown = Select(driver.find_element(By.ID, "fromseason"))
            select_thru_dropdown = Select(driver.find_element(By.ID, "thruseason"))
            select_season_type_dropdown = Select(driver.find_element(By.NAME, "stype"))
            submit_button = driver.find_element(By.XPATH, '//input[@type="submit" and @value="Submit"]')

            select_from_dropdown.select_by_visible_text(year)
            select_thru_dropdown.select_by_visible_text(year)
            select_season_type_dropdown.select_by_visible_text(season_type)

            submit_button.click()

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='players_wrapper']//table/tbody/tr"))
            )

            time.sleep(10)

            df = scrape_table_with_bs4(driver)

            if df.empty:
                logging.warning(f"DataFrame is empty for {year} - {season_type}")
            else:
                logging.info(f"Creating data file for {year} - {season_type}")

            df.to_csv(f"local/data/nst/nst_{season_type}_{year}_goalies.csv", index=False, sep="|")

    driver.quit()

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Script execution time: {execution_time} seconds")