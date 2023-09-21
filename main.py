import requests
import selectorlib
import os
import smtplib
import ssl
import time
import sqlite3

# "INSERT INTO events VALUES ('Tigers', 'Tiger City', '2023.09.02"
# "SELECT * FROM events WHERE city = 'Lion City'"
# "DELETE FROM events WHERE band = 'Tigers'"

PASSWORD = os.getenv("PASSWORD")


URL = "https://programmer100.pythonanywhere.com/tours/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Establish a connection and a cursor
connection = sqlite3.connect("data.db")

def scrape(url):
    # Get response code
    response = requests.get(url=url, headers=HEADERS)
    # Get html text from response code
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    print('extracted_value:', value)
    print(value)
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = "shibbirahmedd@gmail.com"
    password = PASSWORD

    receiver = "shibbirahmedd@gmail.com"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        # Sending mail
        server.sendmail(username, receiver, message)

    print("Email sent")


def store(extracted):
    row = extracted.split(",")
    row = [i.strip() for i in row]
    # band, city, date = row
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
    connection.commit()


def read(extracted):
    row = extracted.split(",")
    row = [i.strip() for i in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?",(band, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


if __name__ == "__main__":
    try:
        while True:
            scraped = scrape(URL)
            extracted = extract(scraped)
            print('extracted:', extracted)

            if extracted != "No upcoming tours":
                row = read(extracted)
                print('row:',row)
                if not row:
                    store(extracted)
                    send_email(message="Hey, new event was found!")

            time.sleep(2)
    except KeyboardInterrupt:
        print("Script interrupted. Exiting gracefully.")
