import string
import requests
import pandas
import re
import mysql.connector
from bs4 import BeautifulSoup
from util.text import clean_string, remove_quotes

def get_subpage_data(url):
    subpage = requests.get(url)
    subpage_soup = BeautifulSoup(subpage.content, 'html.parser')
    section_why = subpage_soup.find(id = "why").find_all("p")
    purpose = section_why[0].text + "\n"
    return remove_quotes(purpose)

def get_valid_drug_data(a, druginfo_url):
    valid_drug_url_ex = '^./meds/[a-zA-Z0-9]+(-es.html){1}'
    try:
        is_valid_url = re.search(valid_drug_url_ex, a['href'])
        if is_valid_url:
            drug_name = "" if a.text is None else clean_string(a.text)
            drug_url = "" if a['href'] is None else a['href']
            subpage_url = druginfo_url + drug_url[2:len(drug_url)]
            drug_purpose = get_subpage_data(subpage_url)
            return drug_name.upper(), drug_url, "" if drug_purpose is None else drug_purpose      
    except Exception:
        print("Unable to get required data from ", a)
    return "", "", ""

def insert_drug_into_db(cursor, name, url, purpose):
    try:
        query = "INSERT INTO drugdb.drug (name, url, purpose) VALUES('{}', '{}', '{}')".format(name, url, purpose)
        cursor.execute(query)
    except mysql.connector.Error as err:
        print("Failed to insert", name, "into the DB")
    
def main():
    db_connection = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "passw0rd",
        database = "drugdb",
        port = "33060"
    )
    db_cursor = db_connection.cursor()

    druginfo_url = 'https://medlineplus.gov/spanish/druginfo/'
    page = None
    abc = string.ascii_uppercase
    count = 0

    for letter in abc:
        print("Scrapping drugs:", letter)
        url = druginfo_url + 'drug_' + letter + 'a.html'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        a_list = soup.body.find_all('a')
        for a in a_list:
            drug_name, drug_url, drug_purpose = get_valid_drug_data(a, druginfo_url)
            if drug_name != "":
                insert_drug_into_db(db_cursor, drug_name, drug_url, drug_purpose)
                count += 1
        db_connection.commit()
        print("Commited", count, "insertions into the DB:", letter)
        count = 0

    db_cursor.close()
    db_connection.close()

if __name__ == "__main__":
    main()