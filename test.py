from io import BytesIO
import requests
import colorgram
from PIL import Image


r = requests.get('http://www.sciencekids.co.nz/images/pictures/flags680/Argentina.jpg')
colors = colorgram.extract(BytesIO(r.content), 3)
print("Hello again miau 3")
print(colors)
