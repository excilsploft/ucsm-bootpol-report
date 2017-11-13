*TEMPLATE MAP

This set of files is a python script that generates a file that can be digested by a d3.js map to display boot policy usage


ucsm-bootpol-report.py
----------------------

    This Script retrieves service profiles and the boot plicies, builds the relationships and then displays (with optional commandline param) a d3.js graph of the relationship.

    Dependcies include
       - Python 2.7.X
       - https://github.com/CiscoUcs/ucsmsdk
       - csv module
       - argparse module
       - getpass module

Usage
-----

	usage: ucsm-bootpol-report.py [-h] -i ID -u UCS [-p PORT] [-s] [-f FILTER]
								  [--templates] [--http]

	show the relationship

	optional arguments:
	  -h, --help            show this help message and exit
	  -i ID, --id ID        ucs management user id
	  -u UCS, --ucs UCS     ucs management ip
	  -p PORT, --port PORT  ucs management port
	  -s, --secure          https transport
	  -f FILTER, --filter FILTER service profile name filter
	  --templates           include templates
	  --http                run webserver on port 8000?


Warning
-------

Browser cache can make errant data show up
