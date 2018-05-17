Python, Flask and color processing
=======================================================================

Process image colors with `requests <http://docs.python-requests.org/en/latest/user/quickstart/#binary-response-content>`_ and `cologram <https://github.com/obskyr/colorgram.py>`_

Create a config.yaml file with correct settings out of the provided config.yaml.orig provided.

.. code-block:: bash

  $ docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" -t alexisbellido/color-process:0.2 .
  $ docker run -it --rm -v $PWD:/root alexisbellido/color-process:0.2 /bin/bash

Also see `<https://github.com/alexisbellido/dockerize-django/tree/master/basic-python>`_.

.. code-block:: bash

  $ python colors.py --id 18140655 -e local


TODO
--------------------------------------------------------

MySQL queries to get image URL from object ID
