import requests

username = 'your_geonames_username'
url = f'http://api.geonames.org/searchJSON?formatted=true&q=USA&maxRows=1000&username={username}'

response = requests.get(url)
data = response.json()

for city in data['geonames']:
    print(city['name'], city['lat'], city['lng'])
