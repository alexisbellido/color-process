Python, Flask and color processing
=======================================================================

.. code-block:: bash

  $ docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" -t alexisbellido/color-process:0.1 .
  $ docker run -it --rm -v $PWD:/root alexisbellido/color-process:0.1 /bin/bash

Also see `<https://github.com/alexisbellido/dockerize-django/tree/master/basic-python>`_.
