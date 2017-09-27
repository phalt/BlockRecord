===========
BlockRecord
===========

.. image:: https://img.shields.io/pypi/v/blockrecord.svg
        :target: https://pypi.python.org/pypi/blockrecord

.. image:: https://circleci.com/gh/phalt/blockrecord/tree/master.svg?style=svg
        :target: https://circleci.com/gh/phalt/blockrecord/tree/master

.. image:: https://codecov.io/gh/phalt/blockrecord/branch/master/graph/badge.svg?token=T9mYPv0Ep2
        :target: http://codecov.io/github/phalt/blockrecord?branch=master

.. image:: https://landscape.io/github/phalt/blockrecord/master/landscape.svg?style=flat
        :target: https://landscape.io/github/phalt/blockrecord/master
        :alt: Code Health


Blockchain-inspired record store for cryptographically verifiable auditing.

This provides the backend implementation of BlockRecord. Use this if you just want the chained record store.

You should use the BlockRecordNode_ project if you want to set up distributed nodes.


* Free software: GNU General Public License v3
* Documentation: https://phalt.github.io/blockrecord


Features
--------

* Block-based record chain.
* Cryptographically verifiable audit history of changes.
* Abstract backends for custom datastore.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`BlockRecordNode`: https://github.com/phalt/blockrecordnode
