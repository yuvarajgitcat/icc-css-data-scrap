import pandas as pd
from selenium import webdriver
import re
import json

# List of URLs for each year from 2020 to 2024
urls = [
    "https://www.icc-ccs.org/index.php/piracy-reporting-centre/live-piracy-map/piracy-map-2024",
    "https://www.icc-ccs.org/index.php/piracy-reporting-centre/live-piracy-map/piracy-map-2023",
    "https://www.icc-ccs.org/index.php/piracy-reporting-centre/live-piracy-map/piracy-map-2022",
    "https://www.icc-ccs.org/index.php/piracy-reporting-centre/live-piracy-map/piracy-map-2021",
    "https://www.icc-ccs.org/index.php/piracy-reporting-centre/live-piracy-map/piracy-map-2020"
]

# Function to extract details using regular expressions
def extract_details(details):
    attack_id_pattern = r"Attack ID:\s*(\S+)"
    sitrep_pattern = r"Sitrep:\s*(.*?)(?:\n|$)"
    date_pattern = r"\d{2}\.\d{2}\.\d{4}"

    attack_id_match = re.search(attack_id_pattern, details)
    attack_id = attack_id_match.group(1) if attack_id_match else "Not Found"

    sitrep_match = re.search(sitrep_pattern, details)
    sitrep = sitrep_match.group(1) if sitrep_match else "Not Found"

    date_match = re.search(date_pattern, sitrep)
    date = date_match.group(0) if date_match else "Not Found"

    location = "Not Found"
    
    def location_extract(sitrep):
        if sitrep:
            parts = sitrep.split(',')
            if len(parts) > 1:
                location_candidate_last = parts[-1].strip()
                if len(parts) > 2:
                    location_candidate_2nd_last = parts[-2].strip()
                    if len(parts) > 3:
                        location_candidate_3rd_last = parts[-3].strip()

                        if any(c.isalpha() for c in location_candidate_3rd_last):
                            return f"{location_candidate_3rd_last}, {location_candidate_2nd_last}, {location_candidate_last}"
                    
                    if any(c.isalpha() for c in location_candidate_2nd_last):
                        return f"{location_candidate_2nd_last}, {location_candidate_last}"
                
                if any(c.isalpha() for c in location_candidate_last):
                    return location_candidate_last

        return location

    location = location_extract(sitrep)

    if sitrep_match:
        sitrep_end_index = sitrep_match.end()
        description = details[sitrep_end_index:].strip()
    else:
        description = "Not Found"

    return attack_id, date, sitrep, location, description

# Collect all data in a single list
data_list = []

# Set up Selenium
driver = webdriver.Chrome()

# Loop through each URL to scrape data
for url in urls:
    driver.get(url)
    driver.implicitly_wait(10)
    page_source = driver.page_source

    # Regex to capture JSON-like structure of incident data
    pattern = re.compile(r'\{.*?"Attack ID.*?\}', re.DOTALL)
    incidents_data = pattern.findall(page_source)

    # Process each JSON string and extract key information
    for incident in incidents_data:
        try:
            cleaned_data = re.sub(r'<.*?>', '', incident)
            incident_json = json.loads(cleaned_data)

            details = incident_json.get('2', '')
            attack_id, date, sitrep, location, description = extract_details(details)

            data_list.append({
                'Latitude': incident_json.get('0'),
                'Longitude': incident_json.get('1'),
                'Attack ID': attack_id,
                'Date': date,
                'Sitrep': sitrep,
                'Location': location,
                'Description': description
            })
        except json.JSONDecodeError:
            continue

# Close the driver
driver.quit()

# Convert to DataFrame 
df = pd.DataFrame(data_list)

# Save DataFrame to Excel
df.to_excel("Aincident_data_with_extracted_details.xlsx", index=False)

print("Data saved to incident_data_with_extracted_details.xlsx")
