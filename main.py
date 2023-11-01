import requests
import inquirer
import json
import argparse
import re
import base64
from base64 import b64encode
from cdm.wks import KeyExtractor

parser = argparse.ArgumentParser(description='DisneyPlus Downloader')
parser.add_argument('-url', type=str, help='URL to extract ID from')
parser.add_argument('-sc', action='store', default='ctr-regular', choices=['ctr-regular', 'cbcs-regular', 'restricted-drm-ctr-sw', 'restricted-drm-cbcs-sw', 'handset-drm-ctr', 'handset-drm-cbcs', 'tv-drm-ctr', 'tv-drm-cbcs'], help='Audio')
args = parser.parse_args()
url = args.url
scenario = args.sc
response = requests.get(url)
identifier = re.search(r'/video/([\w-]+)', response.text).group(1)
print("Identifier found:", identifier)
web_page = 'https://www.disneyplus.com/login'
response = requests.get(web_page)
match = re.search(r"window.server_path = ({.*});", response.text)
if match:
    data = json.loads(match.group(1))
    client_api_key = data["sdk"]["clientApiKey"]

email = 'your email'
password = 'your password'
api_key = client_api_key
device = "android-tv"
application = "android"
latitude = 0
longitude = 0
device_url = f"https://disney.api.edge.bamgrid.com/devices"
device_headers = {
    "authorization": f"Bearer {api_key}"
}
device_data = {
    "deviceFamily": device,
    "applicationRuntime": application,
    "deviceProfile": device,
    "attributes": {}
}
device_response = requests.post(device_url, headers=device_headers, json=device_data)
device_token = device_response.json()
exchange_url = f"https://disney.api.edge.bamgrid.com/token"
exchange_headers = {
    "authorization": f"Bearer {api_key}"
}
exchange_data = {
    "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
    "latitude": latitude,
    "longitude": longitude,
    "platform": device,
    "subject_token": device_token["assertion"],
    "subject_token_type": "urn:bamtech:params:oauth:token-type:device"
}
exchange_response = requests.post(exchange_url, headers=exchange_headers, data=exchange_data)
exchange_device = exchange_response.json()
login_url = f"https://disney.api.edge.bamgrid.com/idp/login"
login_headers = {
    "authorization": f"Bearer {exchange_device['access_token']}"
}
login_data = {
    "email": email,
    "password": password
}
login_response = requests.post(login_url, json=login_data, headers=login_headers)
login = login_response.json()
grant_token_url = f"https://disney.api.edge.bamgrid.com/accounts/grant"
grant_token_headers = {
    "authorization": f"Bearer {exchange_device['access_token']}"
}
grant_token_data = {
    "id_token": login["id_token"]
}
grant_token_response = requests.post(grant_token_url, headers=grant_token_headers, json=grant_token_data)
grant_token = grant_token_response.json()
access_token_url = f"https://disney.api.edge.bamgrid.com/token"
access_token_headers = {
    "authorization": f"Bearer {api_key}"
}
access_token_data = {
    "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
    "latitude": latitude,
    "longitude": longitude,
    "platform": device,
    "subject_token": grant_token['assertion'],
    "subject_token_type": "urn:bamtech:params:oauth:token-type:account"
}
access_token_response = requests.post(access_token_url, headers=access_token_headers, data=access_token_data)
access_token = access_token_response.json()
token = access_token["access_token"]
headers_token = {
    'authorization': f'Bearer {token}',
    'origin': 'https://www.disneyplus.com',
    'referer': 'https://www.disneyplus.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
}

response = requests.get(
    f'https://disney.content.edge.bamgrid.com/svc/content/DmcVideo/version/5.1/region/US/audience/k-false,l-true/maturity/1850/language/en/contentId/{identifier}',
    headers=headers_token,
)
data = response.json()
mediaId = data['data']['DmcVideo']['video']['mediaMetadata']['mediaId']
headers_uwu = {
    'authorization': token,
    "accept": "application/vnd.media-service+json; version=4",
    "x-dss-edge-accept": "vnd.dss.edge+json; version=2",
    "x-dss-feature-filtering": "true",
}
data = {"mediaId": mediaId}
json_string = json.dumps(data)
base64_encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
json_data_uwu = {
    'playback': {
        'attributes': {
            'resolution': {
                'max': [
                    '1280x720',
                ],
            },
            'protocol': 'HTTPS',
            'assetInsertionStrategy': 'SGAI',
            'playbackInitiationContext': 'ONLINE',
            'frameRates': [
                60,
            ],
            'slugDuration': 'SLUG_500_MS',
        },
        'adTracking': {
            'limitAdTrackingEnabled': 'YES',
            'deviceAdId': '00000000-0000-0000-0000-000000000000',
        },
        'tracking': {
            'playbackSessionId': mediaId,
        },
    },
    'playbackId': base64_encoded,
}
response_uwu = requests.post('https://disney.playback.edge.bamgrid.com/v7/playback/ctr-regular', headers=headers_uwu, json=json_data_uwu)
data = response_uwu.json()
base = data['stream']["sources"][0]["complete"]["base"]
path = data['stream']["sources"][0]["complete"]["path"]
queryParams = data['stream']["sources"][0]["complete"]["queryParams"]
m3u8 = f"{base}{path}{queryParams}"
response = requests.get(m3u8)
m3u8_content = response.text
start_marker = 'URI="data:text/plain;base64,'
end_marker = '"'
start_index = m3u8_content.find(start_marker) + len(start_marker)
end_index = m3u8_content.find(end_marker, start_index)
pssh_m3u8 = m3u8_content[start_index:end_index]
print(m3u8)
license_url = "https://disney.playback.edge.bamgrid.com/widevine/v1/obtain-license"
headers = {
    'authorization': f'Bearer {token}',
    'origin': 'https://www.disneyplus.com',
    'referer': 'https://www.disneyplus.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
}

cert_b64 = None
key_extractor = KeyExtractor(pssh_m3u8, cert_b64, license_url, headers)
keys = key_extractor.get_keys()

for key in keys:
    if isinstance(key, list):
        if key:
            for key_str in key:
                print(f"KEY: {key_str}")
