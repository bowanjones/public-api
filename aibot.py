from dotenv import load_dotenv
import os
import requests
import uuid

load_dotenv()

secret = os.getenv("TOKEN")

# Authorization
url = "https://api.public.com/userapiauthservice/personal/access-tokens"
headers = {
    "Content-Type": "application/json"
}

request_body = {
  "validityInMinutes": 123,
  "secret": secret
}

response = requests.post(url, headers=headers, json=request_body)
access = response.json()["accessToken"]

# Account Id
url = "https://api.public.com/userapigateway/trading/account"
headers = {
    "Authorization": f"Bearer {access}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
accountId = response.json()["accounts"][0]["accountId"]

# Portfolio
url = f"https://api.public.com/userapigateway/trading/{accountId}/portfolio/v2"
headers = {
    "Authorization": f"Bearer {access}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data = response.json()
data.pop("accountId", None)
print(data)


# Option Chain
url = f"https://api.public.com/userapigateway/marketdata/{accountId}/option-chain"
headers = {
    "Authorization": f"Bearer {access}",
    "Content-Type": "application/json"
}

request_body = {
  "instrument": {
    "symbol": "ACN",
    "type": "EQUITY"
  },
  "expirationDate": "2025-08-29"
}

response = requests.post(url, headers=headers, json=request_body)
option_chain = response.json()

call_260 = next(
    c for c in option_chain["calls"]
    if int(c["instrument"]["symbol"][-8:]) / 1000 == 260
)

call_2625 = next(
    c for c in option_chain["calls"]
    if int(c["instrument"]["symbol"][-8:]) / 1000 == 262.5
)

symb1= call_260["instrument"]["symbol"]
symb2= call_2625["instrument"]["symbol"]
print("260C symbol:", symb1)
print("2625C symbol:", symb2)

# Limit Order
url = f"https://api.public.com/userapigateway/trading/{accountId}/order/multileg"
headers = {
    "Authorization": f"Bearer {access}",
    "Content-Type": "application/json"
}

order_id = str(uuid.uuid4())
request_body = {
  "orderId": order_id,
  "quantity": 1,
  "type": "LIMIT",
  "limitPrice": ".1",
  "expiration": {
    "timeInForce": "GTD",
    "expirationTime": "2025-11-22T23:10:23.771Z"
  },
  "legs": [
    {
      "instrument": {
        "symbol": symb1,
        "type": "OPTION"
      },
      "side": "BUY",
      "openCloseIndicator": "OPEN",
      "ratioQuantity": 1
    },
        {
      "instrument": {
        "symbol": symb2,
        "type": "OPTION"
      },
      "side": "SELL",
      "openCloseIndicator": "OPEN",
      "ratioQuantity": 1
    }
  ]
}

response = requests.post(url, headers=headers, json=request_body)
data = response.json()
print(data)

