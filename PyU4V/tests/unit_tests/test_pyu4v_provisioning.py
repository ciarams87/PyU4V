# Copyright (c) 2020 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""test_pyu4v_provisioning.py."""
import csv
import os
import tempfile
import testtools

from unittest import mock

from PyU4V import provisioning
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import constants
from PyU4V.utils import exception
from PyU4V.utils import file_handler


class PyU4VProvisioningTest(testtools.TestCase):
    """Test provisioning."""

    def setUp(self):
        """setUp."""
        super(PyU4VProvisioningTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.common = self.conn.common
            self.provisioning = self.conn.provisioning

    def tearDown(self):
        """tearDown."""
        super(PyU4VProvisioningTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_array(self):
        """Test get_array."""
        array_id = self.data.array
        array_details = self.provisioning.get_array(array_id=array_id)
        self.assertEqual(self.data.array_slo_details, array_details)

    def test_get_director(self):
        """Test get_director."""
        dir_details = self.provisioning.get_director(self.data.director_id1)
        self.assertEqual(self.data.director_info, dir_details)

    def test_get_director_list(self):
        """Test get_director_list."""
        dir_list = self.provisioning.get_director_list()
        self.assertEqual(self.data.director_list['directorId'], dir_list)

    def test_get_director_port(self):
        """Test get_director_port."""
        port_details = self.provisioning.get_director_port(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.port_list[0], port_details)

    def test_get_director_port_list(self):
        """Test get_director_port_list."""
        port_key_list = self.provisioning.get_director_port_list(
            self.data.director_id1)
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_port_identifier(self):
        """Test get_port_identifier."""
        wwn = self.provisioning.get_port_identifier(
            self.data.director_id1, self.data.port_id1)
        self.assertEqual(self.data.wwnn1, wwn)

    def test_get_port_identifier_key_exception(self):
        """Test get_port_identifier with key exception."""
        with mock.patch.object(self.provisioning,
                               'get_director_port',
                               return_value={'test': 'data'}):
            wwn = self.provisioning.get_port_identifier(
                self.data.director_id1, self.data.port_id1)
            self.assertEqual(None, wwn)

    def test_get_host(self):
        """Test get_host."""
        host_details = self.provisioning.get_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual(self.data.initiatorgroup[0], host_details)

    def test_get_host_list(self):
        """Test get_host_list."""
        host_list = self.provisioning.get_host_list()
        self.assertEqual(self.data.host_list['hostId'], host_list)

    def test_create_host_name_only(self):
        """Test create_host name only."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_host(
                self.data.initiatorgroup_name_i)
            new_ig_data2 = {'hostId': self.data.initiatorgroup_name_i}
            mock_create.assert_called_once_with(
                category='sloprovisioning', resource_level='symmetrix',
                resource_level_id=self.data.array, resource_type='host',
                payload=new_ig_data2)

    def test_create_host_host_flags_initiator_list_async(self):
        """Test create_host."""
        host_flags = {'consistent_lun': 'true'}
        data = [self.data.wwnn1, self.data.wwpn2]
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_host(
                self.data.initiatorgroup_name_i, host_flags=host_flags,
                initiator_list=data, _async=True)
            new_ig_data = {'hostId': self.data.initiatorgroup_name_i,
                           'initiatorId': data,
                           'hostFlags': host_flags,
                           'executionOption': 'ASYNCHRONOUS'}
            mock_create.assert_called_once_with(
                category='sloprovisioning', resource_level='symmetrix',
                resource_level_id=self.data.array, resource_type='host',
                payload=new_ig_data)

    def test_create_host_initiator_file(self):
        """Test create_host."""
        host_flags = {'consistent_lun': 'true'}
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            with tempfile.TemporaryDirectory() as td:
                file_name = os.path.join(td, 'temp_ut_file')
                with open(file_name, 'w') as f:
                    f.write(self.data.wwnn1)
                self.provisioning.create_host(
                    self.data.initiatorgroup_name_i, host_flags=host_flags,
                    init_file=file_name, _async=True)
            new_ig_data3 = {'hostId': self.data.initiatorgroup_name_i,
                            'initiatorId': [self.data.wwnn1],
                            'hostFlags': host_flags,
                            'executionOption': 'ASYNCHRONOUS'}
            mock_create.assert_called_once_with(
                category='sloprovisioning', resource_level='symmetrix',
                resource_level_id=self.data.array, resource_type='host',
                payload=new_ig_data3)

    def test_modify_host_change_host_flag(self):
        """Test modify_host change host flag."""
        host_name = self.data.initiatorgroup_name_i
        host_flag_dict = {'consistent_lun': 'true'}
        payload = ({'editHostActionParam': {
            'setHostFlagsParam': {'hostFlags': host_flag_dict}}})
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_host(host_name,
                                          host_flag_dict=host_flag_dict)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOST,
                resource_type_id=host_name,
                payload=payload)

    def test_modify_host_remove_initiator(self):
        """Test modify_host remove initiator."""
        host_name = self.data.initiatorgroup_name_i
        remove_init_list = [self.data.wwnn1]
        payload = ({'editHostActionParam': {
            'removeInitiatorParam': {'initiator': remove_init_list}}})
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_host(host_name,
                                          remove_init_list=remove_init_list)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOST,
                resource_type_id=host_name,
                payload=payload)

    def test_modify_host_add_initiator(self):
        """Test modify_host add initiator."""
        host_name = self.data.initiatorgroup_name_i
        add_init_list = [self.data.wwnn1]
        payload = ({'editHostActionParam': {
            'addInitiatorParam': {'initiator': add_init_list}}})
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_host(host_name,
                                          add_init_list=add_init_list)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOST,
                resource_type_id=host_name,
                payload=payload)

    def test_modify_host_change_name(self):
        """Test modify_host change name."""
        host_name = self.data.initiatorgroup_name_i
        new_name = 'my-new-name'
        payload = ({'editHostActionParam': {
            'renameHostParam': {'new_host_name': new_name}}})
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_host(host_name, new_name=new_name)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOST,
                resource_type_id=host_name,
                payload=payload)

    def test_modify_host_exception(self):
        host_name = self.data.initiatorgroup_name_i
        with mock.patch.object(
                self.provisioning, 'modify_resource'):
            self.assertRaises(exception.InvalidInputException,
                              self.provisioning.modify_host, host_name)

    def test_delete_host(self):
        """Test delete_host."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            host_id = self.data.initiatorgroup_name_i
            self.provisioning.delete_host(host_id)
            mock_delete.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOST,
                resource_type_id=host_id)

    def test_get_mvs_from_host(self):
        """Test get_mvs_from_host."""
        mv_list = self.provisioning.get_mvs_from_host(
            self.data.initiatorgroup_name_i)
        self.assertEqual([self.data.masking_view_name_i], mv_list)

    def test_get_initiator_ids_from_host(self):
        """Test get_initiator_ids_from_host."""
        init_list = self.provisioning.get_initiator_ids_from_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual([self.data.wwpn1], init_list)

    def test_get_host_group(self):
        """Test get_host_group."""
        hg_details = self.provisioning.get_hostgroup(self.data.hostgroup_id)
        self.assertEqual(self.data.hostgroup, hg_details)

    def test_get_hostgroup_list(self):
        """Test get_hostgroup_list."""
        hg_list = self.provisioning.get_hostgroup_list()
        self.assertEqual(self.data.hostgroup_list['hostGroupId'], hg_list)
        with mock.patch.object(
                self.provisioning, 'get_resource',
                return_value={'some_key': 'some_value'}):
            hg_list = self.provisioning.get_hostgroup_list()
            self.assertEqual(list(), hg_list)

    def test_create_host_group(self):
        """Test create_host_group."""
        host_group_id = self.data.hostgroup_id
        host_list = [self.data.initiatorgroup_name_f]
        payload = {'hostId': host_list, 'hostGroupId': host_group_id}
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_hostgroup(
                self.data.hostgroup_id, [self.data.initiatorgroup_name_f])
            mock_create.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOSTGROUP,
                payload=payload)

    def test_create_host_group_host_flags_async(self):
        """Test create_host_group with additional flags"""
        host_group_id = self.data.hostgroup_id
        host_list = [self.data.initiatorgroup_name_f]
        host_flags = {'flag': 1}
        payload = {'hostId': host_list, 'hostGroupId': host_group_id,
                   'hostFlags': host_flags, 'executionOption': 'ASYNCHRONOUS'}
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_hostgroup(
                host_group_id, host_list, host_flags, _async=True)
            mock_create.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOSTGROUP,
                payload=payload)

    def test_modify_host_group_change_host_flags(self):
        """Test modify_host_group change flags."""
        host_group_id = self.data.hostgroup_id
        host_flag_dict = {'consistent_lun': 'true'}
        payload = {'editHostGroupActionParam': {
            'setHostGroupFlagsParam': {'hostFlags': host_flag_dict}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_hostgroup(
                host_group_id, host_flag_dict=host_flag_dict)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOSTGROUP,
                resource_type_id=host_group_id,
                payload=payload)

    def test_modify_host_group_remove_host(self):
        """Test modify_host_group remove host."""
        host_group_id = self.data.hostgroup_id
        remove_host_list = ['host1']
        payload = {'editHostGroupActionParam': {
            'removeHostParam': {'host': remove_host_list}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_hostgroup(
                host_group_id, remove_host_list=remove_host_list)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOSTGROUP,
                resource_type_id=host_group_id,
                payload=payload)

    def test_modify_host_group_add_host(self):
        """Test modify_host_group add host."""
        host_group_id = self.data.hostgroup_id
        add_host_list = ['host2']
        payload = {'editHostGroupActionParam': {
            'addHostParam': {'host': add_host_list}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_hostgroup(
                host_group_id, add_host_list=add_host_list)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOSTGROUP,
                resource_type_id=host_group_id,
                payload=payload)

    def test_modify_host_group_change_name(self):
        """Test modify_host_group change name."""
        host_group_id = self.data.hostgroup_id
        new_name = 'my-new-name'
        payload = {'editHostGroupActionParam': {
            'renameHostGroupParam': {'new_host_group_name': new_name}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_hostgroup(
                host_group_id, new_name=new_name)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOSTGROUP,
                resource_type_id=host_group_id,
                payload=payload)

    def test_modify_host_group_exception(self):
        """Test modify_host_group exception."""
        hostgroup_name = self.data.hostgroup_id
        with mock.patch.object(
                self.provisioning, 'modify_resource'):
            self.assertRaises(exception.InvalidInputException,
                              self.provisioning.modify_hostgroup,
                              hostgroup_name)

    def test_delete_hostgroup(self):
        """Test delete_hostgroup."""
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            host_group_id = self.data.hostgroup_id
            self.provisioning.delete_hostgroup(host_group_id)
            mock_delete.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.HOSTGROUP,
                resource_type_id=host_group_id)

    def test_get_initiator(self):
        """Test get_initiator."""
        init_details = self.provisioning.get_initiator(self.data.wwpn1)
        self.assertEqual(self.data.initiator_list[0], init_details)

    def test_get_initiator_list(self):
        """Test get_initiator_list."""
        init_list = self.provisioning.get_initiator_list()
        self.assertEqual(
            self.data.initiator_list[2]['initiatorId'], init_list)

    def test_modify_initiator_remove_masking_entry(self):
        """Test modify_initiator remove masking entry."""
        initiator_name = self.data.wwpn1
        payload = {'editInitiatorActionParam': {
            'removeMaskingEntry': 'true'}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_initiator(
                initiator_name, remove_masking_entry='true')
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.INITIATOR,
                resource_type_id=initiator_name,
                payload=payload)

    def test_modify_initiator_replace_initiator(self):
        """Test modify_initiator replace initiator."""
        initiator_name = self.data.wwpn1
        new_initiator = self.data.wwpn2
        payload = {'editInitiatorActionParam': {
            'replaceInitiatorParam': {'new_initiator': new_initiator}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_initiator(
                initiator_name, replace_init=new_initiator)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.INITIATOR,
                resource_type_id=initiator_name,
                payload=payload)

    def test_modify_initiator_rename_alias(self):
        """Test modify_initiator rename alias."""
        initiator_name = self.data.wwpn1
        rename_alias = ('new node name', 'new port name')
        payload = {'editInitiatorActionParam': {
                   'renameAliasParam': {
                       'node_name': rename_alias[0],
                       'port_name': rename_alias[1]}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_initiator(
                initiator_name, rename_alias=rename_alias)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.INITIATOR,
                resource_type_id=initiator_name,
                payload=payload)

    def test_modify_initiator_set_fcid(self):
        """Test modify_initiator set fcid."""
        initiator_name = self.data.wwpn1
        new_fcid = 'my-new-name'
        payload = {'editInitiatorActionParam': {
            'initiatorSetAttributesParam': {'fcidValue': new_fcid}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_initiator(
                initiator_name, set_fcid=new_fcid)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.INITIATOR,
                resource_type_id=initiator_name,
                payload=payload)

    def test_modify_initiator_change_initiator_flags(self):
        """Test modify_initiator change initiator flags."""
        initiator_name = self.data.wwpn1
        initiator_flags = {'my-flag': 'value'}
        payload = {'editInitiatorActionParam': {
            'initiatorSetFlagsParam': {
                'initiatorFlags': initiator_flags}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_initiator(
                initiator_name, initiator_flags=initiator_flags)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.INITIATOR,
                resource_type_id=initiator_name,
                payload=payload)

    def test_modify_initiator_exception(self):
        """Test modify_initiator exception."""
        initiator_name = self.data.wwpn1
        with mock.patch.object(
                self.provisioning, 'modify_resource'):
            self.assertRaises(
                exception.InvalidInputException,
                self.provisioning.modify_initiator, initiator_name)

    def test_is_initiator_in_host(self):
        """Test is_initiator_in_host true value."""
        check = self.provisioning.is_initiator_in_host(self.data.wwpn1)
        self.assertTrue(check)

    def test_initiator_not_in_host(self):
        """Test is_initiator_in_host false value."""
        check = self.provisioning.is_initiator_in_host('fake-init')
        self.assertFalse(check)

    def test_get_initiator_group_from_initiator(self):
        """Test get_initiator_group_from_initiator."""
        found_ig_name = self.provisioning.get_initiator_group_from_initiator(
            self.data.wwpn1)
        self.assertEqual(self.data.initiatorgroup_name_f, found_ig_name)

    def test_get_masking_view_list(self):
        """Test get_masking_view_list."""
        mv_list = self.provisioning.get_masking_view_list()
        self.assertEqual(self.data.maskingview[2]['maskingViewId'], mv_list)

    def test_get_masking_view(self):
        """Test get_masking_view."""
        mv_details = self.provisioning.get_masking_view(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.maskingview[0], mv_details)

    def test_create_masking_view_existing_components_host_name(self):
        """Test create_masking_view_existing_components host name."""
        port_group_name = self.data.port_group_name_f
        storage_group_name = self.data.storagegroup_name_2
        masking_view = 'my_masking_view'
        host_name = self.data.initiatorgroup_name_f
        host_details = {'useExistingHostParam': {'hostId': host_name}}
        payload = {
            'portGroupSelection': {
                'useExistingPortGroupParam': {
                    'portGroupId': port_group_name}},
            'maskingViewId': masking_view,
            'hostOrHostGroupSelection': host_details,
            'storageGroupSelection': {
                'useExistingStorageGroupParam': {
                    'storageGroupId': storage_group_name}}}
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_masking_view_existing_components(
                port_group_name, masking_view, storage_group_name,
                host_name=host_name)
            mock_create.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.MASKINGVIEW,
                payload=payload)

    def test_create_masking_view_existing_components_host_group(self):
        """Test create_masking_view_existing_components host group."""
        port_group_name = self.data.port_group_name_f
        storage_group_name = self.data.storagegroup_name_2
        masking_view = 'my_masking_view'
        host_group_name = self.data.hostgroup_id
        host_details = {'useExistingHostGroupParam': {
            'hostGroupId': host_group_name}}
        payload = {
            'executionOption': 'ASYNCHRONOUS',
            'portGroupSelection': {
                'useExistingPortGroupParam': {
                    'portGroupId': port_group_name}},
            'maskingViewId': masking_view,
            'hostOrHostGroupSelection': host_details,
            'storageGroupSelection': {
                'useExistingStorageGroupParam': {
                    'storageGroupId': storage_group_name}}}
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_masking_view_existing_components(
                port_group_name, masking_view, storage_group_name,
                host_group_name=host_group_name, _async=True)
            mock_create.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.MASKINGVIEW,
                payload=payload)

    def test_create_masking_view_existing_components_exception(self):
        """Test create_masking_view_existing_components exception."""
        port_group_name = self.data.port_group_name_f
        storage_group_name = self.data.storagegroup_name_2
        self.assertRaises(
            exception.InvalidInputException,
            self.provisioning.create_masking_view_existing_components,
            port_group_name, 'my_masking_view', storage_group_name)

    def test_get_masking_views_from_storage_group(self):
        """Test get_masking_views_from_storage_group."""
        mv_list = self.provisioning.get_masking_views_from_storage_group(
            self.data.storagegroup_name_1)
        self.assertEqual(self.data.sg_details[1]['maskingview'], mv_list)

    def test_get_masking_views_by_host(self):
        """Test get_masking_views_by_host."""
        mv_list = self.provisioning.get_masking_views_by_host(
            self.data.initiatorgroup_name_f)
        self.assertEqual(self.data.initiator_list[0]['maskingview'], mv_list)

    def test_get_element_from_masking_view_get_port_group(self):
        """Test get_masking_view get port group."""
        masking_view_name = self.data.masking_view_name_f
        masking_view_details = self.data.maskingview[0]
        ref_port_group = masking_view_details['portGroupId']
        act_port_group = self.provisioning.get_element_from_masking_view(
            masking_view_name, portgroup=True)
        self.assertEqual(ref_port_group, act_port_group)

    def test_get_element_from_masking_view_get_storage_group(self):
        """Test get_masking_view get storage group."""
        masking_view_name = self.data.masking_view_name_f
        masking_view_details = self.data.maskingview[0]
        ref_storage_group = masking_view_details['storageGroupId']
        act_storage_group = (
            self.provisioning.get_element_from_masking_view(
                masking_view_name, storagegroup=True))
        self.assertEqual(ref_storage_group, act_storage_group)

    def test_get_element_from_masking_view_get_host(self):
        """Test get_masking_view get host."""
        masking_view_name = self.data.masking_view_name_f
        masking_view_details = self.data.maskingview[0]
        ref_host_id = masking_view_details['hostId']
        act_host_id = self.provisioning.get_element_from_masking_view(
            masking_view_name, host=True)
        self.assertEqual(ref_host_id, act_host_id)

    def test_get_element_from_masking_view_get_host_group_id(self):
        """Test get_masking_view get host group id."""
        masking_view_name = self.data.masking_view_name_f
        ref_hostgroup_id = self.data.hostgroup_id
        with mock.patch.object(
                self.provisioning, 'get_masking_view', return_value={
                                   'hostGroupId': self.data.hostgroup_id}):
            act_hostgroup_id = (
                self.provisioning.get_element_from_masking_view(
                    masking_view_name, host=True))
            self.assertEqual(ref_hostgroup_id, act_hostgroup_id)

    def test_get_element_from_masking_view_exception(self):
        """Test get_masking_view exception."""
        with mock.patch.object(self.provisioning, 'get_masking_view',
                               return_value=None):
            self.assertRaises(exception.ResourceNotFoundException,
                              self.provisioning.get_element_from_masking_view,
                              self.data.masking_view_name_f)

    def test_get_common_masking_views(self):
        """Test get_common_masking_views."""
        port_group_name = self.data.port_group_name_f
        initiator_group_name = self.data.initiatorgroup_name_f
        ref_dict = {'port_group_name': port_group_name,
                    'host_or_host_group_name': initiator_group_name}
        with mock.patch.object(
                self.provisioning, 'get_masking_view_list') as mock_list:
            self.provisioning.get_common_masking_views(
                port_group_name, initiator_group_name)
            mock_list.assert_called_once_with(ref_dict)

    def test_delete_masking_view(self):
        """Test delete_masking_view."""
        masking_view_name = self.data.masking_view_name_f
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_masking_view(masking_view_name)
            mock_delete.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.MASKINGVIEW,
                resource_type_id=masking_view_name)

    def test_rename_masking_view(self):
        """Test rename_masking_view."""
        masking_view_name = self.data.masking_view_name_f
        new_name = 'new-name'
        payload = {'editMaskingViewActionParam': {
            'renameMaskingViewParam': {
                'new_masking_view_name': new_name}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.rename_masking_view(masking_view_name, new_name)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.MASKINGVIEW,
                resource_type_id=masking_view_name,
                payload=payload)

    def test_get_host_from_maskingview(self):
        """Test get_host_from_maskingview."""
        ig_id = self.provisioning.get_host_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.initiatorgroup_name_f, ig_id)

    def test_get_storage_group_from_maskingview(self):
        """Test get_storage_group_from_maskingview."""
        storage_group_id = self.provisioning.get_storagegroup_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.storagegroup_name, storage_group_id)

    def test_get_port_group_from_maskingview(self):
        """Test get_port_group_from_maskingview."""
        port_group_id = self.provisioning.get_portgroup_from_maskingview(
            self.data.masking_view_name_f)
        self.assertEqual(self.data.port_group_name_f, port_group_id)

    def test_get_maskingview_connections(self):
        """Test get_maskingview_connections."""
        mv_conn_list = self.provisioning.get_maskingview_connections(
            self.data.masking_view_name_f)
        self.assertEqual(
            self.data.maskingview[0]['maskingViewConnection'], mv_conn_list)

    def test_find_host_lun_id_for_vol_success(self):
        """Test find_host_lun_id_for_vol successful return."""
        host_lun_id = self.provisioning.find_host_lun_id_for_vol(
            self.data.masking_view_name_f, self.data.device_id)
        self.assertEqual(3, host_lun_id)

    def test_find_host_lun_id_for_vol_failure(self):
        """Test find_host_lun_id_for_vol unsuccessful return."""
        with mock.patch.object(
                self.provisioning, 'get_maskingview_connections',
                side_effect=[list(), [{'not_host_lun': 'value'}]]):
            for x in range(0, 2):
                host_lun_id2 = self.provisioning.find_host_lun_id_for_vol(
                    self.data.masking_view_name_f, self.data.device_id)
                self.assertIsNone(host_lun_id2)

    def test_get_port_list(self):
        """Test get_port_list."""
        port_key_list = self.provisioning.get_port_list()
        self.assertEqual(
            self.data.port_key_list['symmetrixPortKey'], port_key_list)

    def test_get_port_group(self):
        """Test get_port_group."""
        port_group_details = self.provisioning.get_portgroup(
            self.data.port_group_name_f)
        self.assertEqual(self.data.portgroup[0], port_group_details)

    def test_get_port_group_list(self):
        """Test get_port_group_list."""
        port_group_list = self.provisioning.get_portgroup_list()
        self.assertEqual(self.data.pg_list['portGroupId'], port_group_list)

    def test_get_ports_from_port_group(self):
        """Test get_ports_from_port_group."""
        port_list = self.provisioning.get_ports_from_pg(
            self.data.port_group_name_f)
        self.assertEqual(['FA-1D:4'], port_list)

    def test_get_target_wwns_from_port_group(self):
        """Test get_target_wwns_from_port_group."""
        with mock.patch.object(
                self.provisioning, 'get_port_group', return_value={
                    'symmetrixPortKey': [{
                        'directorId': self.data.director_id1,
                        'portId': self.data.port_id1}]}) as mck_get_grp:
            target_wwns = self.provisioning.get_target_wwns_from_pg(
                self.data.port_group_name_f)
            self.assertEqual([self.data.wwnn1], target_wwns)
            mck_get_grp.assert_called_once_with(self.data.port_group_name_f)

    def test_get_iscsi_ip_address_and_iqn(self):
        """Test get_iscsi_ip_address_and_iqn."""
        ip_addresses, iqn = self.provisioning.get_iscsi_ip_address_and_iqn(
            'SE-4E:0')
        self.assertEqual([self.data.ip], ip_addresses)
        self.assertEqual(self.data.initiator, iqn)

    def test_get_iscsi_ip_address_and_iqn_exception(self):
        """Test exception in get_iscsi_ip_address_and_iqn."""
        with mock.patch.object(
                self.provisioning, 'get_director_port',
                return_value={'test': 'data'}):
            ip, iqn = (self.provisioning.
                       get_iscsi_ip_address_and_iqn('SE-4E:0'))
            self.assertEqual(ip, list())
            self.assertIsNone(iqn)

    def test_get_storage_group_demand_report(self):
        """Test get_storage_group_demand_report."""
        ref_storage_group_details = self.data.srp_details
        act_storage_group_details = (self.provisioning.
                                     get_storage_group_demand_report())
        self.assertEqual(act_storage_group_details, ref_storage_group_details)

    @mock.patch.object(
        provisioning.ProvisioningFunctions, '_update_port_group_port_ids')
    def test_create_port_group(self, mck_update):
        """Test create_port_group."""
        port_group_id = self.data.port_group_name_f
        director_id = self.data.director_id1
        port_id = self.data.port_id1
        payload = ({'portGroupId': port_group_id,
                    'symmetrixPortKey': [{'directorId': director_id,
                                          'portId': port_id}]})
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_portgroup(port_group_id, director_id,
                                               port_id)
        mock_create.assert_called_once_with(
            category=constants.SLOPROVISIONING,
            resource_level=constants.SYMMETRIX,
            resource_level_id=self.data.array,
            resource_type=constants.PORTGROUP,
            payload=payload)
        mck_update.assert_called_once()

    def test_get_child_storage_group_from_parent(self):
        """Test get_child_storage_group_from_parent."""
        parent_storage_group = self.data.parent_sg
        ref_child_storage_group_list = [self.data.storagegroup_name_1]
        act_child_storage_group_list = (
            self.provisioning.get_child_sg_from_parent(parent_storage_group))
        self.assertEqual(ref_child_storage_group_list,
                         act_child_storage_group_list)

    @mock.patch.object(
        provisioning.ProvisioningFunctions, '_update_port_group_port_ids')
    def test_create_multiport_port_group(self, mck_update):
        """Test create_multiport_port_group."""
        port_group_id = self.data.port_group_name_f
        port_dict_list = [{'directorId': self.data.director_id1,
                           'portId': self.data.port_id1},
                          {'directorId': self.data.director_id2,
                           'portId': self.data.port_id2}, ]

        payload = {'portGroupId': port_group_id,
                   'symmetrixPortKey': port_dict_list}
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_multiport_portgroup(
                port_group_id, port_dict_list)
        mock_create.assert_called_once_with(
            category=constants.SLOPROVISIONING,
            resource_level=constants.SYMMETRIX,
            resource_level_id=self.data.array,
            resource_type=constants.PORTGROUP,
            payload=payload)
        mck_update.assert_called_once()

    @mock.patch.object(file_handler, 'create_list_from_file',
                       return_value=['FA-1D:4', 'SE-4E:0'])
    def test_create_port_group_from_file(self, mock_create_from_file):
        """Test create_port_group_from_file."""
        port_group_id = self.data.port_group_name_f
        payload = [{'directorId': self.data.director_id1,
                    'portId': self.data.port_id1},
                   {'directorId': self.data.director_id2,
                    'portId': self.data.port_id2}]
        with mock.patch.object(
                self.provisioning,
                'create_multiport_portgroup') as mock_create:
            self.provisioning.create_portgroup_from_file(
                'my-file', port_group_id)
            mock_create.assert_called_once_with(
                port_group_id, payload)
        mock_create_from_file.assert_called()

    @mock.patch.object(
        provisioning.ProvisioningFunctions, '_update_port_group_port_ids')
    def test_modify_port_group_remove_port(self, mck_update):
        """Test modify_port_group remove_port."""
        port_group_name = self.data.port_group_name_f
        dirport = (self.data.director_id1, self.data.port_id1)
        ref_payload = {'editPortGroupActionParam': {
            'removePortParam': {
                'port': [{
                    'directorId': dirport[0],
                    'portId': dirport[1]}]}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_portgroup(
                port_group_name, remove_port=dirport)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.PORTGROUP,
                resource_type_id=port_group_name,
                payload=ref_payload)
        mck_update.assert_called_once()

    def test_modify_port_group_rename_port_group(self):
        """Test modify_port_group rename port group."""
        port_group_name = self.data.port_group_name_f
        new_port_group_name = 'new-name'
        ref_payload = {'editPortGroupActionParam': {
                       'renamePortGroupParam': {
                           'new_port_group_name': new_port_group_name}}}
        act_result = self.provisioning.modify_portgroup(
            port_group_name, rename_portgroup=new_port_group_name)
        ref_result = self.data.job_list[0]
        self.assertEqual(ref_result, act_result)
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_portgroup(
                port_group_name, rename_portgroup=new_port_group_name)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.PORTGROUP,
                resource_type_id=port_group_name,
                payload=ref_payload)

    @mock.patch.object(
        provisioning.ProvisioningFunctions, '_update_port_group_port_ids')
    def test_modify_port_group_add_port(self, mck_update):
        """Test modify_port_group add port."""
        port_group_name = self.data.port_group_name_f
        dirport = (self.data.director_id1, self.data.port_id1)
        ref_payload = {'editPortGroupActionParam': {
            'addPortParam': {
                'port': [{
                    'directorId': dirport[0],
                    'portId': dirport[1]}]}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_portgroup(
                port_group_name, add_port=dirport)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.PORTGROUP,
                resource_type_id=port_group_name,
                payload=ref_payload)
        mck_update.assert_called_once()

    def test_modify_port_group_exception(self):
        """Test modify_port_group raised exception."""
        port_group_name = self.data.port_group_name_f
        self.assertRaises(
            exception.InvalidInputException,
            self.provisioning.modify_portgroup, port_group_name)

    def test_delete_port_group(self):
        """Test delete_port_group."""
        port_group = self.data.port_group_name_f
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_del:
            self.provisioning.delete_portgroup(port_group)
            mock_del.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.PORTGROUP,
                resource_type_id=port_group
            )

    def test_get_slo_list(self):
        """Test get_slo_list."""
        slo_list = self.provisioning.get_slo_list()
        self.assertEqual(self.data.slo_list['sloId'], slo_list)

    def test_get_slo(self):
        """Test get_slo."""
        slo_details = self.provisioning.get_slo(self.data.slo)
        self.assertEqual(self.data.slo_details, slo_details)

    def test_modify_slo(self):
        """Test modify_slo."""
        current_name = self.data.slo
        new_name = 'new_name'
        ref_payload = {'editSloActionParam': {
            'renameSloParam': {
                'sloId': new_name}}}
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_slo(current_name, new_name)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.SLO,
                resource_type_id=current_name,
                payload=ref_payload)
        ref_result = self.data.job_list[0]
        act_result = self.provisioning.modify_slo(current_name, new_name)
        self.assertEqual(ref_result, act_result)

    def test_get_srp(self):
        """Test get_srp."""
        srp_details = self.provisioning.get_srp(self.data.srp)
        self.assertEqual(self.data.srp_details, srp_details)

    def test_get_srp_list(self):
        """Test get_srp_list."""
        srp_list = self.provisioning.get_srp_list()
        self.assertEqual(self.data.srp_list['srpId'], srp_list)

    def test_get_compressibility_report(self):
        """Test get_compressibility_report."""
        report = self.provisioning.get_compressibility_report(self.data.srp)
        self.assertEqual(
            self.data.compr_report['storageGroupCompressibility'], report)

    def test_is_compression_capable(self):
        """Test is_compression_capable."""
        compr_capable = self.provisioning.is_compression_capable()
        self.assertTrue(compr_capable)

    def test_get_storage_group(self):
        """Test get_storage_group."""
        storage_group_details = self.provisioning.get_storage_group(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_details[0], storage_group_details)

    def test_get_storage_group_list(self):
        """Test get_storage_group_list."""
        storage_group_list = self.provisioning.get_storage_group_list(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_list['storageGroupId'],
                         storage_group_list)

    def test_get_mv_from_sg(self):
        """Test get_mv_from_sg."""
        mv_list = self.provisioning.get_mv_from_sg(
            self.data.storagegroup_name_1)
        self.assertEqual(self.data.sg_details[1]['maskingview'], mv_list)

    def test_get_num_vols_in_storage_group(self):
        """Test get_num_vols_in_storage_group."""
        num_vols = self.provisioning.get_num_vols_in_sg(
            self.data.storagegroup_name)
        self.assertEqual(2, num_vols)

    def test_is_child_storage_group_in_parent_sg(self):
        """Test is_child_storage_group_in_parent_sg."""
        is_child = self.provisioning.is_child_sg_in_parent_sg(
            self.data.storagegroup_name_1, self.data.parent_sg)
        self.assertTrue(is_child)
        is_child2 = self.provisioning.is_child_sg_in_parent_sg(
            self.data.storagegroup_name_2, self.data.parent_sg)
        self.assertFalse(is_child2)

    def test_create_storage_group_no_slo(self):
        """Test create_storage_group no slo set."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_storage_group(
                srp_id=self.data.srp, sg_id='new-sg', slo=None, workload=None)

            payload = {
                'srpId': 'SRP_1', 'storageGroupId': 'new-sg',
                'emulation': 'FBA', 'sloBasedStorageGroupParam': [
                    {'sloId': 'None', 'workloadSelection': 'None',
                     'volumeAttributes': [
                         {'volume_size': '0', 'capacityUnit': 'GB',
                          'num_of_vols': 0}]}]}

            mock_create.assert_called_once_with(
                category='sloprovisioning',
                resource_level='symmetrix', resource_level_id=self.data.array,
                resource_type='storagegroup', payload=payload)

    def test_create_storage_group_mobility_id(self):
        """Test create_storage_group no slo set."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_storage_group(
                srp_id=self.data.srp, sg_id='new-sg', slo=None,
                workload=None, enable_mobility_id=True)

            payload = {
                'srpId': 'SRP_1', 'storageGroupId': 'new-sg',
                'emulation': 'FBA', 'sloBasedStorageGroupParam': [
                    {'sloId': 'None', 'workloadSelection': 'None',
                     "enable_mobility_id": True,
                     'volumeAttributes': [
                         {'volume_size': '0', 'capacityUnit': 'GB',
                          'num_of_vols': 0}]}]}

            mock_create.assert_called_once_with(
                category='sloprovisioning',
                resource_level='symmetrix', resource_level_id=self.data.array,
                resource_type='storagegroup', payload=payload)

    def test_create_storage_group_slo_async(self):
        """Test create_storage_group no slo set."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', self.data.slo, 'None', _async=True)
            payload = {
                'srpId': self.data.srp,
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'sloId': self.data.slo,
                     'workloadSelection': 'None',
                     'volumeAttributes': [{'num_of_vols': 0,
                                           'volume_size': '0',
                                           'capacityUnit': 'GB'}]}],
                'executionOption': 'ASYNCHRONOUS'}
            mock_create.assert_called_once_with(
                category='sloprovisioning',
                resource_level='symmetrix', resource_level_id=self.data.array,
                resource_type='storagegroup', payload=payload)

    def test_create_storage_group_no_slo_no_compression_name_full_allocate(
            self):
        """Test create_storage_group no slo set."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', self.data.slo, 'None',
                do_disable_compression=True, vol_name=self.data.device_id,
                allocate_full=True)
            payload = {
                'srpId': self.data.srp,
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'sloId': self.data.slo,
                     'workloadSelection': 'None',
                     'noCompression': 'true',
                     'allocate_capacity_for_each_vol': 'true',
                     'persist_preallocated_capacity_through_reclaim_or_copy':
                         'true',
                     'volumeAttributes': [{
                         'num_of_vols': 0,
                         'volume_size': '0',
                         'capacityUnit': 'GB',
                         'volumeIdentifier': {
                             'identifier_name': self.data.device_id,
                             'volumeIdentifierChoice': 'identifier_name'}}]}]}
            mock_create.assert_called_once_with(
                category='sloprovisioning',
                resource_level='symmetrix', resource_level_id=self.data.array,
                resource_type='storagegroup', payload=payload)

    def test_get_volume_effective_wwn_details(self):
        """Test get_volume_effective_wwn_details."""
        device_id = self.data.device_id
        vol_list = [device_id]
        ref_vol_data = [[device_id, None, self.data.volume_wwn,
                        None, [self.data.storagegroup_name]]]
        act_vol_data = self.provisioning.get_volume_effective_wwn_details(
            vol_list)
        self.assertEqual(ref_vol_data, act_vol_data)

    def test_get_volume_effective_wwn_details_write_to_file(self):
        """Test get_volume_effective_wwn_details."""
        device_id = self.data.device_id
        vol_list = [device_id]
        col_list = ['volume_id', 'effective_wwn', 'wwn',
                    'has_effective_wwn', 'storage_group_id']
        storage_group_format = "['{sg}']".format(
            sg=self.data.storagegroup_name)
        row_list = [device_id, '', self.data.volume_wwn,
                    '', storage_group_format]
        ref_out_data = [col_list, row_list]
        with tempfile.TemporaryDirectory() as td:
            file_name = os.path.join(td, 'temp_ut_file')
            act_vol_data = (self.provisioning.
                            get_volume_effective_wwn_details(
                                vol_list, output_file_name=file_name))
            self.assertEqual(None, act_vol_data)
            with open(file_name, 'r') as f:
                file_contents = list(csv.reader(f))
                self.assertEqual(ref_out_data, file_contents)

    def test_find_low_volume_utilization(self):
        """Test find_low_volume_utilization."""
        col_list = ['sg_name', 'volume_id', 'identifier', 'capacity',
                    'allocated_percent']
        ref_device = self.data.volume_details[0]
        row_list = [self.data.storagegroup_name, ref_device['volumeId'],
                    ref_device['volume_identifier'],
                    str(ref_device['cap_gb']),
                    str(ref_device['allocated_percent'])]
        ref_device_no_id = self.data.volume_details[1]
        row_list_no_id = [self.data.storagegroup_name,
                          ref_device_no_id['volumeId'],
                          'None', str(ref_device_no_id['cap_gb']),
                          str(ref_device_no_id['allocated_percent'])]
        ref_out_data = [col_list, row_list, row_list_no_id]
        with mock.patch.object(self.provisioning, 'get_storage_group_list',
                               return_value=[self.data.storagegroup_name]):
            with tempfile.TemporaryDirectory() as td:
                file_name = os.path.join(td, 'temp_ut_file')
                self.provisioning.find_low_volume_utilization(10, file_name)
                with open(file_name, 'r') as f:
                    file_contents = list(csv.reader(f))
                    self.assertEqual(ref_out_data, file_contents)

    def test_get_vol_effective_wwn_details_84(self):
        """Test get_vol_effective_wwn_details_84."""
        col_list = ['volumeId', 'effective_wwn', 'wwn', 'has_effective_wwn',
                    'storageGroupId']
        ref_volume = self.data.volume_details[0]
        storage_group_format = "{sg}".format(sg=ref_volume['storageGroupId'])
        row_list = [ref_volume['volumeId'], '', ref_volume['wwn'], '',
                    storage_group_format]
        ref_out_data = [col_list, row_list]

        with tempfile.TemporaryDirectory() as td:
            vol_list = [self.data.device_id]
            file_name = os.path.join(td, 'temp_ut_file')
            self.provisioning.get_vol_effective_wwn_details_84(vol_list,
                                                               file_name)
            with open(file_name, 'r') as f:
                file_contents = list(csv.reader(f))
                self.assertEqual(ref_out_data, file_contents)

    def test_create_volume_from_storage_group_return_id_success(self):
        """Test create_volume_from_storage_group_return_id."""
        ref_dev_id = "'6AB'"
        task = {
            'description': 'Creating new Volumes {ref_dev_id}'.format(
                ref_dev_id=ref_dev_id)}
        returned_job = {
            'status': 'succeeded',
            'result': 200,
            'task': [task]}
        with mock.patch.object(self.provisioning,
                               'add_new_volume_to_storage_group',
                               return_value=returned_job):
            with mock.patch.object(self.provisioning, 'get_volume_list',
                                   return_value=['00001']):
                act_dev_id = (self.provisioning.
                              create_volume_from_storage_group_return_id(
                                  'vol_name', self.data.storagegroup_name, 1))
                self.assertEqual(ref_dev_id[1:-1], act_dev_id)

    def test_create_volume_from_storage_group_return_id_task_exception(self):
        """Test create_volume_from_storage_group_return_id."""
        ref_dev_id = self.data.device_id
        task = {'fail_key': 'fail_val'}
        returned_job = {
            'status': 'succeeded',
            'result': 200,
            'task': [task]}
        with mock.patch.object(self.provisioning,
                               'add_new_volume_to_storage_group',
                               return_value=returned_job):
            with mock.patch.object(self.provisioning, 'get_volume_list',
                                   return_value=['00001']):
                act_dev_id = (self.provisioning.
                              create_volume_from_storage_group_return_id(
                                  'vol_name', self.data.storagegroup_name, 1))
                self.assertEqual(ref_dev_id, act_dev_id)

    def test_create_storage_group_full_allocated_no_slo(self):
        """Test create_storage_group no slo set."""
        ppctroc = 'persist_preallocated_capacity_through_reclaim_or_copy'
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', None, None, allocate_full=True)

            payload = {
                'srpId': self.data.srp,
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'sloId': 'None',
                     'workloadSelection': 'None',
                     'noCompression': 'true',
                     'allocate_capacity_for_each_vol': 'true',
                     ppctroc: 'true',
                     'volumeAttributes': [{'volume_size': '0',
                                           'capacityUnit': 'GB',
                                           'num_of_vols': 0}]}]}

            mock_create.assert_called_once_with(
                category='sloprovisioning', resource_level='symmetrix',
                resource_level_id=self.data.array,
                resource_type='storagegroup', payload=payload)

    def test_create_storage_group_full_allocated_slo_async(self):
        """Test create_storage_group slo set, async."""
        ppctroc = 'persist_preallocated_capacity_through_reclaim_or_copy'
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            mock_create.reset_mock()
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', self.data.slo, 'None',
                allocate_full=True, _async=True)
            payload = {
                'srpId': self.data.srp,
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'sloId': self.data.slo,
                     'workloadSelection': 'None',
                     'noCompression': 'true',
                     'allocate_capacity_for_each_vol': 'true',
                     ppctroc: 'true',
                     'volumeAttributes': [{'volume_size': '0',
                                           'capacityUnit': 'GB',
                                           'num_of_vols': 0, }]}],
                'executionOption': 'ASYNCHRONOUS'}
            mock_create.assert_called_once_with(
                category='sloprovisioning', resource_level='symmetrix',
                resource_level_id=self.data.array,
                resource_type='storagegroup', payload=payload)

    def test_create_storage_group_vol_name(self):
        """Test create_storage_group."""
        with mock.patch.object(
                self.provisioning, 'create_resource') as mock_create:
            # 1 - no slo, not async
            self.provisioning.create_storage_group(
                self.data.srp, 'new-sg', slo='Diamond', workload=None,
                num_vols=1, vol_size='1', vol_name='ID4TEST')
            volume_identifier = {
                'identifier_name': 'ID4TEST',
                'volumeIdentifierChoice': 'identifier_name'}
            payload1 = {
                'srpId': 'SRP_1',
                'storageGroupId': 'new-sg',
                'emulation': 'FBA',
                'sloBasedStorageGroupParam': [
                    {'sloId': 'Diamond',
                     'workloadSelection': 'None',
                     'volumeAttributes': [{
                         'volume_size': '1',
                         'capacityUnit': 'GB',
                         'num_of_vols': 1,
                         'volumeIdentifier': volume_identifier}]}]}

            mock_create.assert_called_once_with(
                category='sloprovisioning', resource_level='symmetrix',
                resource_level_id=self.data.array,
                resource_type='storagegroup', payload=payload1)

    def test_create_non_empty_storage_group(self):
        """Test create_non_empty_storage_group."""
        srp_id = self.data.srp
        storage_group_id = self.data.storagegroup_name_2
        slo = self.data.slo
        workload = self.data.workload
        num_vols = 1
        vol_size = '2'
        cap_unit = 'GB'
        with mock.patch.object(
                self.provisioning, 'create_storage_group') as mock_create:
            self.provisioning.create_non_empty_storagegroup(
                srp_id, storage_group_id, slo, workload, num_vols, vol_size,
                cap_unit)
            mock_create.assert_called_once_with(
                srp_id, storage_group_id, slo, workload,
                do_disable_compression=False,
                num_vols=num_vols, vol_size=vol_size, cap_unit=cap_unit,
                _async=False, enable_mobility_id=False, vol_name=None,
                snapshot_policy_ids=None)
        act_result = self.provisioning.create_non_empty_storagegroup(
            srp_id, storage_group_id, slo, workload, num_vols, vol_size,
            cap_unit)
        ref_result = self.data.job_list[0]
        self.assertEqual(ref_result, act_result)

    def test_create_non_empty_storage_group_mobility_id(self):
        """Test create_non_empty_storage_group."""
        srp_id = self.data.srp
        storage_group_id = self.data.storagegroup_name_2
        slo = self.data.slo
        workload = self.data.workload
        num_vols = 1
        vol_size = '2'
        cap_unit = 'GB'
        with mock.patch.object(
                self.provisioning, 'create_storage_group') as mock_create:
            self.provisioning.create_non_empty_storage_group(
                srp_id, storage_group_id, slo, workload, num_vols, vol_size,
                cap_unit, enable_mobility_id=True)
            mock_create.assert_called_once_with(
                srp_id, storage_group_id, slo, workload,
                do_disable_compression=False,
                num_vols=num_vols, vol_size=vol_size, cap_unit=cap_unit,
                _async=False, enable_mobility_id=True, vol_name=None,
                snapshot_policy_ids=None)
        act_result = self.provisioning.create_non_empty_storage_group(
            srp_id, storage_group_id, slo, workload, num_vols, vol_size,
            cap_unit)
        ref_result = self.data.job_list[0]
        self.assertEqual(ref_result, act_result)

    def test_create_empty_storage_group(self):
        """Test create_empty_storage_group."""
        srp_id = self.data.srp
        storage_group_id = self.data.storagegroup_name_2
        slo = self.data.slo
        workload = self.data.workload
        with mock.patch.object(
                self.provisioning, 'create_storage_group') as mock_create:
            self.provisioning.create_empty_sg(
                srp_id, storage_group_id, slo, workload)
            mock_create.assert_called_once_with(
                srp_id, storage_group_id, slo, workload,
                do_disable_compression=False, _async=False,
                snapshot_policy_ids=None)
        act_result = self.provisioning.create_empty_sg(
            srp_id, storage_group_id, slo, workload)
        ref_result = self.data.job_list[0]
        self.assertEqual(ref_result, act_result)

    def test_modify_storage_group(self):
        """Test modify_storage_group."""
        storage_group_id = self.data.storagegroup_name
        ref_payload = dict()
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning.modify_storage_group(
                storage_group_id, ref_payload)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.STORAGEGROUP,
                resource_type_id=storage_group_id,
                payload=ref_payload
            )
        ref_result = self.data.job_list[0]
        act_result = self.provisioning.modify_storage_group(
            storage_group_id, ref_payload)
        self.assertEqual(ref_result, act_result)

    def test_add_existing_vol_to_storage_group_vol_string(self):
        """Test add_existing_vol_to_storage_group."""
        payload = {'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addSpecificVolumeParam': {
                    'volumeId': [self.data.device_id]}}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.add_existing_vol_to_sg(
                self.data.storagegroup_name, self.data.device_id)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_add_existing_vol_to_storage_group_vol_list_async(self):
        """Test add_existing_vol_to_storage_group."""
        payload = {'executionOption': 'ASYNCHRONOUS',
                   'editStorageGroupActionParam': {
                       'expandStorageGroupParam': {
                           'addSpecificVolumeParam': {
                               'volumeId': [self.data.device_id]}}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.add_existing_vol_to_sg(
                self.data.storagegroup_name, [self.data.device_id], True)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_add_new_vol_to_storage_group_no_name(self):
        """Test add_new_vol_to_storage_group no vol name, not async."""
        num_of_volumes = 1
        volume_size = 10
        volume_capacity_type = 'GB'
        add_vol_info = {
            'emulation': 'FBA',
            'create_new_volumes': False,
            'volumeAttributes': [{
                'num_of_vols': num_of_volumes,
                'volume_size': volume_size,
                'capacityUnit': volume_capacity_type}]}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            # no vol name; not _async
            self.provisioning.add_new_vol_to_storagegroup(
                self.data.storagegroup_name, num_of_volumes, volume_size,
                volume_capacity_type)
            payload = {'editStorageGroupActionParam': {
                'expandStorageGroupParam': {
                    'addVolumeParam': add_vol_info}}}
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_add_new_vol_to_storage_group_mobility_id(self):
        """Test add_new_vol_to_storage_group no vol name, not async."""
        num_of_volumes = 1
        volume_size = 10
        volume_capacity_type = 'GB'
        add_vol_info = {
            'emulation': 'FBA',
            'create_new_volumes': False,
            "enable_mobility_id": True,
            'volumeAttributes': [{
                'num_of_vols': num_of_volumes,
                'volume_size': volume_size,
                'capacityUnit': volume_capacity_type}]}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            # no vol name; not _async
            self.provisioning.add_new_volume_to_storage_group(
                self.data.storagegroup_name, num_of_volumes, volume_size,
                volume_capacity_type, enable_mobility_id=True)
            payload = {'editStorageGroupActionParam': {
                'expandStorageGroupParam': {
                    'addVolumeParam': add_vol_info}}}
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_add_new_vol_to_storage_group_name_async(self):
        """Test add_new_vol_to_storage_group vol name, async."""
        num_of_volumes = 1
        volume_size = 10
        volume_capacity_type = 'GB'
        volume_name = 'my-vol'
        add_vol_info = {
            'emulation': 'FBA',
            'create_new_volumes': False,
            'volumeAttributes': [{
                'num_of_vols': num_of_volumes,
                'volume_size': volume_size,
                'capacityUnit': volume_capacity_type,
                'volumeIdentifier': {
                    'identifier_name': volume_name,
                    'volumeIdentifierChoice': 'identifier_name'}}]}
        payload = {'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addVolumeParam': add_vol_info}},
            'executionOption': 'ASYNCHRONOUS'}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.add_new_vol_to_storagegroup(
                self.data.storagegroup_name, num_of_volumes, volume_size,
                volume_capacity_type, True, volume_name)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_add_new_vol_to_storage_group_srdf_multihop_srdf(self):
        """Test adding new volume to replicated storage group."""
        remote_array = '000197800124'
        remote_array2 = '000197800125'
        num_of_volumes = 1
        volume_size = 10
        payload = {'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addVolumeParam': {
                    'emulation': 'FBA',
                    'create_new_volumes': False,
                    'volumeAttributes': [{
                        'num_of_vols': 1,
                        'volume_size': 10,
                        'capacityUnit': 'GB'}],
                    'remoteSymmSGInfoParam': {
                        'remote_symmetrix_1_id': remote_array,
                        'remote_symmetrix_1_sgs': ['PU-mystoragegroup-SG'],
                        'remote_symmetrix_2_id': remote_array2,
                        'remote_symmetrix_2_sgs': ['PU-mystoragegroup-SG']
                    }}}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.add_new_volume_to_storage_group(
                storage_group_id=self.data.storagegroup_name,
                num_vols=num_of_volumes, vol_size=volume_size, cap_unit='GB',
                remote_array_1_id=self.data.remote_array,
                remote_array_1_sgs=self.data.storagegroup_name,
                remote_array_2_id=self.data.remote_array2,
                remote_array_2_sgs=self.data.storagegroup_name)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_remove_vol_from_storage_group_volume_string(self):
        """Test remove_vol_from_storage_group single volume."""
        payload = {'editStorageGroupActionParam': {
            'removeVolumeParam': {
                'volumeId': [self.data.device_id]}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            # vol id, not list; not _async
            self.provisioning.remove_vol_from_storagegroup(
                self.data.storagegroup_name, self.data.device_id)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_remove_vol_from_replicated_storage_group_multihop(self):
        """Test remove_vol_from_storage_group single volume."""
        payload = {
            'editStorageGroupActionParam': {
                'removeVolumeParam': {
                    'volumeId': [self.data.device_id],
                    'remoteSymmSGInfoParam': {
                        'remote_symmetrix_1_id': self.data.remote_array,
                        'remote_symmetrix_1_sgs': [
                            self.data.storagegroup_name],
                        'remote_symmetrix_2_id': self.data.remote_array2,
                        'remote_symmetrix_2_sgs': [self.data.storagegroup_name]
                    }}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.remove_volume_from_storage_group(
                storage_group_id=self.data.storagegroup_name,
                vol_id=self.data.device_id,
                remote_array_1_id=self.data.remote_array,
                remote_array_1_sgs=self.data.storagegroup_name,
                remote_array_2_id=self.data.remote_array2,
                remote_array_2_sgs=self.data.storagegroup_name)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_remove_vol_from_storage_group_volume_list(self):
        """Test remove_vol_from_storage_group multiple volumes."""
        payload = {'executionOption': 'ASYNCHRONOUS',
                   'editStorageGroupActionParam': {
                       'removeVolumeParam': {
                           'volumeId': [self.data.device_id]}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            mock_mod.reset_mock()
            self.provisioning.remove_vol_from_storagegroup(
                self.data.storagegroup_name, [self.data.device_id], True)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_move_volumes_between_storage_groups_string(self):
        """Test move_volumes_between_storage_groups string parameter."""
        payload = {'editStorageGroupActionParam': {
            'moveVolumeToStorageGroupParam': {
                'volumeId': [self.data.device_id],
                'storageGroupId': self.data.storagegroup_name_1,
                'force': 'false'}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.move_volumes_between_storage_groups(
                self.data.device_id, self.data.storagegroup_name,
                self.data.storagegroup_name_1)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_move_volumes_between_storage_groups_list(self):
        """Test move_volumes_between_storage_groups list parameter."""
        payload = {'executionOption': 'ASYNCHRONOUS',
                   'editStorageGroupActionParam': {
                       'moveVolumeToStorageGroupParam': {
                           'volumeId': [self.data.device_id],
                           'storageGroupId': self.data.storagegroup_name_1,
                           'force': 'false'}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.move_volumes_between_storage_groups(
                [self.data.device_id], self.data.storagegroup_name,
                self.data.storagegroup_name_1, _async=True)
            mock_mod.assert_called_once_with(
                self.data.storagegroup_name, payload)

    def test_create_volume_from_storage_group_return_dev_id(self):
        """Test create_volume_from_storage_group_return_dev_id."""
        storage_group_name = self.data.storagegroup_name_1
        job = {'status': 'SUCCEEDED',
               'jobId': '12345',
               'result': 'created',
               'resourceLink': 'storagegroup/%s' % storage_group_name,
               'description': 'Creating new Volumes for MY-SG : [00001]'}
        with mock.patch.object(
                self.provisioning, 'add_new_volume_to_storage_group',
                return_value=job):
            with mock.patch.object(self.provisioning, 'get_volume_list',
                                   return_value=['00001']):
                device_id = (
                    self.provisioning.create_volume_from_sg_return_dev_id(
                        'volume_name', storage_group_name, '2'))
                self.assertEqual(self.data.device_id, device_id)

    def test_add_child_storage_group_to_parent_storage_group(self):
        """Test add_child_storage_group_to_parent_storage_group."""
        child_storage_group = self.data.storagegroup_name_1
        parent_storage_group = self.data.parent_sg
        ref_payload = {'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addExistingStorageGroupParam': {
                    'storageGroupId': [child_storage_group]}}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.add_child_sg_to_parent_sg(
                child_storage_group, parent_storage_group)
            mock_mod.assert_called_once_with(
                parent_storage_group, ref_payload)
        ref_result = self.data.job_list[0]
        act_result = self.provisioning.add_child_sg_to_parent_sg(
            child_storage_group, parent_storage_group)
        self.assertEqual(ref_result, act_result)

    def test_remove_child_storage_group_from_parent_storage_group(self):
        """Test remove_child_storage_group_from_parent_storage_group."""
        parent_storage_group = self.data.parent_sg
        child_storage_group = self.data.storagegroup_name_1
        ref_payload = {
            'editStorageGroupActionParam': {
                'removeStorageGroupParam': {
                    'storageGroupId': [child_storage_group],
                    'force': 'true'}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            self.provisioning.remove_child_sg_from_parent_sg(
                child_storage_group, parent_storage_group)
            mock_mod.assert_called_once_with(
                parent_storage_group, ref_payload)
        ref_result = self.data.job_list[0]
        act_result = self.provisioning.remove_child_sg_from_parent_sg(
            child_storage_group, parent_storage_group)
        self.assertEqual(ref_result, act_result)

    def test_update_storage_group_qos_success(self):
        """Test update_storage_group_qos."""
        qos_specs = {'maxIOPS': '3000',
                     'DistributionType': 'never',
                     'maxMBPS': '9001'}
        ref_payload = {
            'editStorageGroupActionParam': {
                'setHostIOLimitsParam': {
                    'host_io_limit_io_sec': qos_specs['maxIOPS'],
                    'host_io_limit_mb_sec': qos_specs['maxMBPS'],
                    'dynamicDistribution': qos_specs['DistributionType']}}}
        with mock.patch.object(
                self.provisioning, 'modify_storage_group') as mock_mod:
            message = self.provisioning.update_storagegroup_qos(
                self.data.qos_storagegroup, qos_specs)
            mock_mod.assert_called_once_with(self.data.qos_storagegroup,
                                             ref_payload)
            self.assertIsNotNone(message)

    def test_update_storage_group_qos_negative_input(self):
        """Test update_storage_group_qos no input."""
        with mock.patch.object(
                self.provisioning, 'modify_storage_group'):
            message = self.provisioning.update_storagegroup_qos('fail',
                                                                dict())
            self.assertIsNone(message)

    def test_update_storage_group_qos_exception(self):
        """Test update_storage_group_qos."""
        qos_specs2 = {'maxIOPS': '4000',
                      'DistributionType': 'oops'}
        self.assertRaises(exception.InvalidInputException,
                          self.provisioning.update_storagegroup_qos,
                          self.data.qos_storagegroup, qos_specs2)

    def test_set_host_io_limit_iops(self):
        """Test set_host_io_limit_iops_or_mbps."""
        storage_group = self.data.qos_storagegroup
        iops = '3000'
        dynamic_distribution = 'Always'
        mbps = '9001'
        ref_qos_specs = {'maxIOPS': iops,
                         'DistributionType': dynamic_distribution,
                         'maxMBPS': mbps}
        with mock.patch.object(
                self.provisioning, 'update_storagegroup_qos') as mock_qos:
            self.provisioning.set_host_io_limit_iops_or_mbps(
                storage_group, iops, dynamic_distribution, mbps)
            mock_qos.assert_called_once_with(storage_group, ref_qos_specs)

    def test_delete_storage_group(self):
        """Test delete_storage_group."""
        storage_group_id = self.data.storagegroup_name
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_storagegroup(storage_group_id)
            mock_delete.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.STORAGEGROUP,
                resource_type_id=storage_group_id
            )

    def test_get_volume(self):
        """Test get_volume."""
        vol_details = self.provisioning.get_volume(self.data.device_id)
        self.assertEqual(self.data.volume_details[0], vol_details)

    def test_get_volume_list(self):
        """Test get_volume_list."""
        vol_list = self.provisioning.get_volume_list()
        ref_vol_list = [self.data.device_id, self.data.device_id2]
        self.assertEqual(ref_vol_list, vol_list)

    def test_get_volume_list_over_max_page_size(self):
        """Test get_volume_list with return val > max page size."""
        return_value = {'id': '123', 'count': 3, 'maxPageSize': 2,
                        'resultList': {
                            'result': [{'volumeId':
                                        str(self.data.device_id)},
                                       {'volumeId':
                                        str(self.data.device_id2)},
                                       {'volumeId':
                                        str(self.data.device_id3)}]}}
        page_list = [[{'volumeId': self.data.device_id},
                      {'volumeId': self.data.device_id2}],
                     [{'volumeId': self.data.device_id3}]]
        with mock.patch.object(self.provisioning, 'get_resource',
                               return_value=return_value):
            with mock.patch.object(self.provisioning.common,
                                   'get_iterator_page_list',
                                   side_effect=page_list):
                vol_list = self.provisioning.get_volume_list()
                ref_vol_list = [self.data.device_id, self.data.device_id2,
                                self.data.device_id3]
                self.assertEqual(ref_vol_list, vol_list)

    def test_get_vols_from_storage_group(self):
        """Test get_vols_from_storage_group."""
        vol_list = self.provisioning.get_vols_from_storagegroup(
            self.data.storagegroup_name)
        ref_vol_list = [self.data.device_id, self.data.device_id2]
        self.assertEqual(ref_vol_list, vol_list)
        with mock.patch.object(self.provisioning, 'get_volume_list',
                               return_value=list()):
            vol_list = self.provisioning.get_vols_from_storagegroup(
                self.data.storagegroup_name)
            self.assertIsNotNone(vol_list)
            self.assertEqual(list(), vol_list)

    def test_get_storage_group_from_vol(self):
        """Test get_storage_group_from_vol."""
        storage_group_list = self.provisioning.get_storagegroup_from_vol(
            self.data.device_id)
        self.assertEqual([self.data.storagegroup_name], storage_group_list)

    def test_is_volume_in_storage_group_success(self):
        """Test is_volume_in_storage_group successful."""
        is_vol = self.provisioning.is_volume_in_storagegroup(
            self.data.device_id, self.data.storagegroup_name)
        self.assertTrue(is_vol)

    def test_is_volume_in_storage_group_failure(self):
        """Test is_volume_in_storage_group unsuccessful."""
        is_vol2 = self.provisioning.is_volume_in_storagegroup(
            self.data.device_id, self.data.storagegroup_name_1)
        self.assertFalse(is_vol2)

    def test_find_volume_device_id_success(self):
        """Test find_volume_device_id volume found successfully."""
        with mock.patch.object(self.provisioning, 'get_volume_list',
                               return_value=['00001']):
            device_id = self.provisioning.find_volume_device_id('my-vol')
            self.assertEqual(self.data.device_id, device_id)

    def test_find_volume_device_id_failure(self):
        """Test find_volume_device_id volume not found."""
        with mock.patch.object(self.provisioning, 'get_volume_list',
                               return_value=list()):
            device_id2 = self.provisioning.find_volume_device_id('not-my-vol')
            self.assertIsNone(device_id2)

    def test_find_volume_device_id_vol_name_not_unique(self):
        """Test find_volume_device_id volume not found."""
        with mock.patch.object(self.provisioning, 'get_volume_list',
                               return_value=['00001', '00002' '00003']):
            device_ids = self.provisioning.find_volume_device_id(
                'not-unique-name')
            self.assertIsInstance(device_ids, list)

    def test_find_volume_identifier(self):
        """Test find_volume_identifier."""
        vol_id = self.provisioning.find_volume_identifier(self.data.device_id)
        self.assertEqual('my-vol', vol_id)

    def test_get_size_of_device_on_array(self):
        """Test get_size_of_device_on_array."""
        vol_size = self.provisioning.get_size_of_device_on_array(
            self.data.device_id)
        self.assertEqual(2, vol_size)

    def test_get_size_of_device_on_array_exception(self):
        """Test get_size_of_device_on_array exception."""
        with mock.patch.object(
                self.provisioning, 'get_volume', return_value=dict()):
            self.assertRaises(exception.ResourceNotFoundException,
                              self.provisioning.get_size_of_device_on_array,
                              self.data.device_id)

    def test_modify_volume(self):
        """Test _modify_volume."""
        device_id = self.data.device_id
        ref_payload = dict()
        with mock.patch.object(
                self.provisioning, 'modify_resource') as mock_mod:
            self.provisioning._modify_volume(device_id, ref_payload)
            mock_mod.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.VOLUME,
                resource_type_id=device_id,
                payload=ref_payload
            )
        ref_result = self.data.job_list[0]
        act_result = self.provisioning._modify_volume(device_id, ref_payload)
        self.assertEqual(ref_result, act_result)

    def test_extend_volume(self):
        """Test extend_volume."""
        device_id = self.data.device_id
        new_volume_size = 3

        payload = {'executionOption': 'ASYNCHRONOUS',
                   'editVolumeActionParam': {
                       'expandVolumeParam': {
                           'volumeAttribute': {
                               'volume_size': str(new_volume_size),
                               'capacityUnit': 'GB'}}}}
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.extend_volume(device_id, new_volume_size,
                                            _async=True)
            mock_mod.assert_called_once_with(device_id, payload)
        act_result = self.provisioning.extend_volume(device_id,
                                                     new_volume_size)
        ref_result = self.data.job_list[0]
        self.assertEqual(ref_result, act_result)

    def test_extend_volume_rdf(self):
        """Test extend_volume."""
        device_id = self.data.device_id
        new_volume_size = 3

        payload = {'executionOption': 'ASYNCHRONOUS',
                   'editVolumeActionParam': {
                       'expandVolumeParam': {
                           'volumeAttribute': {
                               'volume_size': str(new_volume_size),
                               'capacityUnit': 'GB'},
                           'rdfGroupNumber': 42}}}
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.extend_volume(device_id, new_volume_size,
                                            _async=True, rdf_group_num=42)
            mock_mod.assert_called_once_with(device_id, payload)
        act_result = self.provisioning.extend_volume(device_id,
                                                     new_volume_size)
        ref_result = self.data.job_list[0]
        self.assertEqual(ref_result, act_result)

    def test_rename_volume_name(self):
        """Test rename_volume."""
        new_name = 'new_name'
        device_id = self.data.device_id
        ref_payload_name = {
            'editVolumeActionParam': {
                'modifyVolumeIdentifierParam': {
                    'volumeIdentifier': {
                        'identifier_name': new_name,
                        'volumeIdentifierChoice': 'identifier_name'}}}}
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.rename_volume(device_id, new_name)
            mock_mod.assert_called_once_with(device_id, ref_payload_name)
        ref_result = self.data.job_list[0]
        act_result = self.provisioning.rename_volume(device_id, new_name)
        self.assertEqual(ref_result, act_result)

    def test_rename_volume_no_name(self):
        """Test rename_volume no name."""
        device_id = self.data.device_id
        ref_payload_no_name = {
            'editVolumeActionParam': {
                'modifyVolumeIdentifierParam': {
                    'volumeIdentifier': {
                        'volumeIdentifierChoice': 'none'}}}}
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.rename_volume(device_id, None)
            mock_mod.assert_called_once_with(device_id, ref_payload_no_name)
        ref_result = self.data.job_list[0]
        act_result = self.provisioning.rename_volume(device_id, None)
        self.assertEqual(ref_result, act_result)

    def test_deallocate_volume(self):
        """Test deallocate_volume."""
        device_id = self.data.device_id
        ref_payload = {'editVolumeActionParam': {
            'freeVolumeParam': {
                'free_volume': 'true'}}}
        with mock.patch.object(
                self.provisioning, '_modify_volume') as mock_mod:
            self.provisioning.deallocate_volume(device_id)
            mock_mod.assert_called_once_with(device_id, ref_payload)
        ref_result = self.data.job_list[0]
        act_result = self.provisioning.deallocate_volume(device_id)
        self.assertEqual(ref_result, act_result)

    def test_delete_volume(self):
        """Test delete_volume."""
        device_id = self.data.device_id
        with mock.patch.object(
                self.provisioning, 'delete_resource') as mock_delete:
            self.provisioning.delete_volume(self.data.device_id)
            mock_delete.assert_called_once_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.VOLUME,
                resource_type_id=device_id)

    def test_get_workload_settings(self):
        """Test get_workload_settings."""
        wl_setting = self.provisioning.get_workload_settings()
        self.assertEqual(self.data.workloadtype['workloadId'], wl_setting)

    def test_update_port_group_port_ids(self):
        """Test _update_port_group_port_ids."""
        port = '{d}:{p}'.format(d=self.data.director_id1,
                                p=self.data.port_id1)
        port_key = [{constants.DIRECTOR_ID: self.data.director_id1,
                     constants.PORT_ID: port}]
        details = {constants.SYMMETRIX_PORT_KEY: port_key}
        corrected_details = self.provisioning._update_port_group_port_ids(
            details)
        corrected_port_id = corrected_details[
            constants.SYMMETRIX_PORT_KEY][0][constants.PORT_ID]
        self.assertEqual(self.data.port_id1, corrected_port_id)

    def test_get_any_director_port(self):
        """Test get_any_director_port."""
        return_val = [{constants.PORT_ID: self.data.port_id1}]
        with mock.patch.object(
            self.provisioning, 'get_director_port_list',
                return_value=return_val) as mck_get_dir_port:
            port = self.provisioning.get_any_director_port(
                self.data.director_id1)
            self.assertEqual(port, self.data.port_id1)
            mck_get_dir_port.assert_called_once_with(
                self.data.director_id1, filters=None)

    def test_format_director_port(self):
        """Test format_director_port."""
        director = self.data.director_id1
        port = self.data.port_id1
        reference_result = '{d}:{p}'.format(d=director, p=port)
        actual_result = self.provisioning.format_director_port(director, port)
        self.assertEqual(reference_result, actual_result)

    @mock.patch.object(provisioning.ProvisioningFunctions,
                       'get_masking_view_list', return_value=['masking_view'])
    def test_get_active_masking_view_connections(self, mck_get_mv):
        """Test get_active_masking_view_connections."""
        connection = self.data.maskingview[0]['maskingViewConnection']
        with mock.patch.object(self.provisioning,
                               'get_masking_view_connections',
                               return_value=connection) as mck_get_conn:
            masking_view, connections = (
                self.provisioning.get_active_masking_view_connections())
            self.assertEqual(connection, connections)
            self.assertIsInstance(masking_view, str)
            mck_get_conn.assert_called_once_with('masking_view')
        mck_get_mv.assert_called_once()

    def test_get_fa_directors(self):
        """Test get_fa_directors."""
        fa_director = self.data.director_id1
        se_director = self.data.director_id2
        directors = [fa_director, se_director]
        with mock.patch.object(self.provisioning, 'get_director_list',
                               return_value=directors) as mck_get_dir:
            fa_directors = self.provisioning.get_fa_directors()
            self.assertEqual([fa_director], fa_directors)
            mck_get_dir.assert_called_once()

    @mock.patch.object(
        provisioning.ProvisioningFunctions, 'get_initiator_list',
        return_value=[pcd.CommonData.initiator, pcd.CommonData.initiator2])
    @mock.patch.object(
        provisioning.ProvisioningFunctions,
        'get_in_use_initiator_list_from_array',
        return_value=[pcd.CommonData.initiator])
    def test_get_available_initiator(self, mck_get_init, mck_get_used_init):
        """Test get_available_initiator."""
        initiator = self.provisioning.get_available_initiator()
        self.assertEqual(self.data.initiator2, initiator)
        mck_get_init.assert_called_once()
        mck_get_used_init.assert_called_once()

    @mock.patch.object(
        provisioning.ProvisioningFunctions, 'get_initiator_list',
        return_value=[pcd.CommonData.initiator, pcd.CommonData.initiator2])
    @mock.patch.object(
        provisioning.ProvisioningFunctions,
        'get_in_use_initiator_list_from_array',
        return_value=[pcd.CommonData.initiator])
    def test_get_available_initiator_filtered(
            self, mck_get_init, mck_get_used_init):
        """Test get_available_initiator."""
        dir_filter = pcd.CommonData.initiator2
        initiator = self.provisioning.get_available_initiator(dir_filter)
        self.assertEqual(self.data.initiator2, initiator)
        mck_get_init.assert_called_once()
        mck_get_used_init.assert_called_once()

    @mock.patch.object(
        provisioning.ProvisioningFunctions,
        'get_in_use_initiator_list_from_array',
        return_value=[pcd.CommonData.initiator])
    def test_get_in_use_initiator(self, mck_get_used_init):
        """Test get_in_use_initiator."""
        initiator = self.provisioning.get_in_use_initiator()
        self.assertEqual(self.data.initiator, initiator)
        mck_get_used_init.assert_called_once()

    @mock.patch.object(
        provisioning.ProvisioningFunctions,
        'get_in_use_initiator_list_from_array',
        return_value=[pcd.CommonData.initiator])
    def test_get_in_use_initiator_filtered(self, mck_get_used_init):
        """Test get_in_use_initiator filtered."""
        dir_filter = pcd.CommonData.initiator
        initiator = self.provisioning.get_in_use_initiator(dir_filter)
        self.assertEqual(self.data.initiator, initiator)
        mck_get_used_init.assert_called_once()

    def test_get_available_initiator_wwn_as_list(self):
        """Test get_available_initiator_wwn_as_list."""
        avail_init = '{d}:{p}:{w}'.format(
            d=self.data.director_id1, p=self.data.port_id1, w=self.data.wwnn1)
        with mock.patch.object(self.provisioning, 'get_available_initiator',
                               return_value=avail_init) as mck_get_init:
            initiator = (
                self.provisioning.get_available_initiator_wwn_as_list())
            self.assertEqual([self.data.wwnn1], initiator)
            mck_get_init.assert_called_once()

    def test_delete_volume_retry(self):
        """Test delete volume with retry decorator."""
        device_id = self.data.device_id
        excep = exception.VolumeBackendAPIException
        with mock.patch.object(
                self.provisioning, 'delete_resource', side_effect=[
                    excep('random exception 1'), excep('random exception 2'),
                    None]
        ) as mock_delete:
            self.provisioning.delete_volume(self.data.device_id)
            call_count = mock_delete.call_count
            self.assertEqual(3, call_count)
            mock_delete.assert_called_with(
                category=constants.SLOPROVISIONING,
                resource_level=constants.SYMMETRIX,
                resource_level_id=self.data.array,
                resource_type=constants.VOLUME,
                resource_type_id=device_id)

    @mock.patch.object(
        provisioning.ProvisioningFunctions, 'modify_storage_group',
        return_value=dict())
    def test_add_existing_volume_to_storage_group_multi_hop(
            self, mck_sg_modify):
        """Test add_existing_volume_to_storage_group for SRDF protected SG."""
        self.provisioning.add_existing_volume_to_storage_group(
            storage_group_id=self.data.storagegroup_name, vol_ids=["00123"],
            remote_array_1_id=self.data.remote_array,
            remote_array_1_sgs=[self.data.storagegroup_name],
            remote_array_2_id=self.data.remote_array2,
            remote_array_2_sgs=[self.data.storagegroup_name])
        mck_sg_modify.assert_called_once_with(
            self.data.storagegroup_name,
            self.data.sg_expand_payload_multi_site)

    @mock.patch.object(
        provisioning.ProvisioningFunctions, 'modify_storage_group',
        return_value=dict())
    def test_add_existing_volume_to_storage_group_single_hop(
            self, mck_sg_modify):
        """Test add_existing_volume_to_storage_group for SRDF protected SG."""
        self.provisioning.add_existing_volume_to_storage_group(
            storage_group_id=self.data.storagegroup_name, vol_ids=["00123"],
            remote_array_1_id=self.data.remote_array,
            remote_array_1_sgs=[self.data.storagegroup_name])
        mck_sg_modify.assert_called_once_with(
            self.data.storagegroup_name,
            self.data.sg_expand_payload_basic_srdf)
