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

