import requests
from io import BytesIO
from PIL import Image
secret = open("s.txt").read()
url = "http://127.0.0.1:5000/secret"
headers = {
 'Key': f'{secret}',
}
perro_url = "https://upload.cloudlift.app/s/1d694e-4/P2KjZbbilz.jpg"
data = {"url": perro_url, "pet_name": "Fifi"
}

response = requests.get(url, headers=headers, json=data)
print (response)
#print(response.content)


img = Image.open(BytesIO(response.content)).convert("RGBA").save("response.png", format='PNG')

