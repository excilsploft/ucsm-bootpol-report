# coding: utf-8
"""simple script for mapping template/profile dependencies"""
import json
import argparse
import getpass
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsconstants import NamingId
import SimpleHTTPServer
import SocketServer


CONST_HTTPD_PORT = 8001
CONST_BOOTP = 'bootp.json'


def get_sanimage(handle, boot_policy):
    """get the san image paths"""

    san_path =  handle.query_children(in_mo=boot_policy,
                                      class_id=NamingId.LSBOOT_SAN,
                                      hierarchy=True)
    ret_val = [sin.wwn for sin in san_path if 'sanimgpath-' in sin.rn]
    return ret_val

def get_boot_policy(handle):
    """get the boot policy associated with a template"""

    boot_policies = handle.query_classid(NamingId.LSBOOT_POLICY)
    boot_dn_list = [{'name': b.name, 'dn': b.dn,
                    'wwn': get_sanimage(handle, b)} for b in boot_policies]


    return boot_dn_list

def get_templates(handle):
    """get the templates"""
    filter_string = '(type, "updating-template", type="eq")'

    templates = handle.query_classid(NamingId.LS_SERVER,
                                     filter_str=filter_string)
    template_dn_list = [{'dn':t.dn, 'name': t.name, 'boot':
                        t.oper_boot_policy_name} for t in templates]
    return template_dn_list

def get_instances(handle, filter_string=None):
    """get the instances"""

    if filter_string:
        sp_filter = '(type, "instance", type="eq") and (name, "{0}", type="re", flag="I")'.format(filter_string)
    else:
        sp_filter = '(type, "instance", type="eq")'

    service_profiles = handle.query_classid(NamingId.LS_SERVER,
                                            filter_str=sp_filter)

    profile_dn_list = [{'name': p.name, 'template': p.oper_src_templ_name,
                       'boot': p.oper_boot_policy_name}
                       for p in service_profiles]
    return profile_dn_list

def match_boot(dn, boot_list):
    """ given a dn return a boot policy or None"""

    ret_val = None
    for boot_p in boot_list:
        if dn == boot_p['dn']:
            ret_val = boot_p
            break
    return ret_val


def match_template(dn, template_list):
    """ given a dn return a template or None"""

    ret_val = None
    for template in template_list:
        if dn == template['dn']:
            ret_val = template
            break
    return ret_val

def bootp_json(instance_list, boot_list):
    """build a boot policy oriented json"""

    output_json = {'nodes':[], 'links':[]}
    for bootp in boot_list:
        output_json['nodes'].append({'id': bootp['name'], 'group': 0, "wwn":
                                    bootp['wwn']})

    for instance in instance_list:
        output_json['nodes'].append({'id': instance['name'], 'group': 7})

    for bootp in boot_list:
        for instance in instance_list:
            if bootp['dn'] == instance['boot']:
                output_json['links'].append({'source': bootp['name'],
                                             'target': instance['name'],
                                             'value': 1})

    return output_json



def instance_json(template_list, instance_list, boot_list):
    """build a json output """

    output_json = {'name': 'instance', 'children':[]}

    for instance in instance_list:
        sp = {'name': instance['name'], 'children': []}
        template = match_template(instance['template'], template_list)

        if template:
            tmpl = {'name': template['name'], 'children': []}
            bootpol = match_boot(template['boot'], boot_list)
            if bootpol:
                tmpl['children'].append({'name': bootpol['name']})

            sp['children'].append(tmpl)

        output_json['children'].append(sp)

    return output_json


def main(args):
    """main function"""

    if args.id:
        username = args.id

    if args.port:
        port = args.port
    else:
        port = 443

    if args.secure:
        secure=True
    else:
        secure=False

    handle = UcsHandle(args.ucs, username=args.id,
                       password=getpass.getpass(prompt="UCSM Password: "),
                       secure=secure, port=port)
    #handle = UcsHandle('localhost', 'admin', 'admin', secure=False, port=8090)
    handle.login()

    instance_list = get_instances(handle, args.filter)
    template_list = get_templates(handle)
    boot_list = get_boot_policy(handle)

    handle.logout()

    if args.templates:
        output_json = bootp_json(instance_list, boot_list)
    else:
        output_json = instance_json(template_list, instance_list, boot_list)

    with open(CONST_BOOTP, 'wb') as file_out:
        json.dump(output_json, file_out)

    if args.http:
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("",CONST_HTTPD_PORT), handler)

        print "point browser to http://localhost:8000"
        httpd.serve_forever()


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(description="""show the relationship""")
    PARSER.add_argument('-i', '--id', help='ucs management user id', 
                        required=True)
    PARSER.add_argument('-u', '--ucs', help='ucs management ip', required=True)
    PARSER.add_argument('-p', '--port', help='port', required=False)
    PARSER.add_argument('-s', '--secure', help='secure',
                        action='store_true')
    PARSER.add_argument('-f', '--filter', help='service profile name filter',
                        required=False)
    PARSER.add_argument('--templates', help='include templates', required=False,
                         action='store_true')
    PARSER.add_argument('--http', help='run webserver on port 8000?',
                        required=False, action='store_true')

    ARGS = PARSER.parse_args()


    main(ARGS)
