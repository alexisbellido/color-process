from io import BytesIO
import requests
import colorgram
import webcolors
from PIL import Image
import cooperhewitt.swatchbook as swatchbook

image_url = 'https://images.collection.cooperhewitt.org/84_1dc8f7f74b3e7413_z.jpg'
r = requests.get(image_url)
colors = colorgram.extract(BytesIO(r.content), 5)
print("Colors for {0}".format(image_url))

references = ('css3', 'css4', 'crayola')
for reference in references:
    print("reference: {reference}".format(
        reference = reference
    ))
    ref = swatchbook.load_palette(reference)
    for color in colors:
        hex = webcolors.rgb_to_hex((color.rgb.r, color.rgb.g, color.rgb.b))
        closest = swatchbook.closest(reference, hex)
        print("hex: {hex} - closest: {closest}".format(
            hex = hex,
            closest = closest
        ))
        print("============")
