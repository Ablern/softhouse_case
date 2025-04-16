# imports
from flask import Flask, jsonify
import pandas as pd
from datetime import datetime

# create a Flask app
app = Flask(__name__)
""" CSV-filen som används här är exemplet från uppgiften """
# hämta csv-fil med kolumnerna [Date, Kod, Kurs] som separeras av semikolon ';'

CSV_FILE = 'prices_csv.csv'

def pctchange(a, b):
    """ Beräkna procentuell förändring från a till b """
    return ((b-a)/a) * 100 if a!=0 else 0


def get_winners():
    # Läs in CSV-filen
    file = pd.read_csv(CSV_FILE, sep=';')
    file['Date'] = pd.to_datetime(file['Date'])

    # Ta ut senaste datumet och filtrera på det
    latest_date = file['Date'].dt.date.max()
    todays_df = file[file['Date'].dt.date == latest_date]

    winners = []

    for stock in file['Kod'].unique():
        if  len(todays_df[todays_df['Kod'] == stock]) == 0:
            print(f"No data for stock {stock} today.")
            # move on to next element in the loop
            continue

        elif len(todays_df[todays_df['Kod'] == stock]) == 1 and len(file[file['Kod'] == stock]) >= 2:     # bara ett pris idag, men säkerställ att det finns åtminstone en annan datapunkt från tidigare
            print(f"Only one data point for stock {stock} today, compare to yesterdays close price.")
            # Use yesterdays close price to compare with todays (only available) price
            stock_data = file[file['Kod'] == stock]
            stock_data = stock_data.sort_values('Date')
            last_price = stock_data['Kurs'].iloc[-1]          # hämta senaste tillgängliga kursen för 'stock'
            previous_price = stock_data['Kurs'].iloc[-2]       # hämta gårdagens stängningskurs, vi har säkerställt att det finne mer än en datapunkt

        else: 
            print(f"More than one available data point for stock {stock} today, compare to last price with first price of today.")
            # Use first price of today to compare with last price 
            stock_data = todays_df[todays_df['Kod'] == stock]  # hämta data för aktien 'stock'
            stock_data = stock_data.sort_values('Date')         # sortera data efter datum
            previous_price = stock_data['Kurs'].iloc[0]         # hämta första tillgängliga kursen för dagen för 'stock' 
            last_price = stock_data['Kurs'].iloc[-1]            # hämta senaste tillgängliga kursen för 'stock'

        percent_change = pctchange(previous_price, last_price)  # beräkna procentuell förändring (avkastning) från gårdagens stängningskurs till senaste
        # Lägg till aktien i listan
        winners.append({
            "name": stock,
            "percent": round(float(percent_change), 2),         # avrunda till 2 decimaler och typecasta till float för att undvika konflikter med typer från t ex numpy
            "latest": float(last_price)                         # typecast till float, samma anledning som ovan 
        })

        # Sortera listan och hämta topp 3
        winners = sorted(winners, key=lambda x: x['percent'], reverse=True)[:3]
        # Lägg till rank 
        for i, w in enumerate(winners, 1):
            w["rank"] = i
            
    return {"winners": winners}
    

""" Run the application """

@app.route('/winners', methods=['GET'])
def winners():
    return jsonify(get_winners())

if __name__ == '__main__':
    app.run(debug=True)