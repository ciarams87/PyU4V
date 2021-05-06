Installation Guide
==================

Requirements
------------

+-------------------------------+----------------------------------------+
| **PyU4V Version**             | 9.2.1.4                                |
+-------------------------------+----------------------------------------+
| **Minimum Unisphere Version** | 9.2.0.1                                |
+-------------------------------+----------------------------------------+
| **Array Model**               | VMAX-3, VMAX AFA, PowerMax             |
+-------------------------------+----------------------------------------+
| **Array uCode**               | HyperMax OS, PowerMax OS               |
+-------------------------------+----------------------------------------+
| **Platforms**                 | Linux, Windows                         |
+-------------------------------+----------------------------------------+
| **Python**                    | 3.6, 3.7, 3.8, 3.9                     |
+-------------------------------+----------------------------------------+
| **Requirements**              | Requests_, Six_, urllib3_,             |
|                               | prettytable_                           |
+-------------------------------+----------------------------------------+
| **Test Requirements**         | TestTools_, Tox_                       |
+-------------------------------+----------------------------------------+

.. note::
    If you want to continue to use Unisphere 8.4.x or 9.0.x with PyU4V you will
    need to remain on PyU4V 3.1.x. There is no support for PyU4V 9.x with any
    version of Unisphere older than 9.1.x

.. note::
    PyU4V officially supports Python 3.6, 3.7, 3.8, & 3.9. Python 2.x support
    has been dropped since January 1st 2020.

PyU4V Version Compatibility
---------------------------

PyU4V version 9.x is compatible with scripts written for PyU4V versions
>= 3.x, there is **zero** support or compatibility for PyU4V 2.x or earlier
scripts in later versions of PyU4V. If you have scripts written which
specifically target Unisphere REST 8.4, 9.0 or 9.1 endpoints these are still
accessible via PyU4V 9.2.x however you will need to ensure you are passing
the version required when performing these calls as PyU4V 9.2 will default
to using 9.2 endpoints exclusively.  You will also need to pay special
attention to any REST JSON payloads in custom scripts as payloads are
subject to change between major Unisphere REST releases.

Installation
------------

PyU4V can be installed from source, via ``pip``, or run directly from the
source directory. To clone PyU4V and install from source use ``git`` and
``pip``:

.. code-block:: bash

    $ git clone https://github.com/dell/PyU4V
    $ cd PyU4V/
    $ pip install .


Installing via ``pip`` without cloning from source can be achieved by
specifying ``PyU4V`` as the install package for ``pip``:

.. code-block:: bash

    $ pip install PyU4V
    # Install a specific version
    $ pip install PyU4V==9.2.1.1

.. URL LINKS

.. _Requests: https://realpython.com/python-requests/
.. _Six: https://six.readthedocs.io/
.. _urllib3: https://urllib3.readthedocs.io/en/latest/
.. _retired: https://pythonclock.org/
.. _TestTools: https://pypi.org/project/testtools/
.. _Tox: https://pypi.org/project/tox/
.. _prettytable: https://pypi.org/project/PrettyTable/
