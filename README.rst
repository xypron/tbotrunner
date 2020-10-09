tbot Runner
===========

Setup tbot
----------

.. code-block:: bash

    sudo apt-get install python3-paramiko
    git clone https://github.com/Rahix/tbot.git
    cd tbot/
    python3 setup.py install --user
    source completions.sh

Targets
-------

.. code-block:: bash

    tbot -l labconfig.py -b boardconfig.py -vv uboot_build
    tbot -l labconfig.py -b boardconfig.py -vv interactive_uboot
    tbot -l labconfig.py -b boardconfig.py -vv interactive_linux
