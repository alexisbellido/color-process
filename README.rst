Python, Flask and color processing
=======================================================================

.. code-block:: bash

  $ docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" -t alexisbellido/color-process:0.2 .
  $ docker run -it --rm -v $PWD:/root alexisbellido/color-process:0.2 /bin/bash

Also see `<https://github.com/alexisbellido/dockerize-django/tree/master/basic-python>`_.

TODO
--------------------------------------------------------

rebuild Docker image to use requirements.txt

===

download and process image with requests and cologram

http://docs.python-requests.org/en/latest/user/quickstart/#binary-response-content
https://github.com/obskyr/colorgram.py

http://www.sciencekids.co.nz/pictures/flags.html
http://www.sciencekids.co.nz/images/pictures/flags680/Benin.jpg
http://www.sciencekids.co.nz/images/pictures/flags680/Argentina.jpg

import colorgram
import requests
from PIL import Image
from io import BytesIO
r = requests.get('http://www.sciencekids.co.nz/images/pictures/flags680/Argentina.jpg')
colors = colorgram.extract(BytesIO(r.content), 3)
colors
