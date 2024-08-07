import requests
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

def get_users_from_shopfa(mobile=None, q=None, limit=1000000):
    private_key = os.getenv('SHOPFA_PRIVATE_KEY')
    site_domain = os.getenv('SITE_DOMAIN')
    
    if not private_key or not site_domain:
        print("API key or site domain is missing.")
        return None

    url = f'{site_domain}/api/user/users'
    headers = {
        'Private-Key': private_key,
        'Content-Type': 'application/json'
    }

    params = {
        'limit': limit,
        'mobile': mobile,
        'q': q
    }
    
    try:
        print(f"Sending request to {url} with params {params}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        print("Received response from Shopfa.")
        response_json = response.json()
        print("Response Content:", response_json)
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"Failed to get users from Shopfa: {e}")
        return None

def save_contact_to_didar(contact_data):
    didar_api_key = os.getenv('DIDAR_API_KEY')
    if not didar_api_key:
        print("Didar API key is missing.")
        return None

    didar_url = f'https://app.didar.me/api/contact/save?ApiKey={didar_api_key}'

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "Contact": contact_data
    }

    try:
        print(f"Sending data to Didar: {data}")
        response = requests.post(didar_url, json=data, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        print("Received response from Didar:", response_json)
        
        if 'Response' in response_json:
            print(f"Successfully saved contact with ID: {response_json['Response'].get('Id')}")
        else:
            print("Response content does not contain 'Response':", response_json)
        
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to Didar: {e}")
        if 'response' in locals():
            print("Response Content:", response.text)
        return None

def transfer_users_from_shopfa_to_didar():
    shopfa_data = get_users_from_shopfa()
    if not shopfa_data:
        print("No data retrieved from Shopfa.")
        return

    number_of_users_received = len(shopfa_data.get('items', []))
    print(f"Number of users received from Shopfa: {number_of_users_received}")

    for user in shopfa_data.get('items', []):
        contact_data = {
            "Code": str(user.get("id")),  
            "Title": user.get("nickname") if user.get("nickname") else user.get("name"),
            "FirstName": user.get("first_name"),
            "LastName": user.get("last_name") if user.get("last_name") else "Unknown",  
            "DisplayName": f"{user.get('first_name')} {user.get('last_name')}".strip(),  
            "MobilePhone": user.get("mobile"),
            "Email": user.get("email") if user.get("email") else "",  
            "BirthDate": "",  
            "CustomerCode": "",  
            "Address": ""  
        }

        result = save_contact_to_didar(contact_data)
        if result:
            print(f"Successfully saved contact: {result}")
        else:
            print("Failed to save contact.")

if __name__ == "__main__":
    transfer_users_from_shopfa_to_didar()