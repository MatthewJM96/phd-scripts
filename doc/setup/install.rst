************
Installation
************

Depending on how you'd like to install this package you have a couple of
options:

- `Using Poetry`_ (recommended)
- `Direct installation`_ (advanced users)

Using Poetry
============

We recommend installing `phdscripts` using
`poetry <https://python-poetry.org>`_, which ensures a clean contained virtual
environment with all our required dependencies without altering any versions your
existing system may rely on.

For alternative options see the `Direct Installation`_ section.

Windows users
-------------

.. TODO
.. warning:: These instructions have not been tested since migrating to poetry and
    require updating.

.. note:: Windows 10 now ships with a Linux subsystem, giving you access to a
    terminal environment which makes installation a whole lot simpler.

    This installation has been tested using the
    `ubuntu <https://www.microsoft.com/en-gb/p/ubuntu/9nblggh4msv6?activetab=pivot:overviewtab>`_
    system, though it should also work with any other Linux systems you have
    installed.

    For advanced users wishing to install this package within an existing
    Windows python install should see the `Direct installation`_ section.

Ensure you have `poetry` installed on your system. See
`here <https://python-poetry.org/docs/#installation/>`_.

    >>> poetry --version
    Poetry version 1.1.11

With a working Linux system and poetry installation, please follow the remainder
of these installation instructions within that environment (e.g. making sure
the pre-requisites mentioned below are also installed for linux, not on your
windows system).

Pre-requisites
--------------


Ensure you have `poetry` installed on your system. See
`here <https://python-poetry.org/docs/#installation/>`_.

You can check it is installed via your terminal:

    >>> poetry --version
    Poetry version 1.1.11

For development, you'll also need the
`poetry-dynamic-versioning <https://pypi.org/project/poetry-dynamic-versioning/>`_
plugin in your global python:

    >>> pip install poetry-dynamic-versioning

.. note:: Note this plugin must be installed in your **global** Python installation, not
    as a dev-dependency in a project's `pyproject.toml`. Hopefully poetry will support
    plugins in future. See
    `poetry-dynamic-versioning docs <https://pypi.org/project/poetry-dynamic-versioning>`_.





Mac/Linux Users
---------------

Installation for users
^^^^^^^^^^^^^^^^^^^^^^



To install the package in a dedicated environment, enter the following in a terminal window:

.. code-block:: bash

    cd /path/to/this/repo
    poetry install --no-dev

This script creates a dedicated environment named `phdscripts`,
and installs the `phdscripts` package and all its dependencies
within it.

See `poetry documentation <https://python-poetry.org>`_ for more details.





Installation for developers
^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are a separate set of package requirements for developers in order to
enable code linting checks, documentation builds etc.

To install the developer version of the package:



.. code-block:: bash

    cd /path/to/this/repo
    poetry install

Note that this installs the package in "editible" mode so any changes to the source code
will be reflected in your environment immediately.





`pre-commit`
""""""""""""

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

This repository has been set up to include
`pre-commit <https://pre-commit.com>`_ hooks to cover code linting, style,
import sorting etc. To take advantage of these tools, install ``pre-commit``
and run the following:

.. code-block:: bash

    poetry run pre-commit install

See ``.pre-commit-config.yaml`` for the current hooks in use.


Uninstalling the package
^^^^^^^^^^^^^^^^^^^^^^^^





The environment(s) for the project can be viewed with

    >>> poetry env list
    awesomepythonproject-xWGu4bMK-py3.9 (Activated)

and removed by supplying an environment name e.g.

    >>> poetry env remove awesomepythonproject-xWGu4bMK-py3.9
    Deleted virtualenv: {path_to_venv}/awesomepythonproject-xWGu4bMK-py3.9

See `poetry managing environments documentation <https://python-poetry.org/docs/managing-environments/>`_
for more details managing environments, such as having multiple environments, viewing
environment information and removing environments.



Direct installation
===================

If you'd prefer to install the `phdscripts` package within
an existing environment or at system level, you have a couple of options:

Installing from wheel
---------------------

Use `pip` to install the package from a wheel file (as found in the ``dist``
directory):

.. code-block:: bash

    pip install /path/to/<package_version>.whl

Installing from source code
---------------------------

To install a symlinked version of the package, so that any local changes to the
source code are immediately reflected within your python environment:

.. code-block:: bash

    cd /path/to/this/repo
    pip install -e .

Or leave off the ``-e`` flag if you want to install a static version instead.
