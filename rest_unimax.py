# The MIT License (MIT)
# Copyright (c) 2016 Dell Inc. or its subsidiaries.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config
import logging.config
from rest_requests import RestRequests

# register configuration file
LOG = logging.getLogger('PyU4V')
CONF_FILE = 'PyU4V.conf'
logging.config.fileConfig(CONF_FILE)
CFG = Config.ConfigParser()
CFG.read(CONF_FILE)

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


class rest_functions:
    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=False, cert=None):
        self.array_id = CFG.get('setup', 'array')
        if not username:
            username = CFG.get('setup', 'username')
        if not password:
            password = CFG.get('setup', 'password')
        if not server_ip:
            server_ip = CFG.get('setup', 'server_ip')
        if not port:
            port = CFG.get('setup', 'port')
        if not verify:
            verify = CFG.getboolean('setup', 'verify')
        if not cert:
            cert = CFG.get('setup', 'cert')
        base_url = 'https://%s:%s/univmax/restapi' % (server_ip, port)
        self.rest_client = RestRequests(username, password, verify,
                                        cert, base_url)

    def set_array(self, array):
        """Change to a different array.
        :param array: The VMAX serial number
        """
        self.array_id = array

    def close_session(self):
        """Close the current rest session
        """
        response = self.rest_client.close_session()
        return response

    ###############################
    # system functions
    ###############################

    def get_all_alerts(self, filters=None):
        """Queries for a list of All Alert ids across all symmetrix arrays.
        Optionally can be filtered by: create_date_milliseconds(=<>),
        description(=<>), type, severity, state, created_date, acknowledged.
        :param filters: dict of filters - optional
        :return: server response - dict
        """
        target_uri = "univmax/restapi/system/alert"
        return self.rest_client.rest_request(target_uri, GET, filters)

    def get_all_jobs(self, filters=None):
        """Queries for a list of Job ids across all symmetrix arrays.
        Optionally can be filtered by: scheduled_date, name, completed_date,
        username, scheduled_date_milliseconds,
        last_modified_date_milliseconds, last_modified_date,
        completed_date_milliseconds (all params including =,<, or >),
        status (=).
        :param filters: dict of filters - optional
        :return: server response - dict
        """
        target_uri = "univmax/restapi/system/job"
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def get_symmetrix_array(self, array_id=None):
        """Returns a list of arrays, or details on a specific array.
        :param array_id: the array serial number
        :return: server response - dict
        """
        target_uri = "univmax/restapi/system/symmetrix"
        if array_id:
            target_uri += "/%s" % array_id
        return self.rest_client.rest_request(target_uri, GET)

    def get_array_jobs(self, jobID=None, filters=None):
        """Call queries for a list of Job ids for the specified symmetrix.
        The optional filters are: scheduled_date, name, completed_date,
        username, scheduled_date_milliseconds,
        last_modified_date_milliseconds, last_modified_date,
        completed_date_milliseconds (all params including =,<, or >),
        status (=).
        :param jobID: specific ID of the job (optional)
        :param filters: dict of filters - optional
        :return: server response (dict)
        """
        target_uri = "/system/symmetrix/%s/job" % self.array_id
        if jobID:
            target_uri += "/%s" % jobID
        if jobID and filters:
            LOG.error("jobID and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def get_array_alerts(self, alert_id=None, filters=None):
        """Queries for a list of Alert ids for the specified symmetrix.
        The optional filters are: create_date_milliseconds(=<>),
        description(=<>), type, severity, state, created_date, acknowledged.
        :param alert_id: specific id of the alert - optional
        :param filters: dict of filters - optional
        :return: server response - dict
        """
        target_uri = "/system/symmetrix/%s/alert" % self.array_id
        if alert_id:
            target_uri += "/%s" % alert_id
        if alert_id and filters:
            LOG.error("alert_id and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def acknowledge_array_alert(self, alert_id):
        """Acknowledge a specified alert.
        Acknowledge is the only "PUT" (edit) option available.
        :param alert_id: the alert id - string
        :return: server response - dict
        """
        target_uri = ("/system/symmetrix/%s/alert/%s" %
                      (self.array_id, alert_id))
        payload = {"editAlertActionParam": "ACKNOWLEDGE"}
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=payload)

    def delete_alert(self, alert_id):
        """Delete a specified alert.
        :param alert_id: the alert id - string
        :return: status code
        """
        target_uri = ("/system/symmetrix/%s/alert/%s" %
                      (self.array_id, alert_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_uni_version(self):
        target_uri = "/system/version"
        return self.rest_client.rest_request(target_uri, GET)

    #############################
    ### SLOProvisioning functions
    #############################

    # director

    def get_director(self, director=None):
        """Queries for details of Symmetrix directors for a symmetrix
        :param director: the director ID e.g. FA-1D - optional
        :return: the server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/director" % self.array_id
        if director:
            target_uri += "/%s" % director
        return self.rest_client.rest_request(target_uri, GET)

    def get_director_port(self, director, port_no=None, filters=None):
        """Get details of the symmetrix director port.
        Can be filtered by optional parameters, please see documentation.
        :param director: the director ID e.g. FA-1D
        :param port_no: the port number e.g. 1 - optional
        :param filters: optional filters - dict
        :return: the server response - dict
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/director/%s/port"
                      % (self.array_id, director))
        if port_no:
            target_uri += "/%s" % port_no
        if port_no and filters:
            LOG.error("portNo and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def get_port_identifier(self, director, port_no):
        """Get the identifier (if wwn or iqn) of the physical port.
        :param director: the ID of the director
        :param port_no: the number of the port
        :return: wwn (FC) or iqn (iscsi), or None
        """
        info = self.get_director_port(director, port_no)
        try:
            identifier = info["symmetrixPort"][0]["identifier"]
            return identifier
        except KeyError:
            LOG.error("Cannot retrieve port information")
            return None

    # host

    def get_hosts(self, host_id=None, filters=None):
        """Get details on host(s) on the array.
        See documentation for applicable filters - only valid
        if no host is specified.
        :param host_id: the name of the host, optional
        :param filters: optional list of filters - dict
        :return: server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/host" % self.array_id
        if host_id:
            target_uri += "/%s" % host_id
        if host_id and filters:
            LOG.error("Host_id and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, filters)

    def create_host(self, host_name, initiator_list, host_flags=None):
        """Create a host with the given initiators.
        The initiators must not be associated with another host.
        :param host_name: the name of the new host
        :param initiator_list: list of initiators
        :param host_flags: dictionary of optional host flags to apply
        :return: server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/host" % self.array_id
        new_ig_data = ({"hostId": host_name, "initiatorId": initiator_list})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=new_ig_data)

    def modify_host(self, host_id, host_flag_dict=None,
                    remove_init_list=None, add_init_list=None, new_name=None):
        """Modify an existing host.
        Only one parameter can be modified at a time.
        :param host_id: the host name
        :param host_flag_dict: dictionary of host flags
        :param remove_init_list: list of initiators to be removed
        :param add_init_list: list of initiators to be added
        :param new_name: new host name
        :return: server response - dict
        """
        if host_flag_dict:
            edit_host_data = ({"editHostActionParam": {
                "setHostFlagsParam": {"hostFlags": host_flag_dict}}})
        elif remove_init_list:
            edit_host_data = ({"editHostActionParam": {
                "removeInitiatorParam": {"initiator": remove_init_list}}})
        elif add_init_list:
            edit_host_data = ({"editHostActionParam": {
                "addInitiatorParam": {"initiator": add_init_list}}})
        elif new_name:
            edit_host_data = {"editHostActionParam": {
                "renameHostParam": {"new_host_name": new_name}}}
        else:
            LOG.error("No modify host parameters chosen - please supply one "
                      "of the following: host_flag_dict, remove_init_list, "
                      "add_init_list, or new_name.")
            raise Exception
        target_uri = ("/sloprovisioning/symmetrix/%s/host/%s"
                      % (self.array_id, host_id))
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_host_data)

    def delete_host(self, host_id):
        """Delete a given host.
        Cannot delete if associated with a masking view
        :param host_id: name of the host
        :return: status code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/host/%s"
                      % (self.array_id, host_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_mvs_from_host(self, host_id):
        """Retrieve masking view information for a specified host.
        :param host_id: the name of the host
        :return: list of masking views or None
        """
        response = self.get_hosts(host_id=host_id)
        try:
            mv_list = response["host"][0]["maskingview"]
            return mv_list
        except KeyError:
            LOG.debug("No masking views found for host %s." % host_id)
            return None

    def get_initiator_ids_from_host(self, host_id):
        """Get initiator details from a host.
        :param host_id: the name of the host
        :return: list of initiator IDs, or None
        """
        response = self.get_hosts(host_id=host_id)
        try:
            initiator_list = response["host"][0]["initiator"]
            return initiator_list
        except KeyError:
            return None

    # hostgroup

    def get_hostgroups(self, hostgroup_id=None, filters=None):
        """Get details on hostgroup(s) on the array.
        See unisphere documentation for applicable filters - only valid
        if no host is specified.
        :param hostgroup_id: the name of the hostgroup, optional
        :param filters: optional list of filters - dict
        :return: server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/hostgroup" % self.array_id
        if hostgroup_id:
            target_uri += "/%s" % hostgroup_id
        if hostgroup_id and filters:
            LOG.error("hostgroup_id and filters are mutually exclusive "
                      "options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, filters)

    def create_hostgroup(self, hostgroup_id, host_list, host_flags=None):
        """Create a hostgroup containing the given hosts.
        :param hostgroup_id: the name of the new hostgroup
        :param host_list: list of hosts
        :param host_flags: dictionary of optional host flags to apply
        :return: server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/hostgroup" % self.array_id
        new_ig_data = ({"hostId": host_list, "hostGroupId": hostgroup_id})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=new_ig_data)

    def modify_hostgroup(self, hostgroup_id, host_flag_dict=None,
                         remove_host_list=None, add_host_list=None,
                         new_name=None):
        """Modify an existing hostgroup.
        Only one parameter can be modified at a time.
        :param hostgroup_id: the name of the hostgroup
        :param host_flag_dict: dictionary of host flags
        :param remove_host_list: list of hosts to be removed
        :param add_host_list: list of hosts to be added
        :param new_name: new name of the hostgroup
        :return: server response - dict
        """
        if host_flag_dict:
            edit_host_data = ({"editHostGroupActionParam": {
                "setHostGroupFlagsParam": {"hostFlags": host_flag_dict}}})
        elif remove_host_list:
            edit_host_data = ({"editHostGroupActionParam": {
                "removeHostParam": {"host": remove_host_list}}})
        elif add_host_list:
            edit_host_data = ({"editHostGroupActionParam": {
                "addHostParam": {"host": add_host_list}}})
        elif new_name:
            edit_host_data = {"editHostGroupActionParam": {
                "renameHostGroupParam": {"new_host_group_name": new_name}}}
        else:
            LOG.error("No modify hostgroup parameters chosen - please supply "
                      "one of the following: host_flag_dict, "
                      "remove_host_list, add_host_list, or new_name.")
            raise Exception
        target_uri = ("/sloprovisioning/symmetrix/%s/hostgroup/%s"
                      % (self.array_id, hostgroup_id))
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_host_data)

    def delete_hostgroup(self, hostgroup_id):
        """Delete a given hostgroup.
        Cannot delete if associated with a masking view
        :param hostgroup_id: name of the hostgroup
        :return: status code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/hostgroup/%s"
                      % (self.array_id, hostgroup_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    # initiators

    def get_initiators(self, initiator_id=None, filters=None):
        """Lists initiators on a given array.
        See UniSphere documenation for full list of filters.
        Can filter by initiator_id OR filters.
        :param filters: Optional filters - dict
        :return: initiator list
        """
        target_uri = "/sloprovisioning/symmetrix/%s/initiator" % self.array_id
        if initiator_id:
            target_uri += "/%s" % initiator_id
        if initiator_id and filters:
            LOG.error("Initiator_id and filters are mutually exclusive")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def modify_initiator(self, initiator_id, removeMaskingEntry=None,
                         replace_init=None, rename_alias=None,
                         set_fcid=None, initiator_flags=None):
        """Modify an initiator.
        Only one parameter can be edited at a time.
        :param initiator_id: the initiator id
        :param removeMaskingEntry: string - "true" or "false"
        :param replace_init: Id of the new initiator
        :param rename_alias: tuple ('new node name', 'new port name')
        :param set_fcid: set fcid value - string
        :param initiator_flags: dictionary of initiator flags to set
        :return: server response - dict
        """
        if removeMaskingEntry:
            edit_init_data = ({"editInitiatorActionParam": {
                "removeMaskingEntry": removeMaskingEntry}})
        elif replace_init:
            edit_init_data = ({"editInitiatorActionParam": {
                "replaceInitiatorParam": {"new_initiator": replace_init}}})
        elif rename_alias:
            edit_init_data = ({"editInitiatorActionParam": {
                "renameAliasParam": {"port_name": rename_alias[0],
                                     "node_name": rename_alias[1]}}})
        elif set_fcid:
            edit_init_data = ({"editInitiatorActionParam": {
                "initiatorSetAttributesParam": {"fcidValue": set_fcid}}})
        elif initiator_flags:
            edit_init_data = ({"editInitiatorActionParam": {
                "initiatorSetFlagsParam": {
                    "initiatorFlags": initiator_flags}}})
        else:
            LOG.error("No modify initiator parameters chosen - please supply "
                      "one of the following: removeMaskingEntry, "
                      "replace_init, rename_alias, set_fcid, "
                      "initiator_flags.")
            raise Exception
        target_uri = ("/sloprovisioning/symmetrix/%s/initiator/%s"
                      % (self.array_id, initiator_id))
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_init_data)

    def is_initiator_in_host(self, initiator):
        """Check to see if a given initiator is already assigned to a host
        :param initiator: the initiator ID
        :return: bool
        """
        param = {'in_a_host': 'true', 'initiator_hba': initiator}
        response = self.get_initiators(filters=param)
        try:
            if response['message'] == 'No Initiators Found':
                return False
        except KeyError:
            return True

    # masking view

    def get_masking_views(self, masking_view_id=None, filters=None):
        """Get a masking view or list of masking views.
        If masking_view_id, return details of a particular masking view.
        Either masking_view_id or filters can be set
        :param masking_view_id: the name of the masking view
        :param filters: dictionary of filters
        :return: server response - dict
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview"
                      % self.array_id)
        if masking_view_id:
            target_uri += "/%s" % masking_view_id
        if masking_view_id and filters:
            LOG.error("masking_view_id and filters are mutually exclusive")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def create_masking_view_existing_components(
            self, port_group_name, masking_view_name,
            storage_group_name, host_name=None,
            host_group_name=None):
        """Create a new masking view using existing groups.
        Must enter either a host name or a host group name, but
        not both.
        :param port_group_name: name of the port group
        :param masking_view_name: name of the new masking view
        :param storage_group_name: name of the storage group
        :param host_name: name of the host (initiator group)
        :param host_group_name: name of host group
        :return: server response - dict
        """
        if host_name:
            host_details = {"useExistingHostParam": {"hostId": host_name}}
        elif host_group_name:
            host_details = {"useExistingHostGroupParam": {
                "hostGroupId": host_group_name}}
        else:
            LOG.error("Must enter either a host name or a host group name")
            raise Exception()
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview"
                      % self.array_id)

        mv_payload = {"portGroupSelection": {
            "useExistingPortGroupParam": {
                "portGroupId": port_group_name}},
            "maskingViewId": masking_view_name,
            "hostOrHostGroupSelection": host_details,
            "storageGroupSelection": {
                "useExistingStorageGroupParam": {
                    "storageGroupId": storage_group_name}}}
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=mv_payload)

    def modify_masking_view(self, masking_view_id, new_name):
        """Modify an existing masking view.
        Currently, the only supported modification is "rename".
        :param masking_view_id: the current name of the masking view
        :param new_name: the new name of the masking view
        :return: server response - dict
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s"
                      % self.array_id, masking_view_id)
        mv_payload = {"editMaskingViewActionParam": {
            "renameMaskingViewParam": {"new_masking_view_name": new_name}}}
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=mv_payload)

    def delete_masking_view(self, masking_view_id):
        """Delete a given masking view.
        :param masking_view_id: the name of the masking view
        :return: status code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s"
                      % (self.array_id, masking_view_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_host_from_mv(self, masking_view_id):
        """Given a masking view, get the associated host.
        :param masking_view_id: the name of the masking view
        :return:
        """
        response = self.get_masking_views(masking_view_id=masking_view_id)
        try:
            hostId = response['maskingView'][0]['hostId']
            return hostId
        except KeyError:
            LOG.error("Error retrieving host ID from masking view")

    def get_sg_from_mv(self, masking_view_id):
        """Given a masking view, get the associated storage group.
        :param masking_view_id: the masking view name
        :return: the name of the storage group
        """
        response = self.get_masking_views(masking_view_id=masking_view_id)
        try:
            for r in response["maskingView"]:
                return r["storageGroupId"]
        except KeyError:
            LOG.error("Error retrieving storageGroupId from masking view")

    def get_pg_from_mv(self, masking_view_id):
        """Given a masking view, get the associated port group.
        :param masking_view_id: the masking view name
        :return: the name of the port group
        """
        response = self.get_masking_views(masking_view_id=masking_view_id)
        try:
            for r in response["maskingView"]:
                return r["portGroupId"]
        except KeyError:
            LOG.error("Error retrieving portGroupId from masking view")

    def get_mv_connections(self, mv_name):
        """Get all connection information for a given masking view.
        :param mv_name: the name of the masking view
        :return: connection information
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s/"
                      "connections" % (self.array_id, mv_name))
        return self.rest_client.rest_request(target_uri, GET)

    # port

    def get_ports(self, filters=None):
        """Queries for a list of Symmetrix port keys.
        Note a mixture of Front end, back end and RDF port specific values
        are not allowed. See UniSphere documentation for possible values.
        :param filters: dictionary of filters e.g. {'vnx_attached': 'true'}
        :return: server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/port" % self.array_id
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    # portgroup

    def get_portgroups(self, portgroup_id=None, filters=None):
        """Get portgroup(s) details.
        :param portgroup_id: the name of the portgroup
        :param filters: dictionary of filters
        :return: server response - dict
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup"
                      % self.array_id)
        if portgroup_id:
            target_uri += "/%s" % portgroup_id
        if portgroup_id and filters:
            LOG.error("portgroup_id and filters are mutually exclusive")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def create_portgroup(self, portgroup_id, director_id, port_id):
        """Create a new portgroup.
        :param portgroup_id: the name of the new port group
        :param director_id: the directoy id
        :param port_id: the port id
        :return: server response - dict
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup"
                      % self.array_id)
        pg_payload = ({"portGroupId": portgroup_id,
                       "symmetrixPortKey": [{"directorId": director_id,
                                             "portId": port_id}]})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=pg_payload)

    def modify_portgroup(self, portgroup_id, remove_port=None, add_port=None,
                         rename_portgroup=None):
        """Modify an existing portgroup.
        Only one parameter can be modified at a time.
        :param portgroup_id: the name of the portgroup
        :param remove_port: tuple of port details ($director_id, $portId)
        :param add_port: tuple of port details ($director_id, $portId)
        :param rename_portgroup: new portgroup name
        :return: server response - dict
        """
        if remove_port:
            edit_pg_data = ({"editPortGroupActionParam": {"removePortParam": {
                "port": [{"directorId": remove_port[0],
                          "portId": remove_port[1]}]}}})
        elif add_port:
            edit_pg_data = ({"editPortGroupActionParam": {"addPortParam": {
                "port": [{"directorId": add_port[0],
                          "portId": add_port[1]}]}}})
        elif rename_portgroup:
            edit_pg_data = ({"editPortGroupActionParam": {
                "renamePortGroupParam": {
                    "new_port_group_name": rename_portgroup}}})
        else:
            LOG.error("No modify portgroup parameters set - please set one "
                      "of the following: remove_port, add_port, or "
                      "rename_portgroup.")
            raise Exception()
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup/%s"
                      % self.array_id, portgroup_id)
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_pg_data)

    def delete_portgroup(self, portgroup_id):
        """Delete a portgroup.
        :param portgroup_id: the name of the portgroup
        :return: server response
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup/%s"
                      % self.array_id, portgroup_id)
        return self.rest_client.rest_request(target_uri, DELETE)

    def extract_directorId_pg(self, portgroup):
        """Get the symm director information from the port group.
        :param portgroup: the name of the portgroup
        :return: the director information
        """
        info = self.get_portgroups(portgroup_id=portgroup)
        try:
            portKey = info["portGroup"][0]["symmetrixPortKey"]
            return portKey
        except KeyError:
            LOG.error("Cannot find port key information from given portgroup")

    # SLO

    def get_SLO(self, SLO_Id=None):
        """Gets a list of available SLO's on a given array, or returns
        details on a specific SLO if one is passed in in the parameters.
        :param SLO_Id: the service level agreement, optional
        :return: server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/slo" % self.array_id
        if SLO_Id:
            target_uri += "/%s" % SLO_Id
        return self.rest_client.rest_request(target_uri, GET)

    def modify_slo(self, SLO_Id, new_name):
        """Modify an SLO.
        Currently, the only modification permitted is renaming.
        :param SLO_Id: the current name of the slo
        :param new_name: the new name for the slo
        :return: server response - dict
        """
        edit_slo_data = ({"editSloActionParam": {
            "renameSloParam": {"sloId": new_name}}})
        target_uri = ("/sloprovisioning/symmetrix/%s/slo/%s" %
                      self.array_id, SLO_Id)
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_slo_data)

    # SRP

    def get_SRP(self, SRP=None):
        """Gets a list of available SRP's on a given array, or returns
        details on a specific SRP if one is passed in in the parameters.
        :param SRP: the storage resource pool, optional
        :return: SRP details
        """
        target_uri = "/sloprovisioning/symmetrix/%s/srp" % self.array_id
        if SRP:
            target_uri += "/%s" % SRP
        return self.rest_client.rest_request(target_uri, GET)

    # storage group functions.
    #  Note: Can only create a volume in relation to a sg

    def get_sg(self, sg_id=None, filters=None):
        """Gets details of all storage groups on a given array, or returns
        details on a specific sg if one is passed in in the parameters.
        :param sg_id: the storage group name, optional
        :param filters: dictionary of filters e.g.
                       {'child': 'true', 'srp_name': '=SRP_1'}
        :return: sg details
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup"
                      % self.array_id)
        if sg_id:
            target_uri += "/%s" % sg_id
        if sg_id and filters:
            LOG.error("sg_id and filters are mutually exclusive")
            raise Exception()
        return self.rest_client.rest_request(target_uri, GET)

    def create_non_empty_storagegroup(
            self, srpID, sg_id, slo, workload, num_vols, vol_size,
            capUnit):
        """Create a new storage group with the specified volumes.
        Generates a dictionary for json formatting and calls the
        create_sg function to create a new storage group with the
        specified volumes.
        :param srpID: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param num_vols: the amount of volumes to be created
        :param vol_size: the size of each volume
        :param capUnit: the capacity unit (MB, GB)
        :return: message
        """
        new_sg_data = ({"srpId": srpID, "storageGroupId": sg_id,
                        "sloBasedStorageGroupParam": [{
                            "sloId": slo, "workloadSelection": workload,
                            "num_of_vols": num_vols,
                                "volumeAttribute": {
                                "volume_size": vol_size,
                                "capacityUnit": capUnit}}]})
        return self._create_sg(new_sg_data)

    def create_non_empty_compressed_storagegroup(
            self, srpID, sg_id, slo, workload, num_vols, vol_size,
            capUnit):
        """Create a new storage group with the specified volumes.
        Generates a dictionary for json formatting and calls the
        create_sg function to create a new storage group with the
        specified volumes.
        :param srpID: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param num_vols: the amount of volumes to be created
        :param vol_size: the size of each volume
        :param capUnit: the capacity unit (MB, GB)
        :return: message
        """
        new_sg_data = ({"srpId": srpID, "storageGroupId": sg_id,
                        "emulation": "FBA",
                        "sloBasedStorageGroupParam": [{
                            "sloId": slo, "workloadSelection": workload,
                            "noCompression": False,
                            "num_of_vols": num_vols,
                                "volumeAttribute": {
                                "volume_size": vol_size,
                                "capacityUnit": capUnit}}]})


        return self._create_compressed_sg(new_sg_data)


    # create an empty storage group
    def create_empty_sg(self, srpID, sg_id, slo, workload):
        """Generates a dictionary for json formatting and calls the create_sg function
        to create an empty storage group
        :param srpID: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :return: message
        """
        new_sg_data = ({"srpId": srpID, "storageGroupId": sg_id,
                        "sloBasedStorageGroupParam": [{
                                            "num_of_vols": 1,
                                            "sloId": slo,
                                            "workloadSelection": workload,
                                            "volumeAttribute": {
                                                "volume_size": "0",
                                                "capacityUnit": "GB"}}],
                        "create_empty_storage_group": "true"})
        return self._create_sg(new_sg_data)

    def _create_sg(self, new_sg_data):
        """Creates a new storage group with supplied specifications,
        given in dictionary form for json formatting
        :param new_sg_data: the payload of the request
        :return: response - dict
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup"
                      % self.array_id)
        return self.rest_client.rest_request(
            target_uri, POST, request_object=new_sg_data)

    def _create_compressed_sg(self, new_sg_data):
        """Creates a new storage group with supplied specifications,
        given in dictionary form for json formatting
        :param new_sg_data: the payload of the request
        :return: response - dict
        """
        target_uri = ("/83/sloprovisioning/symmetrix/%s/storagegroup"
                      % self.array_id)
        return self.rest_client.rest_request(
            target_uri, POST, request_object=new_sg_data)

    def modify_storagegroup(self, sg_id, edit_sg_data):
        """Edits an existing storage group
        :param sg_id: the name of the storage group
        :param edit_sg_data: the payload of the request
        :return: message
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup/%s"
                      % (self.array_id, sg_id))
        return self.rest_client.rest_request(
            target_uri, PUT, request_object=edit_sg_data)

    def add_existing_vol_to_sg(self, sg_id, vol_id):
        """Expand an existing storage group by adding new volumes.
        :param sg_id: the name of the storage group
        :param vol_id: the device id of the volume
        :return: message
        """
        addVolData = {"editStorageGroupActionParam": {
                                    "addVolumeParam": {
                                            "volumeId": [vol_id]}}}
        return self.modify_storagegroup(sg_id, addVolData)

    def add_new_vol_to_storagegroup(self, sg_id, num_vols, vol_size, capUnit):
        """Expand an existing storage group by adding new volumes.
        :param sg_id: the name of the storage group
        :param num_vols: the number of volumes
        :param vol_size: the size of the volumes
        :param capUnit: the capacity unit
        :return: message
        """
        expand_sg_data = ({"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "num_of_vols": num_vols,
                "emulation": "FBA",
                "volumeAttribute": {
                    "volume_size": vol_size,
                    "capacityUnit": capUnit
                },
                "create_new_volumes": "true"},}})
        return self.modify_storagegroup(sg_id, expand_sg_data)

    def remove_vol_from_storagegroup(self, sg_id, volID):
        """Remove a volume from a given storage group
        :param sg_id: the name of the storage group
        :param volID: the device id of the volume
        :return: message
        """
        del_vol_data = ({"editStorageGroupActionParam": {
            "removeVolumeParam": {
                "volumeId": [volID]}}})
        return self.modify_storagegroup(sg_id, del_vol_data)

    def delete_sg(self, sg_id):
        """Delete a given storage group.
        A storage group cannot be deleted if it
        is associated with a masking view
        :param sg_id: the name of the storage group
        :return: server response
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup/%s"
                     % (self.array_id, sg_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_mv_from_sg(self, storageGroup):
        """Get the associated masking view(s) from a given storage group
        :param storageGroup: the name of the storage group
        :return: Masking view list, or None
        """
        response = self.get_sg(storageGroup)
        mvlist = response["storageGroup"][0]["maskingview"]
        if len(mvlist) > 1:
            return mvlist
        else:
            return None

    def set_hostIO_limit_IOPS(self,storageGroup,IOPS,dynamicDistribution):
       """Set the HOSTIO Limits on an existing storage group
       :param storageGroup: String up to 32 Characters
       :param dynamicDistribution: valid values Always,Never,OnFailure
       :param IOPS integer value Min Value 100, must be specified to nearest 100, e.g.202 is not a valid value
       :return: Status Code
       """
       target_uri = "/sloprovisioning/symmetrix/%s/storagegroup/%s" % (self.array_id, storageGroup)
       iolimits = {"editStorageGroupActionParam": {"setHostIOLimitsParam": {"host_io_limit_io_sec": IOPS,
                                                                            "dynamicDistribution": dynamicDistribution}}}
       return self.rest_client.rest_request(target_uri,PUT, request_object=iolimits)
    # volume

    def get_volumes(self, volID=None, filters=None):
        """Gets details of volume(s) from array.
        :param volID: the volume's device ID
        :param filters: dictionary of filters
        :return: server response - dict
        """
        target_uri = "/sloprovisioning/symmetrix/%s/volume" % self.array_id
        if volID:
            target_uri += volID
        if volID and filters:
            LOG.error("volID and filters are mutually exclusive.")
            raise Exception()
        return self.rest_client.rest_request(target_uri, GET,
                                             params=filters)

    def delete_volume(self, vol_id):
        """Delete a specified volume off the array.
        Note that you cannot delete volumes with any associations/ allocations
        :param vol_id: the device ID of the volume
        :return: server response
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/volume/%s"
                      % (self.array_id, vol_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_deviceId_from_volume(self, vol_identifier):
        """Given the volume identifier (name), return the device ID
        :param vol_identifier: the identifier of the volume
        :return: the device ID of the volume
        """
        response = self.get_volumes(filters=(
            {'volume_identifier': vol_identifier}))
        result = response['resultList']['result'][0]
        return result['volumeId']

    def get_vols_from_SG(self, sgID):
        """Retrieve volume information associated with a particular sg
        :param sgID: the name of the storage group
        :return: list of device IDs of associated volumes
        """
        vols = []
        response = self.get_volumes(filters={'storageGroupId': sgID})
        vol_list = response['resultList']['result']
        for vol in vol_list:
            vol_id = vol['volumeId']
            vols.append(vol_id)
        return vols

    def get_SG_from_vols(self, vol_id):
        """Retrieves sg information for a specified volume.
        Note that a FAST managed volume cannot be a
        member of more than one storage group.
        :param vol_id: the device ID of the volume
        :return: list of storage groups, or None
        """
        response = self.get_volumes(volID=vol_id)
        try:
            sglist = response["volume"][0]["storageGroupId"]
            return sglist
        except KeyError:
            return None

    # workloadtype

    def get_workload(self):
        """Gets details of all available workload types.
        :return: workload details
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/workloadtype"
                      % self.array_id)
        return self.rest_client.rest_request(target_uri, GET)

    ###########################
    #   Replication functions
    ###########################

    # snapshots

    def check_snap_capabilities(self):
        """Check what replication facilities are available
        :return: Replication information
        """
        target_uri = "/replication/capabilities/symmetrix"
        return self.rest_client.rest_request(target_uri, GET)

    def get_snap_sg(self, sg_id):
        """get snapshot information on a particular sg
        :param sg_id: the name of the storage group
        :return: snapshot information
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot"
                      % (self.array_id, sg_id))
        return self.rest_client.rest_request(target_uri, GET)

    def get_snap_sg_generation(self, sg_id, snap_name):
        """Gets a snapshot and its generation count information for a Storage Group.
        The most recent snapshot will have a gen number of 0.
        The oldest snapshot will have a gen number = genCount - 1
        (i.e. if there are 4 generations of particular snapshot,
        the oldest will have a gen num of 3)
        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: snapshot information
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot/%s"
                      % (self.array_id, sg_id, snap_name))
        return self.rest_client.rest_request(target_uri, GET)

    def create_sg_snapshot(self, sg_id, snap_name):
        """Creates a new snapshot of a specified sg
        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot"
                      % (self.array_id, sg_id))
        snap_data = ({"snapshotName": snap_name})
        return self.rest_client.rest_request(
            target_uri, POST, request_object=snap_data)

    def create_new_gen_snap(self, sg_id, snap_name):
        """Establish a new generation of a SnapVX snapshot for a source SG
        :param sg_id: the name of the storage group
        :param snap_name: the name of the existing snapshot
        :return: message
        """
        target_uri = (
            "/replication/symmetrix/%s/storagegroup/%s/snapshot/%s/generation"
            % (self.array_id, sg_id, snap_name))
        data = ({})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=data)

    def restore_snapshot(self, sg_id, snap_name, gen_num):
        """Restore a storage group to its snapshot
        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/"
                      "%s/snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({"action": "Restore"})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def rename_gen_snapshot(self, sg_id, snap_name, gen_num, new_name):
        """Rename an existing storage group snapshot
        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot
        :param new_name: the new name of the snapshot
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/"
                      "snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({"rename": {"newSnapshotName": new_name},
                      "action": "Rename"})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def link_gen_snapshot(self, sg_id, snap_name, gen_num, link_sg_name):
        """Link a snapshot to another storage group
        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param gen_num: generation number of a snapshot
        :param link_sg_name:  the target storage group name
        :return: message
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/"
                      "snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({{"action": "Link",
                       "link": {"linkStorageGroupName": link_sg_name},
                       }})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def delete_sg_snapshot(self, sg_id, snap_name, gen_num):
        """Deletes a specified snapshot.
        Can only delete snap if generation number is known
        :param sg_id: name of the storage group
        :param snap_name: name of the snapshot
        :param gen_num: the generation number of the snapshot
        :return: status code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/"
                      "%s/snapshot/%s/generation/%s"
                      % (self.array_id, sg_id, snap_name, gen_num))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_replication_capabilities(self, array):
        """Check what replication features are licensed and enabled.
        :param array:
        :return:
        """
        target_uri = "/replication/capabilities/symmetrix"
        return self.rest_client.rest_request(target_uri, GET)

    def is_snapvX_licensed(self, array):
        """Check if the snapVx feature is licensed and enabled.
        :param array: the Symm array serial number
        :return: True if licensed and enabled; False otherwise
        """
        snapCapability = False
        response = self.get_replication_capabilities(array)
        try:
            symmList = response['symmetrixCapability']
            for symm in symmList:
                if symm['symmetrixId'] == array:
                    snapCapability = symm['snapVxCapable']
                    break
        except KeyError:
            LOG.error("Cannot access replication capabilities")
        return snapCapability

    #admissibility checks

    def get_wlp_timestamp(self):
        """Get the latest timestamp from WLP for processing New Worlkloads
        :return: JSON Payload
        """
        target_uri = ("/82/wlp/symmetrix/%s"
                      % (self.array_id))
        return self.rest_client.rest_request(target_uri, GET)

    def get_headroom(self,workload):
        """Get the Remaining Headroom Capacity
        :param workload:
        :return: JSON Payload, sample {'headroom': [{'workloadType': 'OLTP', 'headroomCapacity': 29076.34, 'processingDetails':
        {'lastProcessedSpaTimestamp': 1485302100000, 'nextUpdate': 1670}, 'sloName': 'Diamond', 'srp': 'SRP_1', 'emulation': 'FBA'}]}
        """
        target_uri = ("/82/wlp/symmetrix/%s/headroom?emulation=FBA&slo=Diamond&workloadtype=%s&srp=SRP_1"
                     % (self.array_id, workload))

        return self.rest_client.rest_request(target_uri, GET)
