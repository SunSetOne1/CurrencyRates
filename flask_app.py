from flask import Flask, request, jsonify
from datetime import datetime
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Налаштування для Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/sunsetone/mysite/credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("CurrencyRates").sheet1

def get_currency_rates_from_nbu(update_from, update_to):
    date_from = datetime.strptime(update_from, '%Y-%m-%d').strftime('%Y%m%d')

    url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={date_from}&json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def update_google_sheet(data):
    for item in data:
        if 'r030' in item and 'rate' in item:
            sheet.append_row([datetime.now().strftime('%Y-%m-%d'), item['txt'], item['cc'], item['rate']])

@app.route('/update_currency', methods=['POST'])
def update_currency():
    update_from = request.args.get('update_from', datetime.now().strftime('%Y-%m-%d'))
    update_to = request.args.get('update_to', datetime.now().strftime('%Y-%m-%d'))

    rates = get_currency_rates_from_nbu(update_from, update_to)

    if rates:
        update_google_sheet(rates)
        return jsonify({"message": "Currency rates updated successfully!"})
    else:
        return jsonify({"error": "Failed to fetch currency rates"}), 500

if __name__ == '__main__':
     app.run(debug=True)