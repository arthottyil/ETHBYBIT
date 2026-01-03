from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os

app = Flask(__name__)

# Bybit API Keys ഇവിടെ നൽകുക
API_KEY = '9ceLUfP5UjKFcbSPpM'
API_SECRET = '9GhPuoubXxXaWyl58sNDfnxQkj6isAtgmyOP'

# Bybit സെഷൻ കണക്ട് ചെയ്യുന്നു
session = HTTP(
    testnet=False, # ലൈവ് ട്രേഡിംഗിന് False എന്ന് തന്നെ നൽകുക
    api_key=API_KEY,
    api_secret=API_SECRET,
)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # സിഗ്നൽ സ്വീകരിക്കുന്നു
        raw_data = request.get_data(as_text=True).lower()
        print(f"Bybit Signal: {raw_data}")

        symbol = "ETHUSDT"
        
        # BUY സിഗ്നൽ
        if 'buy' in raw_data:
            print("Bybit: Executing BUY Order...")
            order = session.place_order(
                category="spot",
                symbol=symbol,
                side="Buy",
                orderType="Market",
                qty="10", # 10 USDT മൂല്യമുള്ള ETH വാങ്ങുന്നു
                marketUnit="quoteCoin" # തുക USDT-യിൽ നിശ്ചയിക്കാൻ ഇത് സഹായിക്കും
            )
            print(f"Buy Success: {order}")
            return "Buy Executed", 200

        # SELL സിഗ്നൽ
        elif 'sell' in raw_data:
            print("Bybit: Executing SELL Order...")
            # ബാലൻസ് ചെക്ക് ചെയ്യുന്നു
            balance_info = session.get_wallet_balance(accountType="UNIFIED", coin="ETH")
            qty = balance_info['result']['list'][0]['coin'][0]['equity']
            
            if float(qty) > 0:
                order = session.place_order(
                    category="spot",
                    symbol=symbol,
                    side="Sell",
                    orderType="Market",
                    qty=str(qty)
                )
                print(f"Sell Success: {order}")
                return "Sell Executed", 200
            return "No ETH Balance", 200

    except Exception as e:
        print(f"Bybit Error: {str(e)}")
        return str(e), 200

    return "Ignored", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
