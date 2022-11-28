import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import logging

CARGO_OPTIONS = [
    "GENERAL FREIGHT",
    "HOUSEHOLD GOODS",
    "XMETAL; SHEETS, COILS, ROLLS",
    "MOTOR VEHICLES",
    "DRIVE AWAY/TOWAWAY",
    "XLOGS, POLES, BEAMS, LUMBER",
    "XBUILDING MATERIALS",
    "MOBILE HOMES",
    "XMACHINERY, LARGE OBJECTS",
    "FRESH PRODUCE",
    "LIQUIDS/GASES",
    "INTERMODAL CONTAINERS",
    "PASSENGERS",
    "OIL FIELD EQUIPMENT",
    "LIVESTOCK",
    "GRAIN, FEED, HAY",
    "COAL, COKE",
    "MEAT",
    "XGARBAGE, REFUSE, TRASH",
    "U.S. MAIL",
    "CHEMICALS",
    "COMMODITIES DRY BULK",
    "REFRIGERATED FOOD",
    "BEVERAGES",
    "PAPER PRODUCTS",
    "UTILITY",
    "FARM SUPPLIES",
    "XCONSTRUCTION",
    "WATER WELL",
    "OTHER"
]


def process_row(row):
    """
    for each row from original dataframe, acquire additional required information from the webpage, and return concatenated rows
    """
    id_number = row['DOT_NUMBER']
    new_info = acquire_info_from_webpage(id_number)
    new_row = pd.concat([row,pd.Series(new_info)])
    return new_row

def acquire_info_from_webpage(id_number):
    """
    scrape the relevant info about the vehicle with this ID number, returns a dictionary of new columns relevant to the row
    """

    def acquire_cargo_info(soup):
        """
        return dictionary of the form {CARGO_OPTION: True/False, etc} for each cargo carried option, for a given BeautifulSoup for a given ID number
        """
        cargo_carried = soup.find(attrs={'class':'cargo'})

        cargo_dict = {x: False for x in CARGO_OPTIONS}
        for item in cargo_carried.find(attrs={'class': 'checked'}):
            # exclude nested spans that are used for eg Checked display
            if isinstance(item, NavigableString):
                cargo_dict[item] = True
        return cargo_dict
    

    def acquire_vehicle_type_info(soup):
        """
        return dictionary of the form {vehicle_type_owned: Int, vehicle_type_term_leased: Int, vehicle_type_trip_leased:Int} for a given BeautifulSoup for a given ID number
        """
        vehicle_types_properties = {}
        rows = soup.find("table").find("tbody").find_all("tr")


        for row in rows:
            header = row.find("th").get_text()

            cells = row.find_all("td")
            vehicle_types_properties[header + "_OWNED"] = int(cells[0].get_text())
            vehicle_types_properties[header + "_TERM_LEASED"] = int(cells[1].get_text())
            vehicle_types_properties[header + "_TRIP_LEASED"] = int(cells[2].get_text())
            
        return vehicle_types_properties
    


    URL = f"https://ai.fmcsa.dot.gov/SMS/Carrier/{id_number}/CarrierRegistration.aspx"
    try:
        data = requests.get(URL)
        soup = BeautifulSoup(data.content, 'html.parser')
        cargo_carried = soup.find_all("span", {"class": "cargo"})

        cargo_dict = acquire_cargo_info(soup)

        vehicle_type_dict = acquire_vehicle_type_info(soup)

        cargo_dict.update(vehicle_type_dict)
        return cargo_dict
    except: 
        logging.error('failed to parse page for following id: ', id_number, "the data for this ID will not be parsed")
