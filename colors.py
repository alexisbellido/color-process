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
@click.option('-u', '--url', help='Image URL')
def extract_colors(url):
    click.echo('Extracting colors from {url}'.format(
        url = url
    ))
    r = requests.get(url)
    colors = colorgram.extract(BytesIO(r.content), 5)

    references = ('css3', 'css4', 'crayola')
    for reference in references:
        click.echo("reference: {reference}".format(
            reference = reference
        ))
        ref = swatchbook.load_palette(reference)
        for color in colors:
            hex = webcolors.rgb_to_hex((color.rgb.r, color.rgb.g, color.rgb.b))
            closest = swatchbook.closest(reference, hex)
            click.echo("hex: {hex} - closest: {closest}".format(
                hex = hex,
                closest = closest
            ))
            click.echo("============")

@click.command()
@click.option('-n', '--accession_number', help='Accession number (object number in TMS exports)')
@click.option('-e', '--environment', default='local', help='Environment.')
@click.option('--input', type=click.File('r'), required=False)
@click.option('--dryrun', is_flag=True, help='Dry run, nothing is actually changed.')
def extract(environment, dryrun, accession_number=None, input=None):
    """Query MS SQL TMS database and updates MySQL collection website database."""
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

    if not accession_number and not input:
        click.echo('Nothing to process. Pass an accession number or input file\n')
        exit()

    accession_numbers = []

    if accession_number:
        accession_numbers.append(accession_number)
    elif input:
        for accession_number in input:
            accession_numbers.append(accession_number.rstrip())

    count=0
    for accession_number in accession_numbers:
        count += 1
        click.echo('===========================================================\n')
        click.echo('{count} - Running for {accession_number} on {environment}\n'.format(
            count=count,
            accession_number=accession_number,
            environment=environment
        ))

        # MS SQL processing
        # http://www.pymssql.org/en/stable/pymssql_examples.html
        conn = pymssql.connect(
            config[environment]['mssql']['host'],
            config[environment]['mssql']['username'],
            config[environment]['mssql']['password'],
            config[environment]['mssql']['database']
        )
        cursor = conn.cursor()
        tms_query = """SELECT TOP 1
            o.ObjectNumber,
            o.ObjectName,
            ot.Title,
            o.Description,
            o.DateBegin,
            o.DateEnd,
            o.Dated,
            o.CreditLine,
            o.ClassificationID,
            o.Medium,
            o.Dimensions,
            o.Markings,
            o.Signed,
            o.Inscribed,
            o.Provenance,
            o.PublicAccess,
            o.Accountability,
            o.ObjectID,
            can.AltNameId,
            can.DisplayName,
            c.ConstituentID,
            cxrd.ConXrefID
        FROM Objects o
            INNER JOIN ObjTitles ot ON o.ObjectID = ot.ObjectID AND ot.DisplayOrder = 1
            INNER JOIN ConXrefs cxr ON cxr.ID = o.ObjectID
            INNER JOIN ConXrefDetails cxrd ON cxr.ConXrefID = cxrd.ConXrefID
            INNER JOIN Roles r ON cxr.RoleID = r.RoleID
            INNER JOIN ConAltNames can ON cxrd.NameID = can.AltNameId
            INNER JOIN Constituents c ON can.ConstituentID = c.ConstituentID
        WHERE
            (cxr.TableID = 108) AND
            (r.Role = 'Designer' OR r.role='Artist') AND
            (r.RoleTypeID = 1) AND
            (cxrd.UnMasked=0) AND
            (o.ObjectNumber = '{accession_number}')""".format(
            accession_number=accession_number
        )
        cursor.execute(tms_query)

        # TODO improve turning None into empty string and replacing single unpack_quotes
        # Can I do it with T-SQL?
        for row in cursor:
            tms_object = {
                'object_number': row[0],
                'name': row[1],
                'title': row[2],
                'description': row[3] if row[3] else '',
                'date_begin': row[4],
                'date_end': row[5],
                'dated': row[6] if row[6] else '',
                'credit': row[7],
                'classification_id': row[8],
                'medium': row[9] if row[9] else '',
                'dimensions': row[10] if row[10] else '',
                'markings': row[11] if row[11] else '',
                'signed': row[12] if row[12] else '',
                'inscribed': row[13] if row[13] else '',
                'provenance': row[14] if row[14] else '',
                'public_access': row[15],
                'accountability': row[16],
                'display_name': row[19],
                'constituent_id': row[20],
                'conxref_id': row[21],
            }
            break

        if dryrun:
            click.echo("\nDry run MS SQL Server...\n")
            click.echo(tms_object)
            conn.close()

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
        c.execute("""SELECT id, accession_number FROM Objects WHERE accession_number = '%s'""" % (
        accession_number,
        ))
        row = c.fetchone()
        object_id = row[0]
        if 'local' == environment:
            url = 'https://collection.cooperhewitt.test/objects/{object_id}/'.format(
                object_id=object_id
            )
        elif 'production' == environment:
            url = 'https://collection.cooperhewitt.org/objects/{object_id}/'.format(
                object_id=object_id
            )
        click.echo('Object URL: {url}\n'.format(
            url=url
        ))

        if dryrun:
            click.echo("\nDry run MySQL...\n")
            click.echo(row)
        else:
            # TODO improve removal of single quotes
            click.echo(tms_object)
            c.execute("""UPDATE Objects SET titles="{""1"":{""en-uk"":""%s""}}", display_medium="%s", tms_extras='{"display_date":"%s","markings":"%s","signed":"%s","inscribed":"%s","provenance":"%s","description":"%s","dimensions":"%s","name":"%s","credit":"%s","public_access":"%s","accountability":"%s"}' WHERE accession_number = '%s'""" % (
                tms_object['title'].replace("'","''"),
                tms_object['medium'].replace("'","''"),
                tms_object['dated'],
                tms_object['markings'].replace("'","''"),
                tms_object['signed'].replace("'","''"),
                tms_object['inscribed'].replace("'","''"),
                tms_object['provenance'].replace("'","''"),
                tms_object['description'].replace("'","''"),
                tms_object['dimensions'],
                tms_object['name'].replace("'","''"),
                tms_object['credit'].replace("'","''"),
                tms_object['public_access'],
                tms_object['accountability'],
                accession_number
            ))
            # TODO other persons besides tms_object['constituent_id'] 5840
            if 5840 == tms_object['constituent_id']:
                c.execute("""INSERT INTO ObjectsPeople (object_id, person_id, role_id, alt_name_tms_id, is_public, object_score, role_type_id, parent_id, count_images, count_images_public, tms_id) VALUES (
                    %d, 18050457, 35236565, 8383, 1, 7, 1, 0, 1, 1, %d) ON DUPLICATE KEY UPDATE object_id = %d""" % (
                    object_id,
                    tms_object['conxref_id'],
                    object_id,
                ))
        db.commit()
        db.close()
        click.echo('===========================================================\n')

if __name__ == '__main__':
    extract_colors()
