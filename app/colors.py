# -- coding: utf-8 --

import yaml
import json

import click
from io import BytesIO
import MySQLdb
import requests
import colorgram
import webcolors
from PIL import Image
import cooperhewitt.swatchbook as swatchbook

@click.command()
@click.option('-i', '--id', help='Object ID')
@click.option('--input', type=click.File('r'), required=False)
@click.option('--output', type=click.File('w'), required=False)
@click.option('-e', '--environment', default='local', help='Environment.')
def extract_colors(id = None, input = None, output = None, environment = 'local'):

    ids = []
    if id:
        ids.append(id)
    elif input:
        for id in input:
            ids.append(id.rstrip())
        input.close()

    if not ids:
        click.echo('No object IDs passed')
        exit()

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

    if output:
        output.write(separator.join(headings) + '\n')

    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

    # MySQL processing
    # http://mysqlclient.readthedocs.io/user_guide.html#introduction
    db = MySQLdb.connect(
        host=config[environment]['mysql']['host'],
        user=config[environment]['mysql']['username'],
        passwd=config[environment]['mysql']['password'],
        db=config[environment]['mysql']['database'],
        use_unicode=True,
        charset='utf8'
    )

    c = db.cursor()
    sql = """SELECT tms_id, secret FROM ObjectsImages WHERE object_id = '%s' AND is_primary = 1 ORDER BY tms_id"""

    for id in ids:
        click.echo('\nExtracting colors for object {id}'.format(
            id = id
        ))
        c.execute(sql % (id))
        row = c.fetchone()
        if not row:
            continue

        url = 'https://images.collection.cooperhewitt.org/{tms_id}_{secret}_z.jpg'.format(
            tms_id = row[0],
            secret = row[1]
        )
        r = requests.get(url)

        if r.status_code != 200:
            url = 'https://images.collection.cooperhewitt.org/{tms_id}__z.jpg'.format(
                tms_id = row[0],
                secret = row[1]
            )
            r = requests.get(url)

        try:
            colors = colorgram.extract(BytesIO(r.content), 5)
        except OSError:
            continue

        references = ('css3', 'css4', 'crayola')

        for reference in references:
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
            if output:
                output.write(separator.join(line) + '\n')
            else:
                click.echo(separator.join(line))

    if output:
        output.close()
    db.close()

if __name__ == '__main__':
    extract_colors()
