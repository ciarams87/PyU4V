..  toctree::
    :maxdepth: 2
    :hidden:

    installation
    configuration
    quick_start
    recommendations
    contribute
    support
    programmers_guide
    tools
    api
    genindex

Welcome to PyU4V's documentation!
=================================

Overview
--------

PyU4V is a Python module that simplifies interaction with the Unisphere for
PowerMax REST API.  It wraps REST calls with simple APIs that abstract the HTTP
request and response handling.

.. note::
   You can get the Unisphere for PowerMax REST documentation by
   navigating to a URL in your local instance of Unisphere for PowerMax.
   Navigate to ``https://{ip}:{port}/univmax/restapi/docs`` where ``{ip}`` is
   the IP address of your Unisphere server and ``{port}`` is the port it is
   listening on. A zip file will be downloaded to your computer containing
   complete Unisphere REST endpoint documentation.

Supported PyU4V Versions
------------------------

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

.. note::
    PyU4V version 9.x is compatible with scripts written for PyU4V versions
    >= 3.x, there is **zero** support or compatibility for PyU4V 2.x or earlier
    scripts in later versions of PyU4V. If you have scripts written which
    specifically target Unisphere REST 8.4, 9.0 or 9.1 endpoints these are
    still accessible via PyU4V 9.2.x however you will need to ensure you are
    passing the version required when performing these calls as PyU4V 9.2 will
    default to using 9.2 endpoints exclusively. You will also need to pay
    special attention to any REST JSON payloads in custom scripts as payloads
    are subject to change between major Unisphere REST releases.

Getting Started
---------------

:doc:`installation`
    How to get the source code, and how to build or install the python package.

:doc:`configuration`
    Configuring PyU4V for your environment.

:doc:`quick_start`
    Making your first calls with PyU4V.

:doc:`contribute`
    Contribute to the PyU4V project.

:doc:`support`
    How to get support with or open issues for PyU4V.

:doc:`programmers_guide`
    A range of examples demonstrating various PyU4V module usage.

:doc:`tools`
  The tools guide for PyU4V

:doc:`api`
    A glossary of all available functions.

Build your own PyU4V Docs
-------------------------

PyU4V docs have been built using Sphinx and included with the source PyU4V
package, however if you would like to build the docs from scratch use the
following commands::

   $ pip install sphinx
   $ pip install sphinx-rtd-theme
   $ cd PyU4V/docs
   $ make clean && make html

All of the necessary make files and sphinx configuration files are included
with PyU4V so you can build the docs after the required dependencies have been
installed.

Once the above commands have been run you will find newly generated html files
within the ``/PyU4V/docs/build`` folder. Open ``index.html`` within a
browser of your choosing to view the docs offline. Generating the docs is not
required, we have bundled the most up-to-date docs with PyU4V so you can still
navigate to ``/PyU4V/docs/build/index.html`` within your browser to view
PyU4V docs offline.

Disclaimer
----------

PyU4V 9.2 is distributed under the Apache 2.0 License. Unless required by
applicable law or agreed to in writing, software distributed under the Apache
2.0 License is distributed on an **"as is" basis, without warranties or**
**conditions of any kind**, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

.. URL LINKS

.. _Requests: https://realpython.com/python-requests/
.. _Six: https://six.readthedocs.io/
.. _urllib3: https://urllib3.readthedocs.io/en/latest/
.. _retired: https://pythonclock.org/
.. _TestTools: https://pypi.org/project/testtools/
.. _Tox: https://pypi.org/project/tox/
.. _prettytable: https://pypi.org/project/PrettyTable/