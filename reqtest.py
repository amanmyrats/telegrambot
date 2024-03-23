import requests

url = 'https://api.telegram.org/bot7156890309:AAFOhkmgYUK4uo23NsK_KsCTrl-eSjZahFw/getUpdates'

response = requests.get(url)
print(response.text)