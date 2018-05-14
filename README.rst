Python, Flask and color processing
=======================================================================

.. code-block:: bash

  $ docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" -t alexisbellido/color-process:0.1 .
  $ docker run -it --rm -v $PWD:/root alexisbellido/color-process:0.1 /bin/bash

Also see `<https://github.com/alexisbellido/dockerize-django/tree/master/basic-python>`_.

TODO
--------------------------------------------------------

rebuild Docker image to use requirements.txt

verify if colormath 3.0 is compatible. cooperhewitt-swatchbook 0.3 has requirement colormath<2.0, but you'll have colormath 3.0.0 which is incompatible.
