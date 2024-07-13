"""
This module contains a script to scrape data from a website using Selenium and BeautifulSoup.
"""

import logging
import os
from io import StringIO
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import boto3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_goalies(driver, season_type, year):
    """
    Download goalie data for a specific season type and year.
    """
    logging.info(f"Downloading {season_type} {year} goalies...")
    select_year = Select(driver.find_element(By.ID, "season_type"))
    select_year.select_by_visible_text(year)

    table_html = driver.find_element(By.ID, "goaliesTable").get_attribute("outerHTML")
    table_io = StringIO(table_html)
    df = pd.read_html(table_io)[0]
    
    # Table is not being written to csv file correctly. Thanks CoPilot :D
    df['Name'] = df['Name'].str.extract(r'(\d+)([A-Za-z ]+)', expand=True)[1].str.strip()
    df_cleaned = df.dropna(subset=['Name'])
    
    return df_cleaned

def lambda_handler(event, context):
    """
    Open the webpage and download goalie data for different seasons and years.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Firefox(options=options)
    driver.get("https://moneypuck.com/goalies.htm")

    select_situation_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "situation_type")))
    season_type_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "table_playoff_type")))
    season_year_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "season_type")))

    select_situation_dropdown = Select(select_situation_dropdown)
    select_season_type = Select(season_type_dropdown)
    select_year = Select(season_year_dropdown)

    select_situation_dropdown.select_by_value("5on5")

    select_season_type_options = select_season_type.options
    year_options = select_year.options

    s3_bucket_name = os.environ.get("S3_BUCKET_NAME")  

    s3 = boto3.client("s3")
    files_written = []  

    for season_type in select_season_type_options:
        select_season_type.select_by_visible_text(season_type.text)

        for year in year_options:
            df_cleaned = download_goalies(driver, season_type.text, year.text)
            csv_data = df_cleaned.to_csv(index=False, sep="|")

            file_name = f"mp/raw/{year}/{season_type}/mp_{season_type}_{year}_goalies.csv"
            
            s3.put_object(Body=csv_data, Bucket=s3_bucket_name, Key=file_name)
            
            files_written.append(file_name)

    driver.close()

    return {
        "statusCode": 200,
        "body": "Data scraped and uploaded to S3 successfully!",
        "files_written": files_written  
    }
    