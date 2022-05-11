********************************
phdscripts
********************************

Scripts I am using in my PhD.

.. hidden 'Home' button as it's often not clear you need to click on the logo
  at the top of the page to get back to this file

.. toctree::
  :hidden:

  Home <self>

.. include everything in the setup folder:

.. toctree::
  :maxdepth: 1
  :caption: Setup:
  :glob:

  setup/*

.. include everything in the modules folder, with the 'public' page first:

.. toctree::
  :maxdepth: 2
  :caption: Functionality:
  :glob:

  modules/_public.rst
  modules/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
