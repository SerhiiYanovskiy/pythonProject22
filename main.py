from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


def get_fedex(trak):
    opts = Options()
    opts.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    driver.get("https://www.fedex.com/fedextrack/")
    time.sleep(2)
    click = "/html/body/div[1]/div/div/div[2]/ul[2]/li[2]/button"
    driver.find_element_by_xpath(click).click()
    input_track = "/html/body/div[1]/div/div/div[2]/div[2]/div/form/input"
    driver.find_element_by_xpath(input_track).send_keys("776783001175")
    driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[2]/div/form/button").click()
    time.sleep(3)
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html")
    status = soup.find("div", class_="detail-page-default").find("h1")
    return status.text


def get_usp(track):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    driver.get(f"https://www.ups.com/track?loc=en_US&requester=QUIC&tracknum={track}/trackdetails")
    time.sleep(1)
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html")
    status = soup.find("div", class_="ng-star-inserted").find_all("span")
    return str(status[1].text.split(" ")[1])

def get_usps(track):
    opts = Options()
    opts.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    driver.get(f"https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1={track}")
    time.sleep(3)
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html")
    status = soup.find("div", class_="delivery_status").find("strong").text
    return status.split(" ")[0]



SAMPLE_RANGE_NAME = 'testlist!A2:C2000'
class GoogleSheet:
    SPREADSHEET_ID = '12jygv7rlII6S793yljvfOP-V1W1QwH9w0WEEGfR4OSM'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def update(self, range, values):
        data = [{
            'range': range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
                                                                  body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

    def read(self, range):
        try:
            result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])
            return values
        except HttpError as err:
            print(err)



def main():
    gs = GoogleSheet()
    range = 'testlist!A2:C2000'
    res = gs.read(range)
    for elem in res:
        if elem[1] == "UPS":
            new = get_usp(elem[0])
            elem[2] = str(new)
        elif elem[1] == "FedEx":
            new = get_fedex(elem[0])
            elem[2] = new
        elif elem[1] == "USPS":
            new = get_usps(elem[0])
            elem[2] = new
        else:
            continue

    gs.update(range, res)


if __name__ == "__main__":
    main()

