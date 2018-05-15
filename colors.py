# -- coding: utf-8 --

import yaml
import json

import click
from io import BytesIO
import requests
import colorgram
import webcolors
from PIL import Image
import cooperhewitt.swatchbook as swatchbook

@click.command()
@click.option('-i', '--id', help='Object ID')
@click.option('-u', '--url', help='Image URL')
def extract_colors(id, url):
    click.echo('Extracting colors for object {id}, image {url}'.format(
        id = id,
        url = url
    ))

    separator = ','
    headings = [
        'object_id',
        'url',
        'palette',
        'color_1',
        'closest_1',
        'color_2',
        'closest_2',
        'color_3',
        'closest_3',
        'color_4',
        'closest_4',
        'color_5',
        'closest_5'
    ]
    click.echo(separator.join(headings))

    r = requests.get(url)
    colors = colorgram.extract(BytesIO(r.content), 5)
    references = ('css3', 'css4', 'crayola')
    for reference in references:
        # click.echo("reference: {reference}".format(
        #     reference = reference
        # ))
        ref = swatchbook.load_palette(reference)

        line = [
            id,
            url,
            reference
        ]

        for color in colors:
            hex = webcolors.rgb_to_hex((color.rgb.r, color.rgb.g, color.rgb.b))
            closest = swatchbook.closest(reference, hex)
            line.extend((hex, closest[0]))
            # click.echo("hex: {hex} - closest: {closest}".format(
            #     hex = hex,
            #     closest = closest
            # ))
            # click.echo("============")

        click.echo(separator.join(line))

if __name__ == '__main__':
    extract_colors()
