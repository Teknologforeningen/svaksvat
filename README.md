Svaksvat
========

Dependencies for SvakSvatGUI as Ubuntu packages:
================================================
python3
python3-virtualenv
python3-pyqt4
ldap-utils (for LDAP support)

Dependencies on Windows:
========================

# Install these #
Python 3.X http://www.python.org/download/
psycopg2 (For Python 3.X) http://www.stickpeople.com/projects/python/win-psycopg/
git - I recommend http://windows.github.com/ and use it's Git Shell from now on

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
- Windows: `svaksvat_ve/bin/activate`

Install dependencies with pip:
`pip install -I -r requirements.txt`

Running
=======
To run on Ubuntu:
`
cp svaksvat.cfg.cp svaksvat.cfg
python3 svaksvatgui.py
`
To run svaksvat scripts:
ex.
`
python3 scripts/modulenadresser.py
`
