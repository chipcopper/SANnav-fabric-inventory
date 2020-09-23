#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Sample code for retrieving a SANnav inventory via the API """

# Copyright: (c) 2020 Chip Copper <chip.copper@broadcom.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import requests
import urllib3

# Update these to point to a SANnav server
SANNAV_IP_ADDRESS = "10.155.2.143"
SANNAV_FOS_USERNAME = "cc"
SANNAV_FOS_PASSWORD = "password"

# Execute the retrieval of the fabric/switch information
def get_fabric_list(address, username, password):
    """ Get a list of fabrics and the switches in each returning a JSON structure """

    # Get the authenticating UUID to be used for all subsequent calls
    headers = {"username": username, "password": password, \
        "Content-Type": "application/json", "Accept": "application/json"}
    login_request = requests.post("https://" + address + "/external-api/v1/login/", \
        headers=headers, verify=False)
    response = login_request.json()
    session_id = response["sessionId"]
    headers = {"Authorization": session_id, "Content-Type": "application/json", \
        "Accept": "application/json"}

    # Get the fabric list and then iterate through each fabric for the switch list
    try:
        fab_list_request = \
            requests.get("https://" + address + "/external-api/v1/discovery/fabrics/", \
            headers=headers, verify=False)
        fab_list = fab_list_request.json()

        for fabric in fab_list["Fabrics"]:
            principal_switch_wwn = fabric['principalSwitchWwn']
            params = {"principalSwitchWWN": principal_switch_wwn}
            switch_list_request = \
                requests.get("https://" + address + "/external-api/v1/discovery/fabric-members/", \
                params=params, headers=headers, verify=False)
            switch_list = switch_list_request.json()
            fabric["Switches"] = switch_list["Switches"]

    except BaseException:
        print("Exception")

    # Close out the session
    _ = requests.post("https://" + address + "/external-api/v1/logout/", \
        headers=headers, verify=False)
    return fab_list

def main():
    """ Call the inventory function and print the results appropriately """


    fab_list = get_fabric_list(SANNAV_IP_ADDRESS, SANNAV_FOS_USERNAME, SANNAV_FOS_PASSWORD)

    # Print all known facts about the fabrics and the switches
    # Comment out this print statement if this code will be used to generate
    # an Ansible Tower inventory.
    print(json.dumps(fab_list))

    # This section of code formats the results to be in a format acceptable to Ansible Tower (awx).
    # To use it, unblock the following block of code and comment out the preceeding print statement.

    _ = """
    toAwx = {'_meta': {'hostvars': {}}}

    for fabric in fab_list["Fabrics"]:
        toAwx[fabric["name"]] = { 'hosts': []}
        for switch in fabric["Switches"]:
            toAwx[fabric["name"]]['hosts'].append(switch['ipAddress'])
    print(json.dumps(toAwx));
    """

if __name__ == "__main__":

    # If warnings are desired, comment out the following line
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
