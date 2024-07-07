import os

import requests
from requests_oauthlib import OAuth2Session
import pprint

# Setup credentials and URLs
company_id = os.getenv('COMPANY_ID')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"
sandbox_base_url = f'https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}'
auth_url = 'https://appcenter.intuit.com/connect/oauth2'
token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
scope = ['com.intuit.quickbooks.accounting']

# Step 1: Get Authorization URL and store state
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
authorization_url, state = oauth.authorization_url(auth_url)
print('Please go to this URL and authorize access:', authorization_url)

# Step 2: Get the authorization response
redirect_response = input('Paste the full redirect URL here: ')

# Step 3: Recreate the OAuth2 session with the state and fetch the token
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, state=state, scope=scope)
oauth.fetch_token(token_url, authorization_response=redirect_response, client_secret=client_secret)


# Step 4: Fetch transactions
def fetch_transactions():
    url = f'{sandbox_base_url}/query?query=select * from BankTxn'
    headers = {
        'Authorization': f'Bearer {oauth.token["access_token"]}',
        'Accept': 'application/json'
    }
    response = oauth.get(url, headers=headers)

    # Handle potential errors
    try:
        response.raise_for_status()
        transactions = response.json().get('QueryResponse', {}).get('BankTxn', [])
    except (requests.exceptions.HTTPError, ValueError) as e:
        print(f'Error: {e}')
        print('Response content:', response.content)
        transactions = []

    return transactions


# Fetch and print the first transaction
transactions = fetch_transactions()
if transactions:
    pprint.pprint(transactions[0])
else:
    print("No transactions found or an error occurred.")