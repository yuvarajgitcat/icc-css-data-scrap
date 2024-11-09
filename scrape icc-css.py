import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json

# Set up Selenium with ChromeDriver
driver = webdriver.Chrome()
driver.get("https://www.icc-ccs.org/index.php/piracy-reporting-centre/live-piracy-map/piracy-map-2022")  # replace with actual URL

# Wait for the page to load
driver.implicitly_wait(10)
page_source = driver.page_source
driver.quit()

# Regex to capture JSON-like structure of incident data
pattern = re.compile(r'\{.*?"Attack ID.*?\}', re.DOTALL)
incidents_data = pattern.findall(page_source)

# Process each JSON string and extract key information
data_list = []
for incident in incidents_data:
    try:
        cleaned_data = re.sub(r'<.*?>', '', incident)
        incident_json = json.loads(cleaned_data)
        # Extracting relevant details
        data_list.append({
            'Latitude': incident_json.get('0'),
            'Longitude': incident_json.get('1'),
            'Details': incident_json.get('2')
        })
    except json.JSONDecodeError:
        continue

# Convert to DataFrame
df = pd.DataFrame(data_list)

# Save DataFrame to Excel
df.to_excel("incident_data.xlsx", index=False)

print("Data saved to incident_data.xlsx")
