#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Kevin Breit (@kbreit) <kevin.breit@kevinbreit.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: meraki_ms_static_route
short_description: Manage static routes on MS switches
description:
- Allows for creation, management, and visibility into static routes on Meraki MS switches.
options:
    state:
        description:
        - Create or modify an organization.
        type: str
        choices: [ present, query ]
        default: present
    net_name:
        description:
        - Name of network containing access points.
        type: str
    net_id:
        description:
        - ID of network containing access points.
        type: str
    number:
        description:
        - Number of SSID to apply firewall rule to.
        type: str
        aliases: [ ssid_number ]
    ssid_name:
        description:
        - Name of SSID to apply firewall rule to.
        type: str
        aliases: [ ssid ]
    allow_lan_access:
        description:
        - Sets whether devices can talk to other devices on the same LAN.
        type: bool
        default: yes
    rules:
        description:
        - List of firewall rules.
        type: list
        elements: dict
        suboptions:
            policy:
                description:
                - Specifies the action that should be taken when rule is hit.
                type: str
                choices: [ allow, deny ]
            protocol:
                description:
                - Specifies protocol to match against.
                type: str
                choices: [ any, icmp, tcp, udp ]
            dest_port:
                description:
                - Comma-seperated list of destination ports to match.
                type: str
            dest_cidr:
                description:
                - Comma-separated list of CIDR notation networks to match.
                type: str
            comment:
                description:
                - Optional comment describing the firewall rule.
                type: str
author:
- Kevin Breit (@kbreit)
extends_documentation_fragment: cisco.meraki.meraki
'''

EXAMPLES = r'''
- name: Create single firewall rule
  meraki_mr_l3_firewall:
    auth_key: abc123
    state: present
    org_name: YourOrg
    net_id: 12345
    number: 1
    rules:
      - comment: Integration test rule
        policy: allow
        protocol: tcp
        dest_port: 80
        dest_cidr: 192.0.2.0/24
    allow_lan_access: no
  delegate_to: localhost

- name: Enable local LAN access
  meraki_mr_l3_firewall:
    auth_key: abc123
    state: present
    org_name: YourOrg
    net_id: 123
    number: 1
    rules:
    allow_lan_access: yes
  delegate_to: localhost

- name: Query firewall rules
  meraki_mr_l3_firewall:
    auth_key: abc123
    state: query
    org_name: YourOrg
    net_name: YourNet
    number: 1
  delegate_to: localhost
'''

RETURN = r'''

'''

from ansible.module_utils.basic import AnsibleModule, json
from ansible_collections.cisco.meraki.plugins.module_utils.network.meraki.meraki import MerakiModule, meraki_argument_spec


def construct_payload(meraki):
    payload = {}
    if meraki.params['name'] is not None:
        payload['name'] = meraki.params['name']
    if meraki.params['subnet'] is not None:
        payload['subnet'] = meraki.params['subnet']
    if meraki.params['next_hop_ip'] is not None:
        payload['nextHopIp'] = meraki.params['next_hop_ip']
    if meraki.params['advertise_via_ospf_enabled'] is not None:
        payload['advertiseViaOspfEnabled'] = meraki.params['advertise_via_ospf_enabled']
    if meraki.params['prefer_over_ospf_routes_enabled'] is not None:
        payload['preferOverOspfRoutesEnabled'] = meraki.params['prefer_over_ospf_routes_enabled']
    return payload


def main():
    # define the available arguments/parameters that a user can pass to
    # the module
    argument_spec = meraki_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['present', 'query'], default='present'),
                         serial=dict(type='str'),
                         name=dict(type='str'),
                         subnet=dict(type='str'),
                         next_hop_ip=dict(type='str'),
                         advertise_via_ospf_enabled=dict(type='bool'),
                         prefer_over_ospf_routes_enabled=dict(type='bool'),
                         )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False,
                           )
    meraki = MerakiModule(module, function='ms_static_route')

    meraki.params['follow_redirects'] = 'all'

    query_urls = {'ms_static_route': '/devices/{serial}/switch/routing/staticRoutes'}
    create_urls = {'ms_static_route': '/devices/{serial}/switch/routing/staticRoutes'}

    meraki.url_catalog['get_all'].update(query_urls)
    meraki.url_catalog['create'] = create_urls

    payload = None

    # execute checks for argument completeness

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    if meraki.params['state'] == 'query':
        path = meraki.construct_path('get_all', custom={'serial': meraki.params['serial']})
        response = meraki.request(path, method='GET')
        meraki.result['data'] = response
        meraki.exit_json(**meraki.result)
    elif meraki.params['state'] == 'present':
        path = meraki.construct_path('create', custom={'serial': meraki.params['serial']})
        payload = construct_payload(meraki)
        response = meraki.request(path, method='POST', payload=json.dumps(payload))
        meraki.result['data'] = response
        meraki.result['changed'] = True
        meraki.exit_json(**meraki.result)


    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    meraki.exit_json(**meraki.result)


if __name__ == '__main__':
    main()
