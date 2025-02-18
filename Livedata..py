from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import pandas as pd
import datetime, time

api_key = 'ABCD123'
username = 'ABCD'
pwd = '1234'
token = 'ABCDEFGHIJK'

obj=SmartConnect(api_key=api_key)
data = obj.generateSession(username, pwd, pyotp.TOTP(token).now())

df = pd.read_csv(r'K:/QuantLab/OptionLive/angelonetoken.csv')


index_symbol = "NIFTY"

symbol_token = df.loc[df['symbol'] == index_symbol, 'token'].values[0]

print(f"Token for {index_symbol}: {symbol_token}")

excel_path = "K:/QuantLab/OptionLive/niftyATM.xlsx"

while True:
    try:
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Data logged at {formatted_time}")
        # Get Live Spot Price
        
        spot_data = obj.ltpData(exchange="NSE", tradingsymbol=index_symbol, symboltoken=symbol_token)
        spot_price = spot_data['data']['ltp']
        
        # Calculate ATM Strike
        atm_strike = round(spot_price / 100) * 100
        
        expiry = "20FEB25"  # Set expiry date
        ce_symbol = f"NIFTY{expiry}{atm_strike}CE"
        pe_symbol = f"NIFTY{expiry}{atm_strike}PE"
        
        option_ce_token = df[df['symbol'] == ce_symbol]['token'].iloc[0]
        option_pe_token = df[df['symbol'] == pe_symbol]['token'].iloc[0]
        
        # Get Option Prices
        ce_data = obj.ltpData(exchange="NFO", tradingsymbol=ce_symbol, symboltoken=option_ce_token)
        ce_price = ce_data['data']['ltp']
        
        pe_data = obj.ltpData(exchange="NFO", tradingsymbol=pe_symbol, symboltoken=option_pe_token)
        pe_price = pe_data['data']['ltp']
        
        straddle_price = ce_price + pe_price
        
        # Append Data to Excel
        new_data = pd.DataFrame([[current_time, atm_strike, pe_price, ce_price, straddle_price]],
                                columns=["Time", "ATM Strike", "PE Value", "CE Value", "Straddle Price"])
        
        try:
            existing_data = pd.read_excel(excel_path)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except FileNotFoundError:
            updated_data = new_data
        
        updated_data.to_excel(excel_path, index=False)
        if (current_time.hour == 15 and current_time.minute == 30):
            break
      
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(60)  # Wait for 60 second
