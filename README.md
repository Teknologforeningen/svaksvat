SvakSvat
========

* Branches
* master - stable branch
* staging - development branch

master should rebased from staging always when new functionality is needed.

Dependencies for SvakSvatGUI as Ubuntu packages:
================================================
* python3
* python3-virtualenv
* python3-pyqt4
* ldap-utils (for LDAP support)

Dependencies on Windows:
========================

# Install these #
* Python 3.X http://www.python.org/download/
* psycopg2 (For Python 3.X) http://www.stickpeople.com/projects/python/win-psycopg/
* git - My recommendation is http://windows.github.com/ and use its Git Shell to
* run SvakSvat

# To get pip and virtualenv working on windows: #
- Run these scripts on Windows:
 - distribute http://python-distribute.org/distribute_setup.py
 - pip https://raw.github.com/pypa/pip/master/contrib/get-pip.py
- Then run `pip install virtualenv`


Platform independent dependencies
=================================
Navigate to the repo root and run:
`
virtualenv3 --system-site-packages svaksvat_ve
`
Activate the virtualenv
- Linux/Mac: `source svaksvat_ve/bin/activate`
- Windows: `svaksvat_ve/Scripts/activate`

Install dependencies with pip:
`pip install -I -r requirements.txt`

Running with Vagrant
====================

Vagrant brings up a virtual machine, that hosts the database and maybe ldap in
the future. It is meant to make starting development easier.

You can install vagrant from http://vagrantup.com

You'll also need VirtualBox to manage the virtual machines http://virtualbox.org

Navigate to the repo root with the Vagrantfile and run:
```
vagrant plugin install vagrant-librarian-chef
vagrant up
```

Now is a good time to fetch a coffee. After the 'vagrant up' command finishes
you can run SvakSvat with the following commands:

```
cp svaksvat.cfg.vagrant svaksvat.cfg
python3 svaksvatgui.py
```

Enter `members` as username and password everywhere

To run svaksvat scripts:
ex.
`
python3 scripts/modulenadresser.py
`
