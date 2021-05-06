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
"""test_pyu4v_ci_provisioning.py."""
import os
from PyU4V.tests.ci_tests import base
from PyU4V.utils import constants
from PyU4V.utils import exception
from PyU4V.utils import file_handler
import random
import re
import testtools
import time


class CITestProvisioning(base.TestBaseTestCase, testtools.TestCase):
    """Test Provisioning."""

    def setUp(self):
        """setUp."""
        super(CITestProvisioning, self).setUp()
        self.provisioning = self.conn.provisioning

    def test_get_array(self):
        """Test get_array."""
        response = self.provisioning.get_array(array_id=self.conn.array_id)
        self.assertTrue(response)
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('symmetrixId'), self.conn.array_id)
        self.assertTrue(response.get('local'))

    def test_get_director(self):
        """Test get_director."""
        availability = 'availability'
        director_number = 'director_number'
        director_slot_number = 'director_slot_number'
        director_list = self.provisioning.get_director_list()
        for director in director_list:
            director_details = self.provisioning.get_director(director)
            self.assertIsInstance(director_details, dict)
            self.assertIn(availability, director_details)
            self.assertIn(director_number, director_details)
            self.assertIn(director_slot_number, director_details)
            self.assertIn(constants.DIRECTOR_ID, director_details)
            self.assertIn(constants.NUM_OF_PORTS, director_details)
            self.assertIn(constants.NUM_OF_CORES, director_details)
            self.assertIsInstance(director_details[availability], str)
            self.assertIsInstance(director_details[director_number], int)
            self.assertIsInstance(director_details[director_slot_number], int)
            director_id = director_details[constants.DIRECTOR_ID]
            self.assertIsInstance(director_id, str)
            self.assertIsInstance(
                director_details[constants.NUM_OF_PORTS], int)
            self.assertIsInstance(
                director_details[constants.NUM_OF_CORES], int)
            self.assertIsNotNone(re.match(constants.DIRECTOR_SEARCH_PATTERN,
                                          director_id))

    def test_get_director_list(self):
        """Test get_director_list."""
        director_list = self.provisioning.get_director_list()
        self.assertTrue(len(director_list) > 0)
        self.assertIsInstance(director_list, list)
        for director in director_list:
            self.assertIsInstance(director, str)
            self.assertIsNotNone(re.match(constants.DIRECTOR_SEARCH_PATTERN,
                                          director))

    def test_get_director_port(self):
        """Test get_director_port."""
        director_port_list = self.provisioning.get_port_list()
        for director_port in director_port_list:
            director = director_port[constants.DIRECTOR_ID]
            port = director_port[constants.PORT_ID]
            port_details = self.provisioning.get_director_port(
                director, port)
            self._validate_director_port(port_details)

    def test_get_director_port_list(self):
        """Test get_director_port_list."""
        director_list = self.provisioning.get_director_list()
        director = director_list[0]
        director_port_list = self.provisioning.get_director_port_list(
            director)
        self.assertIsInstance(director_port_list, list)
        for director_port in director_port_list:
            self.assertIsInstance(director_port, dict)
            self.assertIn(constants.DIRECTOR_ID, director_port)
            self.assertIn(constants.PORT_ID, director_port)
            director_id = director_port[constants.DIRECTOR_ID]
            port_id = director_port[constants.PORT_ID]
            self.assertIsInstance(director_id, str)
            self.assertIsInstance(port_id, str)
            self.assertIsNotNone(
                re.match(constants.DIRECTOR_SEARCH_PATTERN, director_id))
            self.assertIsNotNone(
                re.match(constants.PORT_SEARCH_PATTERN, port_id))

    def test_get_port_identifier(self):
        """Test get_port_identifier."""
        director_port_list = self.provisioning.get_port_list()
        for director_port in director_port_list:
            director = director_port[constants.DIRECTOR_ID]
            port = director_port[constants.PORT_ID]
            port_identifier = self.provisioning.get_port_identifier(
                director, port)
            if port_identifier is not None:
                self.assertIsInstance(port_identifier, str)

    def test_create_empty_host(self):
        """Test create_host create empty host."""
        host_name = self.create_empty_host()
        host_list = self.provisioning.get_host_list()
        get_host_details = self.provisioning.get_host(host_name)
        initiator_count = get_host_details[constants.NUM_OF_INITIATORS]
        self.assertIn(host_name, host_list)
        self.assertIsNotNone(get_host_details)
        self.assertEqual(0, initiator_count)

    def test_create_host_with_initiator_list_host_flags(self):
        """Test create_host with initiator list."""
        available_initiator_list = (
            self.provisioning.get_available_initiator_wwn_as_list())
        if not available_initiator_list:
            self.skipTest('test_create_host_with_initiator_list_host_flags '
                          '- Unable to get an available initiator.')
        host_flags = constants.HOST_FLAGS
        host_flags[constants.SCSI_3] = {constants.OVERRIDE: constants.TRUE,
                                        constants.ENABLED: constants.TRUE}
        host_flags[constants.CONSISTENT_LUN] = constants.TRUE
        host_name = self.create_host(available_initiator_list, host_flags)
        host_list = self.provisioning.get_host_list()
        get_host_details = self.provisioning.get_host(host_name)
        initiator_count = get_host_details[constants.NUM_OF_INITIATORS]
        initiator = get_host_details[constants.INITIATOR]
        enabled_flags = get_host_details[constants.ENABLED_FLAGS]
        consitent_lun = get_host_details[constants.CONSISTENT_LUN]
        self.assertIn(host_name, host_list)
        self.assertIsNotNone(get_host_details)
        self.assertEqual(1, initiator_count)
        self.assertEqual(available_initiator_list, initiator)
        self.assertEqual(constants.SCSI_3_FLAG, enabled_flags)
        self.assertEqual(consitent_lun, True)

    def test_create_host_initiator_file(self):
        """Test create_host with initiator file."""
        available_initiator_list = (
            self.provisioning.get_available_initiator_wwn_as_list())
        if not available_initiator_list:
            self.skipTest('test_create_host_initiator_file '
                          '- Unable to get an available initiator.')
        csv_file_name = 'test.csv'
        temp_dir = self.create_temp_directory()
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        with open(csv_file_path, 'w') as tmp:
            for initiator in available_initiator_list:
                tmp.write(initiator)
        host_name = self.create_host(init_file=csv_file_path)
        host_list = self.provisioning.get_host_list()
        host_details = self.provisioning.get_host(host_name)
        initiator_count = host_details[constants.NUM_OF_INITIATORS]
        initiator = host_details[constants.INITIATOR]
        self.assertIsNotNone(host_details)
        self.assertIn(host_name, host_list)
        self.assertIsNotNone(host_details)
        self.assertEqual(1, initiator_count)
        self.assertEqual(available_initiator_list, initiator)

    def test_create_host_async(self):
        """Test create_host with async update."""
        host_name = self.create_host(_async=True)
        host_details = self.provisioning.get_host(host_name)
        host_list = self.provisioning.get_host_list()
        self.assertIsNotNone(host_details)
        self.assertIn(host_name, host_list)

    def test_modify_host_edit_host_flags(self):
        """Test modify_host edit host flags."""
        host_name = self.create_empty_host()
        host_flags = constants.HOST_FLAGS
        host_flags[constants.SPC2_PROTOCOL_VERSION] = {
            constants.OVERRIDE: constants.TRUE,
            constants.ENABLED: constants.TRUE}
        self.provisioning.modify_host(
            host_name, host_flag_dict=host_flags)
        host_details = self.provisioning.get_host(host_name)
        enabled_flags = host_details[constants.ENABLED_FLAGS]
        self.assertIn(constants.SPC2_PROTOCOL_VERSION_FLAG, enabled_flags)

    def test_modify_host_edit_name(self):
        """Test modify_host edit name."""
        host_name = self.create_empty_host()
        host_list = self.provisioning.get_host_list()
        self.assertIn(host_name, host_list)
        new_name = self.generate_name(constants.HOST)
        self.provisioning.modify_host(host_name, new_name=new_name)
        self.addCleanup(self.delete_host, new_name)
        host_list = self.provisioning.get_host_list()
        self.assertIn(new_name, host_list)
        self.assertNotIn(host_name, host_list)

    def test_modify_host_add_initiator(self):
        """Test modify_host add initiator."""
        host_name = self.create_empty_host()
        available_initiator = (
            self.provisioning.get_available_initiator_wwn_as_list())
        if not available_initiator:
            self.skipTest('test_modify_host_add_initiator '
                          '- Unable to get an available initiator.')
        self.provisioning.modify_host(host_name,
                                      add_init_list=available_initiator)
        host_details = self.provisioning.get_host(host_name)
        initiator = host_details[constants.INITIATOR]
        self.assertEqual(available_initiator, initiator)

    def test_modify_host_remove_initiator(self):
        """Test modify_host remove initiator."""
        available_initiator = (
            self.provisioning.get_available_initiator_wwn_as_list())
        if not available_initiator:
            self.skipTest('test_modify_host_remove_initiator '
                          '- Unable to get an available initiator.')
        host_name = self.create_host(available_initiator)
        self.provisioning.modify_host(
            host_name, remove_init_list=available_initiator)
        host_details = self.provisioning.get_host(host_name)
        initiator_count = host_details[constants.NUM_OF_INITIATORS]
        self.assertEqual(0, initiator_count)
        self.assertNotIn(constants.INITIATOR, host_details)

    def test_modify_host_exception(self):
        """Test modify_host exception."""
        self.assertRaises(exception.InvalidInputException,
                          self.provisioning.modify_host, 'Test_name')

    def test_delete_host(self):
        """Test delete_host."""
        host_name = self.create_empty_host()
        host_list = self.provisioning.get_host_list()
        self.addCleanup(self.delete_host, host_name)
        self.assertIn(host_name, host_list)
        self.delete_host(host_name)
        host_list = self.provisioning.get_host_list()
        self.assertNotIn(host_name, host_list)

    def test_get_mvs_from_host(self):
        """Test get_mvs_from_host."""
        masking_view_list = self.provisioning.get_masking_view_list()
        # _Cloud masking views throw errors with GET requests
        masking_view_list = [mv for mv in masking_view_list if
                             '_CLOUD' not in mv]
        for masking_view in masking_view_list:
            masking_view_details = (
                self.provisioning.get_masking_view(masking_view))
            if constants.HOST_ID in masking_view_details:
                host_id = masking_view_details[constants.HOST_ID]
            else:
                host_id = masking_view_details[constants.HOST_GROUP_ID]
            host_masking_views = (
                self.provisioning.get_mvs_from_host(host_id))
            self.assertIsInstance(host_masking_views, list)
            self.assertIn(masking_view, host_masking_views)

    def test_get_masking_views_from_host(self):
        """Test get_masking_views_from_host."""
        masking_view_list = self.provisioning.get_masking_view_list()
        # _Cloud masking views throw errors with GET requests
        masking_view_list = [mv for mv in masking_view_list if
                             '_CLOUD' not in mv]
        for masking_view in masking_view_list:
            masking_view_details = (
                self.provisioning.get_masking_view(masking_view))
            if constants.HOST_ID in masking_view_details:
                host_id = masking_view_details[constants.HOST_ID]
            else:
                host_id = masking_view_details[constants.HOST_GROUP_ID]
            host_masking_views = (
                self.provisioning.get_masking_views_from_host(host_id))
            self.assertIsInstance(host_masking_views, list)
            self.assertIn(masking_view, host_masking_views)

    def test_get_initiator_ids_from_host(self):
        """Test get_initiator_ids_from_host."""
        host_list = self.provisioning.get_host_list()
        host_list = [host for host in host_list if '_CLOUD' not in host]
        for host in host_list:
            host_details = self.provisioning.get_host(host)
            initiator_ids = (
                self.provisioning.get_initiator_ids_from_host(host))
            self.assertIsInstance(initiator_ids, list)
            if host_details[constants.NUM_OF_INITIATORS] > 0:
                initiators = host_details[constants.INITIATOR]
                for initiator in initiators:
                    self.assertIsInstance(initiator, str)

    def test_create_host_group_host_flags(self):
        """Test create_host_group."""
        host_flags = constants.HOST_FLAGS
        host_flags[constants.SCSI_3] = {constants.OVERRIDE: constants.TRUE,
                                        constants.ENABLED: constants.TRUE}
        host_group_name = self.create_host_group(host_flags)
        host_group_list = self.provisioning.get_host_group_list()
        host_group = self.provisioning.get_host_group(host_group_name)
        enabled_flags = host_group[constants.ENABLED_FLAGS]
        self.assertIn(host_group_name, host_group_list)
        self.assertIsNotNone(host_group)
        self.assertEqual(constants.SCSI_3_FLAG, enabled_flags)

    def test_create_hostgroup(self):
        """Test create_hostgroup."""
        host_name = self.create_empty_host()
        host_group_name = self.generate_name('host_group')
        self.conn.provisioning.create_hostgroup(
            host_group_name, [host_name])
        self.addCleanup(self.delete_host_group, host_group_name)
        host_group_list = self.provisioning.get_host_group_list()
        self.assertIn(host_group_name, host_group_list)

    def test_create_host_group_async(self):
        """Test create_host_group async."""
        host_group_name = self.create_host_group(_async=True)
        host_group_list = self.provisioning.get_host_group_list()
        host_group = self.provisioning.get_host_group(host_group_name)
        self.assertIn(host_group_name, host_group_list)
        self.assertIsNotNone(host_group)

    def test_modify_host_group_edit_name(self):
        """Test modify host group edit name."""
        host_group_name = self.create_host_group()
        new_name = self.generate_name(constants.HOST_GROUP)
        host_group_list = self.provisioning.get_host_group_list()
        self.assertIn(host_group_name, host_group_list)
        self.assertNotIn(new_name, host_group_list)
        self.provisioning.modify_host_group(host_group_name, new_name=new_name)
        host_group_list = self.provisioning.get_host_group_list()
        self.addCleanup(self.delete_host_group, new_name)
        self.assertNotIn(host_group_name, host_group_list)
        self.assertIn(new_name, host_group_list)

    def test_modify_host_group_add_host(self):
        """Test modify host group add host."""
        host_group_name = self.create_host_group()
        host_group_details = self.provisioning.get_host_group(host_group_name)
        host_name = self.create_empty_host()
        self.assertEqual(1, host_group_details[constants.NUM_OF_HOSTS])
        self.provisioning.modify_host_group(host_group_name,
                                            add_host_list=[host_name])
        host_group_details = self.provisioning.get_host_group(host_group_name)
        hosts_in_group = host_group_details[constants.HOST]
        host_was_added = False
        for item in hosts_in_group:
            if item[constants.HOST_ID] == host_name:
                host_was_added = True
        self.assertEqual(2, host_group_details[constants.NUM_OF_HOSTS])
        self.assertTrue(host_was_added)

    def test_modify_hostgroup_add_host(self):
        """Test modify hostgroup add host."""
        host_group_name = self.create_host_group()
        host_group_details = self.provisioning.get_host_group(host_group_name)
        host_name = self.create_empty_host()
        self.assertEqual(1, host_group_details[constants.NUM_OF_HOSTS])
        self.provisioning.modify_hostgroup(host_group_name,
                                           add_host_list=[host_name])
        host_group_details = self.provisioning.get_host_group(host_group_name)
        hosts_in_group = host_group_details[constants.HOST]
        host_was_added = False
        for item in hosts_in_group:
            if item[constants.HOST_ID] == host_name:
                host_was_added = True
        self.assertEqual(2, host_group_details[constants.NUM_OF_HOSTS])
        self.assertTrue(host_was_added)

    def test_modify_host_group_remove_host(self):
        """Test modify host group remove host."""
        host_name_1 = self.create_empty_host()
        host_name_2 = self.create_empty_host()
        host_group_name = self.generate_name(constants.HOST_GROUP)
        host_group_details = self.provisioning.create_host_group(
            host_group_name, [host_name_1, host_name_2])
        self.addCleanup(self.delete_host_group, host_group_name)
        self.assertEqual(2, host_group_details[constants.NUM_OF_HOSTS])
        self.provisioning.modify_host_group(host_group_name,
                                            remove_host_list=[host_name_2])
        host_group_details = self.provisioning.get_host_group(host_group_name)
        self.assertEqual(1, host_group_details[constants.NUM_OF_HOSTS])
        remaining_host = host_group_details[
            constants.HOST][0][constants.HOST_ID]
        self.assertEqual(host_name_1, remaining_host)
        self.assertNotEqual(host_name_2, remaining_host)

    def test_modify_host_group_edit_flags(self):
        """Test modify_host_group_edit_flags."""

        host_group_name = self.create_host_group()
        host_group_details = self.provisioning.get_host_group(host_group_name)

        enabled_flags = host_group_details[constants.ENABLED_FLAGS]
        self.assertEqual('', enabled_flags)

        try:
            host_groups_hosts = host_group_details.get(constants.HOST)
            host_name = host_groups_hosts[0].get(constants.HOST_ID)
            host_flags = constants.HOST_FLAGS
            host_flags[constants.SCSI_3] = {constants.OVERRIDE: constants.TRUE,
                                            constants.ENABLED: constants.TRUE}
            self.provisioning.modify_host(host_name,
                                          host_flag_dict=host_flags)
            self.provisioning.modify_host_group(host_group_name,
                                                host_flag_dict=host_flags)
            host_group_details = self.provisioning.get_host_group(
                host_group_name)
            enabled_flags = host_group_details[constants.ENABLED_FLAGS]
            self.assertIn(constants.SCSI_3_FLAG, enabled_flags)
        except exception.VolumeBackendAPIException:
            self.skipTest('Erroneous error for consistent lun violation which '
                          'is only appearing in CI sporadically, not possible '
                          'to pin down source at present but manual tests '
                          'pass for the feature with no issues.')

    def test_get_hostgroup(self):
        """Test get_hostgroup."""
        host_group_list = self.conn.provisioning.get_host_group_list()
        for host_group in host_group_list:
            host_group_details = self.conn.provisioning.get_hostgroup(
                host_group)
            self.assertIsNotNone(host_group_details)
            self.assertIsInstance(host_group_details, dict)

    def test_get_hostgroup_list(self):
        """Test get_hostgroup_list."""
        host_group_list = self.conn.provisioning.get_hostgroup_list()
        self.assertIsNotNone(host_group_list)
        self.assertIsInstance(host_group_list, list)

    def test_modify_host_group_exception(self):
        """Test modify_host exception."""
        self.assertRaises(exception.InvalidInputException,
                          self.provisioning.modify_host_group, 'test')

    def test_delete_host_group(self):
        """Test delete_host_group."""
        host_group_name = self.create_host_group()
        host_group_list = self.provisioning.get_host_group_list()
        self.assertIn(host_group_name, host_group_list)
        self.provisioning.delete_host_group(host_group_name)
        host_group_list = self.provisioning.get_host_list()
        self.assertNotIn(host_group_name, host_group_list)

    def test_delete_hostgroup(self):
        """Test delete_hostgroup."""
        host_group_name = self.create_host_group()
        host_group_list = self.provisioning.get_host_group_list()
        self.assertIn(host_group_name, host_group_list)
        self.provisioning.delete_hostgroup(host_group_name)
        host_group_list = self.provisioning.get_host_list()
        self.assertNotIn(host_group_name, host_group_list)

    def test_get_initiator(self):
        """Test get_initiator."""
        initiator_list = self.provisioning.get_initiator_list()
        for initiator in initiator_list:
            initiator_details = self.provisioning.get_initiator(initiator)
            self._validate_initiator_details(initiator_details)

    def test_get_initiator_list(self):
        """Test get_initiator_list."""
        initiator_list = self.provisioning.get_initiator_list()
        self.assertIsInstance(initiator_list, list)
        for initiator in initiator_list:
            self.assertIsInstance(initiator, str)
            self.assertIsNotNone(
                re.match(constants.INITIATOR_SEARCH_PATTERN, initiator))

    def test_get_inuse_initiator_list_from_array(self):
        """Test get_in_use_initiator_list_from_array."""
        in_use_list = self.provisioning.get_in_use_initiator_list_from_array()
        self.assertIsInstance(in_use_list, list)
        for initiator in in_use_list:
            self.assertIsInstance(initiator, str)
            self.assertIsNotNone(
                re.match(constants.INITIATOR_SEARCH_PATTERN, initiator))

    def test_modify_initiator_remove_masking_entry(self):
        """Test modify_initiator remove masking entry."""
        initiator = self.provisioning.get_available_initiator()
        if not initiator:
            self.skipTest('test_modify_initiator_remove_masking_entry '
                          '- Unable to get an available initiator.')
        self.assertRaises(
            exception.VolumeBackendAPIException,
            self.provisioning.modify_initiator,
            initiator, remove_masking_entry=constants.TRUE)

    def test_modify_initiator_replace_initiator(self):
        """Test modify_initiator replace initiator."""
        director_type = 'FA'
        initiator_1 = self.provisioning.get_in_use_initiator(director_type)
        initiator_2 = self.provisioning.get_available_initiator(director_type)
        if not initiator_1 or not initiator_2:
            self.skipTest('test_modify_initiator_replace_initiator '
                          '- Unable to get an available initiator.')
        initiator_1_details = self.provisioning.get_initiator(initiator_1)
        initiator_2_details = self.provisioning.get_initiator(initiator_2)
        initiator_1_id = initiator_1_details[constants.INITIATOR_ID]
        initiator_2_id = initiator_2_details[constants.INITIATOR_ID]
        symmetrix_port_key = initiator_1_details[
            constants.SYMMETRIX_PORT_KEY][0]
        initiator_1_director_port = self.provisioning.format_director_port(
            symmetrix_port_key[constants.DIRECTOR_ID],
            symmetrix_port_key[constants.PORT_ID])
        self.provisioning.modify_initiator(
            initiator_1, replace_init=initiator_2_id)
        updated_initiator = '{dp}:{id}'.format(
            dp=initiator_1_director_port, id=initiator_2_id)
        result = self.provisioning.get_initiator(updated_initiator)
        self.assertIsNotNone(result)
        self.assertEqual(initiator_2_id, result[constants.INITIATOR_ID])
        self.provisioning.modify_initiator(
            updated_initiator, replace_init=initiator_1_id)

    def test_modify_initiator_rename_alias(self):
        """Test modify_initiator rename alias."""
        initiator = self.provisioning.get_available_initiator()
        if not initiator:
            self.skipTest('test_modify_initiator_rename_alias '
                          '- Unable to get an available initiator.')
        initiator_details = self.provisioning.get_initiator(initiator)
        initiator_id = initiator_details[constants.INITIATOR_ID]
        old_alias = (initiator_id, initiator_id)
        if constants.ALIAS in initiator_details:
            old_alias = tuple(initiator_details[constants.ALIAS].split('/'))
        new_alias = (
            'pyu4v_ci', 'pyu4v_alias-{}'.format(round(time.time())))
        new_alias_str = new_alias[0] + '/' + new_alias[1]
        self.provisioning.modify_initiator(initiator, rename_alias=new_alias)
        initiator_details = self.provisioning.get_initiator(initiator)
        try:
            self.assertEqual(
                new_alias_str, initiator_details[constants.ALIAS])
        finally:
            self.provisioning.modify_initiator(
                initiator, rename_alias=old_alias)

    def test_modify_initiator_set_fcid(self):
        """Test modify_initiator set fcid."""
        self.skipTest('test_modify_initiator_set_fcid - OPT 564116')
        initiator = self.provisioning.get_in_use_initiator()
        initiator_details = self.provisioning.get_initiator(initiator)
        old_fcid = ''
        if constants.FCID in initiator_details:
            old_fcid = initiator_details[constants.FCID]
        new_fcid = '999999'
        self.provisioning.modify_initiator(initiator, set_fcid=new_fcid)
        initiator_details = self.provisioning.get_initiator(initiator)
        self.assertEqual(new_fcid, initiator_details[constants.FCID])
        self.provisioning.modify_initiator(initiator, set_fcid=old_fcid)

    def test_modify_initiator_change_initiator_flags(self):
        """Test modify_initiator change initiator flags."""
        initiator_name = '1%015x' % random.randrange(16**15)
        host = self.create_host(initiator_list=[initiator_name])
        port_group_name, _ = self.create_port_group()
        masking_view_name = self.generate_name('masking_view')
        storage_group_name = self.create_empty_storage_group()
        self.provisioning.add_new_volume_to_storage_group(
            storage_group_name, 1, 1, 'GB')
        device_id = (
            self.provisioning.get_volumes_from_storage_group(
                storage_group_name)[0])
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        self.provisioning.create_masking_view_existing_components(
            port_group_name, masking_view_name, storage_group_name, host)
        self.addCleanup(self.delete_masking_view, masking_view_name)
        initiator_list = self.provisioning.get_initiator_list()
        initiator = [x for x in initiator_list if initiator_name in x][0]
        flags = constants.HOST_FLAGS
        flags.pop(constants.CONSISTENT_LUN, None)
        flags.pop(constants.VOLUME_SET_ADDRESSING, None)
        flags[constants.OPENVMS] = {constants.OVERRIDE: constants.TRUE,
                                    constants.ENABLED: constants.TRUE}
        flags[constants.AVOID_RESET_BROADCAST] = {
            constants.OVERRIDE: constants.TRUE,
            constants.ENABLED: constants.TRUE}
        self.provisioning.modify_initiator(initiator, initiator_flags=flags)
        initiator_details = self.provisioning.get_initiator(initiator)
        initiator_flags = initiator_details[constants.ENABLED_FLAGS]
        self.assertIn(constants.OPENVMS_FLAG, initiator_flags)
        self.assertIn(constants.AVOID_RESET_BROADCAST_FLAG, initiator_flags)
        flags[constants.OPENVMS] = {constants.OVERRIDE: constants.FALSE,
                                    constants.ENABLED: constants.FALSE}
        flags[constants.AVOID_RESET_BROADCAST] = {
            constants.OVERRIDE: constants.FALSE,
            constants.ENABLED: constants.FALSE}
        self.provisioning.modify_initiator(initiator, initiator_flags=flags)
        initiator_details = self.provisioning.get_initiator(initiator)
        if constants.ENABLED_FLAGS in initiator_flags:
            initiator_flags = initiator_details[constants.ENABLED_FLAGS]
            self.assertNotIn(constants.OPENVMS_FLAG, initiator_flags)
            self.assertNotIn(
                constants.AVOID_RESET_BROADCAST_FLAG, initiator_flags)

    def test_modify_initiator_exception(self):
        """Test modify_initiator replace_initiator."""
        self.assertRaises(exception.InvalidInputException,
                          self.provisioning.modify_initiator,
                          constants.INITIATOR)

    def test_is_initiator_in_host_success(self):
        """Test is_initiator_in_host where initiator is in host."""
        initiator = self.provisioning.get_in_use_initiator()
        result = self.provisioning.is_initiator_in_host(initiator)
        self.assertTrue(result)

    def test_is_initiator_in_host_failure(self):
        """Test is_initiator_in_host where initiator is not in host."""
        initiator = self.provisioning.get_available_initiator()
        if not initiator:
            self.skipTest('test_is_initiator_in_host_failure '
                          '- Unable to get an available initiator.')
        result = self.provisioning.is_initiator_in_host(initiator)
        self.assertFalse(result)

    def test_get_initiator_group_from_initiator_group(self):
        """Test get_initiator_group_from_initiator init group exists."""
        initiator = self.provisioning.get_in_use_initiator()
        initiator_details = self.provisioning.get_initiator(initiator)
        group = self.provisioning.get_initiator_group_from_initiator(
            initiator)
        self.assertIsNotNone(group)
        self.assertIn(constants.HOST, initiator_details)
        self.assertEqual(initiator_details[constants.HOST], group)

    def test_get_initiator_group_from_initiator_no_group(self):
        """Test get_initiator_group_from_initiator no initiator group."""
        initiator = self.provisioning.get_available_initiator()
        if not initiator:
            self.skipTest('test_get_initiator_group_from_initiator_no_group '
                          '- Unable to get an available initiator.')
        initiator_details = self.provisioning.get_initiator(initiator)
        group = self.provisioning.get_initiator_group_from_initiator(
            initiator)
        self.assertIsNone(group)
        self.assertNotIn(constants.HOST, initiator_details)

    def test_get_masking_view_list(self):
        """Test get_masking_view_list."""
        masking_view_list = self.provisioning.get_masking_view_list()
        self.assertIsNotNone(masking_view_list)
        for masking_view in masking_view_list:
            self.assertIsInstance(masking_view, str)

    def test_get_masking_view(self):
        """Test get_masking_view."""
        masking_view_list = self.provisioning.get_masking_view_list()[3:]
        for masking_view in masking_view_list:
            if not masking_view.startswith('_'):
                masking_view_details = self.provisioning.get_masking_view(
                    masking_view)
                self.assertIsNotNone(masking_view_details)
                self.assertIn(constants.MASKING_VIEW_ID, masking_view_details)
                self.assertIn(constants.PORT_GROUP_ID, masking_view_details)
                self.assertIn(
                    constants.STORAGE_GROUP_ID_CAMEL, masking_view_details)
                self.assertIsInstance(
                    masking_view_details[constants.MASKING_VIEW_ID], str)
                self.assertIsInstance(
                    masking_view_details[constants.PORT_GROUP_ID], str)
                self.assertIsInstance(
                    masking_view_details[constants.STORAGE_GROUP_ID_CAMEL],
                    str)
                if constants.HOST_ID in masking_view_details:
                    self.assertIsInstance(
                        masking_view_details[constants.HOST_ID], str)
                if constants.HOST_GROUP_ID in masking_view_details:
                    self.assertIsInstance(
                        masking_view_details[constants.HOST_GROUP_ID], str)

    def test_create_masking_view_existing_components_host(self):
        """Test create_masking_view_existing_components with host."""
        masking_view_name = self.generate_name('masking_view')
        port_group_name, _ = self.create_port_group()
        host_name = self.create_empty_host()
        storage_group_name = self.create_empty_storage_group()
        volume_name = self.generate_name()
        device = (
            self.conn.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, 1))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device)
        masking_view_details = (
            self.conn.provisioning.create_masking_view_existing_components(
                port_group_name, masking_view_name, storage_group_name,
                host_name))
        self.addCleanup(self.delete_masking_view, masking_view_name)
        masking_view_list = self.provisioning.get_masking_view_list()
        self.assertIn(masking_view_name, masking_view_list)
        self.assertIn(constants.MASKING_VIEW_ID, masking_view_details)
        self.assertIn(constants.HOST_ID, masking_view_details)
        self.assertIn(constants.PORT_GROUP_ID, masking_view_details)
        self.assertIn(constants.STORAGE_GROUP_ID_CAMEL, masking_view_details)
        masking_view_id = masking_view_details[constants.MASKING_VIEW_ID]
        host_id = masking_view_details[constants.HOST_ID]
        port_group_id = masking_view_details[constants.PORT_GROUP_ID]
        storage_group_id = masking_view_details[
            constants.STORAGE_GROUP_ID_CAMEL]
        self.assertIsInstance(masking_view_id, str)
        self.assertIsInstance(host_id, str)
        self.assertIsInstance(port_group_id, str)
        self.assertIsInstance(storage_group_id, str)
        self.assertEqual(masking_view_name, masking_view_id)
        self.assertEqual(host_name, host_id)
        self.assertEqual(port_group_name, port_group_id)
        self.assertEqual(storage_group_name, storage_group_id)

    def test_create_masking_view_existing_components_host_group(self):
        """Test create_masking_view_existing_components with host group."""
        masking_view_name = self.generate_name('masking_view')
        port_group_name, _ = self.create_port_group()
        host_group_name = self.create_host_group()
        storage_group_name = self.create_empty_storage_group()
        volume_name = self.generate_name()
        device = (
            self.conn.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, 1))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device)
        masking_view_details = (
            self.conn.provisioning.create_masking_view_existing_components(
                port_group_name, masking_view_name, storage_group_name,
                host_group_name))
        self.addCleanup(self.delete_masking_view, masking_view_name)
        masking_view_list = self.provisioning.get_masking_view_list()
        self.assertIn(masking_view_name, masking_view_list)
        self.assertIn(constants.HOST_GROUP_ID, masking_view_details)
        host_group_id = masking_view_details[constants.HOST_GROUP_ID]
        self.assertIsInstance(host_group_id, str)
        self.assertEqual(host_group_name, host_group_id)

    def test_create_masking_view_existing_components_async(self):
        """Test create_masking_view_existing_components with async flag."""
        masking_view_name, _ = self.create_masking_view(_async=True)
        masking_view_list = self.provisioning.get_masking_view_list()
        self.assertIn(masking_view_name, masking_view_list)

    def test_create_masking_view_existing_components_exception(self):
        """Test create_masking_view_existing_components exception."""
        self.assertRaises(
            exception.InvalidInputException,
            self.provisioning.create_masking_view_existing_components,
            'port_group_name', 'masking_view_name', 'storage_group_name')

    def test_get_masking_views_from_storage_group(self):
        """Test get_masking_views_from_storage_group."""
        masking_view_name, masking_view_details = self.create_masking_view()
        storage_group = masking_view_details[constants.STORAGE_GROUP_ID_CAMEL]
        returned_masking_view_list = (
            self.provisioning.get_masking_view_from_storage_group(
                storage_group))
        self.assertIsNotNone(returned_masking_view_list)
        self.assertIsInstance(returned_masking_view_list, list)
        returned_masking_view = returned_masking_view_list[0]
        self.assertIsInstance(returned_masking_view, str)
        self.assertEqual(masking_view_name, returned_masking_view)

    def test_get_masking_views_by_initiator_group(self):
        """Test get_masking_views_by_initiator_group."""
        masking_view_name, masking_view_details = self.create_masking_view()
        initiator_group = masking_view_details[constants.HOST_ID]
        returned_masking_view_list = (
            self.provisioning.get_masking_views_by_initiator_group(
                initiator_group))
        self.assertIsNotNone(returned_masking_view_list)
        self.assertIsInstance(returned_masking_view_list, list)
        returned_masking_view = returned_masking_view_list[0]
        self.assertIsInstance(returned_masking_view, str)
        self.assertEqual(masking_view_name, returned_masking_view)

    def test_get_masking_views_by_host(self):
        """Test get_masking_views_by_host."""
        masking_view_name, masking_view_details = self.create_masking_view()
        initiator_group = masking_view_details[constants.HOST_ID]
        returned_masking_view_list = (
            self.provisioning.get_masking_views_by_host(
                initiator_group))
        self.assertIsNotNone(returned_masking_view_list)
        self.assertIsInstance(returned_masking_view_list, list)
        returned_masking_view = returned_masking_view_list[0]
        self.assertIsInstance(returned_masking_view, str)
        self.assertEqual(masking_view_name, returned_masking_view)

    def test_get_element_from_masking_view_port_group(self):
        """Test get_element_from_masking_view port group."""
        masking_view_name, masking_view_details = self.create_masking_view()
        port_group_name = self.provisioning.get_element_from_masking_view(
            masking_view_name, portgroup=True)
        self.assertIsNotNone(port_group_name)
        self.assertIsInstance(port_group_name, str)
        self.assertEqual(
            masking_view_details[constants.PORT_GROUP_ID], port_group_name)

    def test_get_element_from_masking_view_host(self):
        """Test get_element_from_masking_view host."""
        masking_view_name, masking_view_details = self.create_masking_view()
        host_name = self.provisioning.get_element_from_masking_view(
            masking_view_name, host=True)
        self.assertIsNotNone(host_name)
        self.assertIsInstance(host_name, str)
        self.assertEqual(masking_view_details[constants.HOST_ID], host_name)

    def test_get_element_from_masking_view_host_group(self):
        """Test get_element_from_masking_view host group."""
        masking_view_name, masking_view_details = self.create_masking_view(
            use_host_group=True)
        host_group_name = self.provisioning.get_element_from_masking_view(
            masking_view_name, host=True)
        self.assertIsNotNone(host_group_name)
        self.assertIsInstance(host_group_name, str)
        self.assertEqual(
            masking_view_details[constants.HOST_GROUP_ID], host_group_name)

    def test_get_element_from_masking_view_storage_group(self):
        """Test get_element_from_masking_view storage group."""
        masking_view_name, masking_view_details = self.create_masking_view()
        storage_group_name = self.provisioning.get_element_from_masking_view(
            masking_view_name, storagegroup=True)
        self.assertIsNotNone(storage_group_name)
        self.assertIsInstance(storage_group_name, str)
        self.assertEqual(
            masking_view_details[constants.STORAGE_GROUP_ID_CAMEL],
            storage_group_name)

    def test_get_port_group_common_masking_views(self):
        """Test get_port_group_common_masking_views."""
        masking_view_name, masking_view_details = self.create_masking_view()
        port_group_name = masking_view_details[constants.PORT_GROUP_ID]
        initiator_group_name = masking_view_details[constants.HOST_ID]
        common_masking_view_list = (
            self.provisioning.get_port_group_common_masking_views(
                port_group_name, initiator_group_name))
        self.assertIsNotNone(common_masking_view_list)
        self.assertIsInstance(common_masking_view_list, list)
        common_masking_view = common_masking_view_list[0]
        self.assertIsInstance(common_masking_view, str)
        self.assertEqual(masking_view_name, common_masking_view)

    def test_get_common_masking_views(self):
        """Test get_common_masking_views."""
        masking_view_name, masking_view_details = self.create_masking_view()
        port_group_name = masking_view_details[constants.PORT_GROUP_ID]
        initiator_group_name = masking_view_details[constants.HOST_ID]
        common_masking_view_list = self.provisioning.get_common_masking_views(
            port_group_name, initiator_group_name)
        self.assertIsNotNone(common_masking_view_list)
        self.assertIsInstance(common_masking_view_list, list)
        common_masking_view = common_masking_view_list[0]
        self.assertIsInstance(common_masking_view, str)
        self.assertEqual(masking_view_name, common_masking_view)

    def test_rename_masking_view(self):
        """Test rename_masking_view."""
        masking_view_name, _ = self.create_masking_view()
        new_name = self.generate_name('masking_view')
        masking_view_list = self.provisioning.get_masking_view_list()
        while new_name in masking_view_list:
            new_name = self.generate_name('masking_view')
        masking_view_details = self.provisioning.rename_masking_view(
            masking_view_name, new_name)
        self.addCleanup(self.delete_masking_view, new_name)
        masking_view_list = self.provisioning.get_masking_view_list()
        self.assertIn(new_name, masking_view_list)
        self.assertNotIn(masking_view_name, masking_view_list)
        new_id = masking_view_details[constants.MASKING_VIEW_ID]
        self.assertEqual(new_name, new_id)

    def test_get_host_from_masking_view(self):
        """Test get_host_from_masking_view."""
        masking_view_name, masking_view_details = self.create_masking_view()
        host = self.provisioning.get_host_from_masking_view(masking_view_name)
        self.assertIsNotNone(host)
        self.assertIsInstance(host, str)
        self.assertEqual(masking_view_details[constants.HOST_ID], host)

    def test_get_host_from_maskingview(self):
        """Test get_host_from_maskingview."""
        masking_view_name, masking_view_details = self.create_masking_view()
        host = self.provisioning.get_host_from_maskingview(masking_view_name)
        self.assertIsNotNone(host)
        self.assertIsInstance(host, str)
        self.assertEqual(masking_view_details[constants.HOST_ID], host)

    def test_get_storage_group_from_masking_view(self):
        """Test storage_group_from_masking_view."""
        masking_view_name, masking_view_details = self.create_masking_view()
        storage_group = self.provisioning.get_storage_group_from_masking_view(
            masking_view_name)
        self.assertIsNotNone(storage_group)
        self.assertIsInstance(storage_group, str)
        self.assertEqual(
            masking_view_details[constants.STORAGE_GROUP_ID_CAMEL],
            storage_group)

    def test_get_storagegroup_from_maskingview(self):
        """Test storagegroup_from_maskingview."""
        masking_view_name, masking_view_details = self.create_masking_view()
        storage_group = self.provisioning.get_storagegroup_from_maskingview(
            masking_view_name)
        self.assertIsNotNone(storage_group)
        self.assertIsInstance(storage_group, str)
        self.assertEqual(
            masking_view_details[constants.STORAGE_GROUP_ID_CAMEL],
            storage_group)

    def test_get_port_group_from_masking_view(self):
        """Test get_port_group_from_masking_view."""
        masking_view_name, masking_view_details = self.create_masking_view()
        if masking_view_name:
            port_group = self.provisioning.get_port_group_from_masking_view(
                masking_view_name)
            self.assertIsNotNone(port_group)
            self.assertIsInstance(port_group, str)
            self.assertEqual(
                masking_view_details[constants.PORT_GROUP_ID], port_group)

    def test_get_portgroup_from_maskingview(self):
        """Test get_portgroup_from_maskingview."""
        masking_view_name, masking_view_details = self.create_masking_view()
        if masking_view_name:
            port_group = self.provisioning.get_portgroup_from_maskingview(
                masking_view_name)
            self.assertIsNotNone(port_group)
            self.assertIsInstance(port_group, str)
            self.assertEqual(
                masking_view_details[constants.PORT_GROUP_ID], port_group)

    def test_get_masking_view_connections(self):
        """Test get_masking_view_connections."""
        _, active_connections = (
            self.provisioning.get_active_masking_view_connections())
        self.assertIsInstance(active_connections, list)
        for connection in active_connections:
            self._validiate_masking_view_connection(connection)

    def test_find_host_lun_id_for_volume(self):
        """Test find_host_lun_id_for_volume."""
        selected_masking_view, active_connections = (
            self.provisioning.get_active_masking_view_connections())
        for connection in active_connections:
            lun = self.provisioning.find_host_lun_id_for_volume(
                selected_masking_view, connection[constants.VOLUME_ID_CAMEL])
            if lun is not None:
                self.assertIsInstance(lun, int)
                self.assertEqual(
                    int(connection[constants.HOST_LUN_ADDRESS], 16), lun)
                break

    def test_find_host_lun_id_for_vol(self):
        """Test find_host_lun_id_for_vol."""
        selected_masking_view, active_connections = (
            self.provisioning.get_active_masking_view_connections())
        for connection in active_connections:
            lun = self.provisioning.find_host_lun_id_for_vol(
                selected_masking_view, connection[constants.VOLUME_ID_CAMEL])
            if lun is not None:
                self.assertIsInstance(lun, int)
                self.assertEqual(
                    int(connection[constants.HOST_LUN_ADDRESS], 16), lun)
                break

    def test_find_host_lun_id_for_volume_no_connections(self):
        """Test find_host_lun_id_for_volume no connections."""
        volume_details = self.create_volume()
        device_id = volume_details[constants.DEVICE_ID]
        masking_view_name, _ = self.create_masking_view()
        lun = self.provisioning.find_host_lun_id_for_vol(
            masking_view_name, device_id)
        self.assertIsNone(lun)

    def test_get_port_list(self):
        """Test get_port_list."""
        port_list = self.provisioning.get_port_list()
        self.assertIsNotNone(port_list)
        for port in port_list:
            self.assertIn(constants.DIRECTOR_ID, port)
            self.assertIn(constants.PORT_ID, port)
            director_id = port[constants.DIRECTOR_ID]
            port_id = port[constants.PORT_ID]
            self.assertIsInstance(director_id, str)
            self.assertIsInstance(port_id, str)
            self.assertIsNotNone(re.match(constants.DIRECTOR_SEARCH_PATTERN,
                                          director_id))
            self.assertIsNotNone(re.match(constants.PORT_SEARCH_PATTERN,
                                          port_id))

    def test_get_port_group(self):
        """Test get_port_group."""
        port_group_name, port_group_details = self.create_port_group()
        port_group_result = self.provisioning.get_port_group(port_group_name)
        director = port_group_details[
            constants.SYMMETRIX_PORT_KEY][0][constants.DIRECTOR_ID]
        port = port_group_details[
            constants.SYMMETRIX_PORT_KEY][0][constants.PORT_ID]
        formatted_director_port = self.provisioning.format_director_port(
            director, port)
        num_of_ports = port_group_details[constants.NUM_OF_PORTS]
        num_of_masking_views = port_group_details[
            constants.NUM_OF_MASKING_VIEWS]
        ref_type = port_group_details[constants.TYPE]
        self._validate_port_group_details(
            port_group_name, port_group_result, [formatted_director_port],
            num_of_ports, num_of_masking_views, ref_type)

    def test_get_portgroup(self):
        """Test get_portgroup."""
        port_group_name, port_group_details = self.create_port_group()
        port_group_result = self.provisioning.get_portgroup(port_group_name)
        director = port_group_details[
            constants.SYMMETRIX_PORT_KEY][0][constants.DIRECTOR_ID]
        port = port_group_details[
            constants.SYMMETRIX_PORT_KEY][0][constants.PORT_ID]
        formatted_director_port = self.provisioning.format_director_port(
            director, port)
        num_of_ports = port_group_details[constants.NUM_OF_PORTS]
        num_of_masking_views = port_group_details[
            constants.NUM_OF_MASKING_VIEWS]
        ref_type = port_group_details[constants.TYPE]
        self._validate_port_group_details(
            port_group_name, port_group_result, [formatted_director_port],
            num_of_ports, num_of_masking_views, ref_type)

    def test_get_port_group_list(self):
        """Test get_port_group_list."""
        port_group_list = self.provisioning.get_port_group_list()
        self.assertIsNotNone(port_group_list)
        self.assertIsInstance(port_group_list, list)
        for port_group in port_group_list:
            self.assertIsInstance(port_group, str)

    def test_get_portgroup_list(self):
        """Test get_portgroup_list."""
        port_group_list = self.provisioning.get_portgroup_list()
        self.assertIsNotNone(port_group_list)
        self.assertIsInstance(port_group_list, list)
        for port_group in port_group_list:
            self.assertIsInstance(port_group, str)

    def test_get_ports_from_port_group(self):
        """Test get_ports_from_port_group."""
        port_group_name, port_group_details = self.create_port_group()
        port_list = self.provisioning.get_ports_from_port_group(
            port_group_name)
        self.assertIsNotNone(port_list)
        self.assertIsInstance(port_list, list)
        reference_port = port_group_details[
            constants.SYMMETRIX_PORT_KEY][0][constants.PORT_ID]
        result_port = port_list[0]
        self.assertEqual(reference_port, result_port)
        self.assertIsNotNone(
            re.match(constants.PORT_SEARCH_PATTERN, result_port))

    def test_get_ports_from_pg(self):
        """Test get_ports_from_pg."""
        port_group_name, port_group_details = self.create_port_group()
        port_list = self.provisioning.get_ports_from_pg(port_group_name)
        self.assertIsNotNone(port_list)
        self.assertIsInstance(port_list, list)
        reference_port = port_group_details[
            constants.SYMMETRIX_PORT_KEY][0][constants.PORT_ID]
        result_port = port_list[0]
        self.assertEqual(reference_port, result_port)
        self.assertIsNotNone(
            re.match(constants.PORT_SEARCH_PATTERN, result_port))

    def test_get_target_wwns_from_port_group(self):
        """Test get_target_wwns_from_port_group."""
        port_group_name, port_group_details = self.create_port_group()
        target_wwns = self.provisioning.get_target_wwns_from_port_group(
            port_group_name)
        self.assertIsNotNone(target_wwns)
        self.assertIsInstance(target_wwns, list)
        for wwn in target_wwns:
            self.assertIsInstance(wwn, str)
            self.assertIsNotNone(
                re.match(constants.WWN_SEARCH_PATTERN_16, wwn))

    def test_get_target_wwns_from_pg(self):
        """Test get_target_wwns_from_pg."""
        port_group_name, port_group_details = self.create_port_group()
        target_wwns = self.provisioning.get_target_wwns_from_pg(
            port_group_name)
        self.assertIsNotNone(target_wwns)
        self.assertIsInstance(target_wwns, list)
        for wwn in target_wwns:
            self.assertIsInstance(wwn, str)
            self.assertIsNotNone(
                re.match(constants.WWN_SEARCH_PATTERN_16, wwn))

    def test_get_iscsi_ip_address_and_iqn(self):
        """Test get_iscsi_ip_address_and_iqn."""
        port_list = self.provisioning.get_port_list()
        se_director_ports = [p for p in port_list if 'SE-' in p[
            constants.DIRECTOR_ID]]
        for se_director_port in se_director_ports:
            director_id = se_director_port[constants.DIRECTOR_ID]
            port_id = se_director_port[constants.PORT_ID]
            iscsi_id = self.provisioning.format_director_port(
                director_id, port_id)
            ip_addresses, iqn = (
                self.provisioning.get_iscsi_ip_address_and_iqn(iscsi_id))
            if ip_addresses:
                self.assertIsInstance(ip_addresses, list)
                for ip in ip_addresses:
                    valid_ip = (
                        self.common.check_ipv4(
                            ip) or self.common.check_ipv6(ip))
                    self.assertIsInstance(ip, str)
                    self.assertTrue(valid_ip)
            if iqn:
                self.assertIsInstance(iqn, str)

    def test_create_port_group(self):
        """Test create_port_group."""
        directors = self.conn.provisioning.get_director_list()
        port_group_name = self.generate_name(constants.PORT_GROUP)
        director = None
        port = None
        for d in directors:
            if 'FA-' in d:
                director = d
                port = self.conn.provisioning.get_director_port_list(
                    director)[0][constants.PORT_ID]
                break
        formatted_director_port = self.provisioning.format_director_port(
            director, port)
        port_group_details = self.conn.provisioning.create_port_group(
            port_group_name, director, port)
        self.addCleanup(self.delete_port_group, port_group_name)
        self._validate_port_group_details(
            port_group_name, port_group_details, [formatted_director_port])

    def test_create_portgroup(self):
        """Test create_portgroup."""
        directors = self.conn.provisioning.get_director_list()
        port_group_name = self.generate_name(constants.PORT_GROUP)
        director = None
        port = None
        for d in directors:
            if 'FA-' in d:
                director = d
                port = self.conn.provisioning.get_director_port_list(
                    director)[0][constants.PORT_ID]
                break
        formatted_director_port = self.provisioning.format_director_port(
            director, port)
        port_group_details = self.conn.provisioning.create_portgroup(
            port_group_name, director, port)
        self.addCleanup(self.delete_port_group, port_group_name)
        self._validate_port_group_details(
            port_group_name, port_group_details, [formatted_director_port])

    def test_create_multiport_port_group(self):
        """Test create_multiport_port_group."""
        port_group_name = self.generate_name(constants.PORT_GROUP)
        fa_directors = self.provisioning.get_fa_directors()
        selected_director_ports = list()
        for director in fa_directors:
            if len(selected_director_ports) < 2:
                ports = self.provisioning.get_director_port_list(
                    director, filters='aclx=true')
                # avoid GOS ports
                ports = [p for p in ports if int(p[constants.PORT_ID]) < 30]
                selected_director_ports.append(ports[0])
        reference_director_ports = list()
        for director_port in selected_director_ports:
            director_id = director_port[constants.DIRECTOR_ID]
            port_id = director_port[constants.PORT_ID]
            formatted_director_port = self.provisioning.format_director_port(
                director_id, port_id)
            reference_director_ports.append(formatted_director_port)
        port_group_details = self.provisioning.create_multiport_port_group(
            port_group_name, selected_director_ports)
        self.addCleanup(self.delete_port_group, port_group_name)
        self._validate_port_group_details(
            port_group_name, port_group_details, reference_director_ports,
            2)

    def test_create_multiport_portgroup(self):
        """Test create_multiport_portgroup."""
        port_group_name = self.generate_name(constants.PORT_GROUP)
        fa_directors = self.provisioning.get_fa_directors()
        selected_director_ports = list()
        for director in fa_directors:
            if len(selected_director_ports) < 2:
                ports = self.provisioning.get_director_port_list(
                    director, filters='aclx=true')
                # avoid GOS ports
                ports = [p for p in ports if int(p[constants.PORT_ID]) < 30]
                selected_director_ports.append(ports[0])
        reference_director_ports = list()
        for director_port in selected_director_ports:
            director_id = director_port[constants.DIRECTOR_ID]
            port_id = director_port[constants.PORT_ID]
            formatted_director_port = self.provisioning.format_director_port(
                director_id, port_id)
            reference_director_ports.append(formatted_director_port)
        port_group_details = self.provisioning.create_multiport_portgroup(
            port_group_name, selected_director_ports)
        self.addCleanup(self.delete_port_group, port_group_name)
        self._validate_port_group_details(
            port_group_name, port_group_details, reference_director_ports,
            2)

    def test_create_port_group_from_file(self):
        """Test create_port_group_from_file."""
        fa_directors = self.provisioning.get_fa_directors()
        if fa_directors:
            port_group_name = self.generate_name()
            director = fa_directors[0]
            port = self.provisioning.get_any_director_port(
                director, filters='aclx=true')
            formatted_director_port = self.provisioning.format_director_port(
                director, port)
            csv_file_name = 'test.csv'
            temp_dir = self.create_temp_directory()
            csv_file_path = os.path.join(temp_dir, csv_file_name)
            with open(csv_file_path, 'w') as tmp:
                tmp.write(formatted_director_port)
            port_group_details = (
                self.provisioning.create_port_group_from_file(
                    csv_file_path, port_group_name))
            self.addCleanup(self.delete_port_group, port_group_name)
            self._validate_port_group_details(
                port_group_name, port_group_details,
                [formatted_director_port])

    def test_create_portgroup_from_file(self):
        """Test create_portgroup_from_file."""
        fa_directors = self.provisioning.get_fa_directors()
        if fa_directors:
            port_group_name = self.generate_name()
            director = fa_directors[0]
            port = self.provisioning.get_any_director_port(
                director, filters='aclx=true')
            formatted_director_port = self.provisioning.format_director_port(
                director, port)
            csv_file_name = 'test.csv'
            temp_dir = self.create_temp_directory()
            csv_file_path = os.path.join(temp_dir, csv_file_name)
            with open(csv_file_path, 'w') as tmp:
                tmp.write(formatted_director_port)
            port_group_details = (
                self.provisioning.create_portgroup_from_file(
                    csv_file_path, port_group_name))
            self.addCleanup(self.delete_port_group, port_group_name)
            self._validate_port_group_details(
                port_group_name, port_group_details,
                [formatted_director_port])

    def test_modify_port_group_remove_port(self):
        """Test modify_port_group remove port."""
        port_group_name, port_group_details = self.create_port_group(
            number_of_ports=2)
        director_port_list = port_group_details[constants.SYMMETRIX_PORT_KEY]
        self.assertEqual(2, port_group_details[constants.NUM_OF_PORTS])
        self.assertEqual(2, len(director_port_list))
        remove_director = director_port_list[0][constants.DIRECTOR_ID]
        remove_port = director_port_list[0][constants.PORT_ID]
        remaining_director = director_port_list[1][constants.DIRECTOR_ID]
        remaining_port = director_port_list[1][constants.PORT_ID]
        remaining_director_port = self.provisioning.format_director_port(
            remaining_director, remaining_port)
        modify_port_result = self.provisioning.modify_port_group(
            port_group_name, remove_port=(remove_director, remove_port))
        self._validate_port_group_details(
            port_group_name, modify_port_result, [remaining_director_port],
            ref_port_count=1)
        port_group_details = self.provisioning.get_port_group(port_group_name)
        self._validate_port_group_details(
            port_group_name, port_group_details, [remaining_director_port],
            ref_port_count=1)

    def test_modify_port_group_add_port(self):
        """Test modify_port_group add port."""
        fa_directors = self.provisioning.get_fa_directors()
        selected_director_ports = list()
        for fa_director in fa_directors:
            port = self.provisioning.get_any_director_port(
                fa_director, filters='aclx=true')
            director_port = self.provisioning.format_director_port(
                fa_director, port)
            selected_director_ports.append(director_port)
        port_group_name = self.generate_name(constants.PORT_GROUP)
        director, port = selected_director_ports[0].split(':')
        port_group_details = self.provisioning.create_port_group(
            port_group_name, director, port)
        self.addCleanup(self.delete_port_group, port_group_name)
        self.assertEqual(1, port_group_details[constants.NUM_OF_PORTS])
        director, port = selected_director_ports[1].split(':')
        modify_result = self.provisioning.modify_port_group(
            port_group_name, add_port=(director, port))
        self._validate_port_group_details(
            port_group_name, modify_result, selected_director_ports[:2],
            ref_port_count=2)

    def test_modify_port_group_rename_port_group(self):
        """Test modify_port_group rename."""
        port_group_name, _ = self.create_port_group()
        new_name = self.generate_name(constants.PORT_GROUP)
        port_group_list = self.provisioning.get_port_group_list()
        while new_name in port_group_list:
            new_name = self.generate_name(constants.PORT_GROUP)
            port_group_list = self.provisioning.get_port_group_list()
        modify_result = self.provisioning.modify_port_group(
            port_group_name, rename_port_group=new_name)
        self.addCleanup(self.delete_port_group, new_name)
        port_group_list = self.provisioning.get_port_group_list()
        self.assertIn(new_name, port_group_list)
        self._validate_port_group_details(new_name, modify_result)

    def test_modify_port_group_exception(self):
        """Test modify_port_group exception."""
        port_group_name = self.generate_name(constants.PORT_GROUP)
        self.assertRaises(exception.InvalidInputException,
                          self.provisioning.modify_port_group,
                          port_group_name)

    def test_modify_portgroup_rename_port_group(self):
        """Test modify_portgroup rename."""
        port_group_name, _ = self.create_port_group()
        new_name = self.generate_name(constants.PORT_GROUP)
        port_group_list = self.provisioning.get_port_group_list()
        while new_name in port_group_list:
            new_name = self.generate_name(constants.PORT_GROUP)
            port_group_list = self.provisioning.get_port_group_list()
        modify_result = self.provisioning.modify_portgroup(
            port_group_name, rename_portgroup=new_name)
        self.addCleanup(self.delete_port_group, new_name)
        port_group_list = self.provisioning.get_port_group_list()
        self.assertIn(new_name, port_group_list)
        self._validate_port_group_details(new_name, modify_result)

    def test_delete_port_group(self):
        """Test delete_port_group."""
        port_group_name, _ = self.create_port_group()
        port_group_list = self.provisioning.get_port_group_list()
        self.assertIn(port_group_name, port_group_list)
        self.provisioning.delete_port_group(port_group_name)
        port_group_list = self.provisioning.get_port_group_list()
        self.assertNotIn(port_group_name, port_group_list)

    def test_delete_portgroup(self):
        """Test delete_portgroup."""
        port_group_name, _ = self.create_port_group()
        port_group_list = self.provisioning.get_port_group_list()
        self.assertIn(port_group_name, port_group_list)
        self.provisioning.delete_portgroup(port_group_name)
        port_group_list = self.provisioning.get_port_group_list()
        self.assertNotIn(port_group_name, port_group_list)

    def test_get_slo_list(self):
        """Test get_slo_list."""
        service_level_list = self.provisioning.get_slo_list()
        valid_service_level_list = ['Bronze', 'Silver', 'Gold',
                                    'Platinum', 'Diamond', 'Optimized']
        self.assertIsNotNone(service_level_list)
        for service_level in service_level_list:
            self.assertIsInstance(service_level, str)
            self.assertIn(service_level, valid_service_level_list)

    def test_get_service_level_list(self):
        """Test get_service_level_list."""
        service_level_list = self.provisioning.get_service_level_list()
        valid_service_level_list = ['Bronze', 'Silver', 'Gold',
                                    'Platinum', 'Diamond', 'Optimized']
        self.assertIsNotNone(service_level_list)
        for service_level in service_level_list:
            self.assertIsInstance(service_level, str)
            self.assertIn(service_level, valid_service_level_list)

    def test_get_service_level(self):
        """Test get_service_level."""
        service_level_list = self.provisioning.get_service_level_list()
        for service_level in service_level_list:
            service_level_details = self.provisioning.get_service_level(
                service_level)
            self._validate_service_level_details(
                service_level, service_level_details)

    def test_get_slo(self):
        """Test get_slo."""
        service_level_list = self.provisioning.get_service_level_list()
        for service_level in service_level_list:
            service_level_details = self.provisioning.get_slo(service_level)
            self._validate_service_level_details(
                service_level, service_level_details)

    def test_modify_service_level(self):
        """Test modify_service_level."""
        service_level_list = self.provisioning.get_service_level_list()
        service_level = service_level_list[0]
        service_level_details = self.provisioning.get_service_level(
            service_level)
        old_name = service_level_details[constants.SLO_ID]
        new_name = self.generate_name(constants.SERVICE_LEVEL)
        self.provisioning.modify_service_level(service_level, new_name)
        service_level_list = self.provisioning.get_service_level_list()
        self.assertIn(new_name, service_level_list)
        self.assertNotIn(old_name, service_level_list)
        service_level_details = self.provisioning.get_service_level(
            new_name)
        self._validate_service_level_details(new_name, service_level_details)
        self.provisioning.modify_service_level(new_name, old_name)

    def test_modify_slo(self):
        """Test modify_slo."""
        service_level_list = self.provisioning.get_service_level_list()
        service_level = service_level_list[0]
        service_level_details = self.provisioning.get_service_level(
            service_level)
        old_name = service_level_details[constants.SLO_ID]
        new_name = self.generate_name(constants.SERVICE_LEVEL)
        self.provisioning.modify_slo(service_level, new_name)
        service_level_list = self.provisioning.get_service_level_list()
        self.assertIn(new_name, service_level_list)
        self.assertNotIn(old_name, service_level_list)
        service_level_details = self.provisioning.get_service_level(
            new_name)
        self._validate_service_level_details(new_name, service_level_details)
        self.provisioning.modify_slo(new_name, old_name)

    def test_get_srp(self):
        """Test get_srp."""
        srp_list = self.provisioning.get_srp_list()
        for srp in srp_list:
            srp_details = self.provisioning.get_srp(srp)
            self._validate_srp_details(srp_details)

    def test_get_srp_list(self):
        """Test get_srp_list."""
        srp_list = self.provisioning.get_srp_list()
        self.assertIsNotNone(srp_list)
        self.assertIsInstance(srp_list, list)
        for srp in srp_list:
            self.assertIsInstance(srp, str)

    def test_get_compressibility_report(self):
        """Test get_compressibility_report."""
        srp_list = self.provisioning.get_srp_list()
        if not srp_list:
            self.skipTest(
                'test_get_compressibility_report - Could not find any SRPs.')
        populated_report = None
        for srp in srp_list:
            report = self.provisioning.get_compressibility_report(srp)
            self.assertIsInstance(report, list)
            if report:
                populated_report = report
        num_of_volumes = 'num_of_volumes'
        allocated_cap_gb = 'allocated_cap_gb'
        used_cap_gb = 'used_cap_gb'
        compression_enabled = 'compression_enabled'
        target_ratio_to_one = 'target_ratio_to_one'
        for storage_group_detail in populated_report:
            self.assertIn(
                constants.STORAGE_GROUP_ID_CAMEL, storage_group_detail)
            self.assertIn(num_of_volumes, storage_group_detail)
            self.assertIn(allocated_cap_gb, storage_group_detail)
            self.assertIn(used_cap_gb, storage_group_detail)
            self.assertIn(compression_enabled, storage_group_detail)
            self.assertIs(
                str, type(
                    storage_group_detail[constants.STORAGE_GROUP_ID_CAMEL]))
            self.assertIs(
                int, type(storage_group_detail[num_of_volumes]))
            self.assertIs(
                float, type(storage_group_detail[allocated_cap_gb]))
            self.assertIs(
                float, type(storage_group_detail[used_cap_gb]))
            self.assertIs(
                bool, type(storage_group_detail[compression_enabled]))
            if target_ratio_to_one in storage_group_detail:
                self.assertIs(
                    float,
                    type(storage_group_detail[target_ratio_to_one]))

    def test_is_compression_capable(self):
        """Test is_compression_capable."""
        result = self.provisioning.is_compression_capable()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)

    def test_get_storage_group(self):
        """Test get_storage_group."""
        storage_group_name = self.create_empty_storage_group()
        ref_storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)
        self.assertEqual(storage_group_name,
                         storage_group_details[
                             constants.STORAGE_GROUP_ID_CAMEL])
        self.assertEqual(
            ref_storage_group_details[constants.SLO],
            storage_group_details[constants.SLO])
        self.assertEqual(
            ref_storage_group_details[constants.SERVICE_LEVEL],
            storage_group_details[constants.SERVICE_LEVEL])
        self.assertEqual(
            ref_storage_group_details[constants.BASE_SLO_NAME],
            storage_group_details[constants.BASE_SLO_NAME])
        self.assertEqual(
            ref_storage_group_details[constants.SRP],
            storage_group_details[constants.SRP])
        self.assertEqual(
            ref_storage_group_details[constants.SLO_COMPLIANCE],
            storage_group_details[constants.SLO_COMPLIANCE])
        self.assertEqual(
            ref_storage_group_details[constants.NUM_OF_VOLS],
            storage_group_details[constants.NUM_OF_VOLS])
        self.assertEqual(
            ref_storage_group_details[constants.NUM_OF_CHILD_SGS],
            storage_group_details[constants.NUM_OF_CHILD_SGS])
        self.assertEqual(
            ref_storage_group_details[constants.NUM_OF_PARENT_SGS],
            storage_group_details[constants.NUM_OF_PARENT_SGS])
        self.assertEqual(
            ref_storage_group_details[constants.NUM_OF_MASKING_VIEWS],
            storage_group_details[constants.NUM_OF_MASKING_VIEWS])
        self.assertEqual(
            ref_storage_group_details[constants.NUM_OF_SNAPSHOTS],
            storage_group_details[constants.NUM_OF_SNAPSHOTS])
        self.assertEqual(
            ref_storage_group_details[constants.CAP_GB],
            storage_group_details[constants.CAP_GB])
        self.assertEqual(
            ref_storage_group_details[constants.DEVICE_EMULATION],
            storage_group_details[constants.DEVICE_EMULATION])
        self.assertEqual(
            ref_storage_group_details[constants.TYPE],
            storage_group_details[constants.TYPE])
        self.assertEqual(
            ref_storage_group_details[constants.UNPROTECTED],
            storage_group_details[constants.UNPROTECTED])
        self.assertEqual(
            ref_storage_group_details[constants.COMPRESSION],
            storage_group_details[constants.COMPRESSION])

    def test_get_storage_group_demand_report(self):
        """Test get_storage_group_demand_report."""
        srp_list = self.provisioning.get_srp_list()
        srp_report = None
        for srp in srp_list:
            report = self.provisioning.get_storage_group_demand_report(
                srp)
            if report:
                srp_report = report
            else:
                self.assertIsInstance(report, dict)
                self.assertIn(constants.STORAGE_GROUP_DEMAND, report)
                self.assertIsInstance(
                    report[constants.STORAGE_GROUP_DEMAND], list)
                self.assertIsNone(report[constants.STORAGE_GROUP_DEMAND])
        if srp_report:
            self._validate_srp_demand_report(srp_report)

    def test_get_storage_group_demand_report_no_srp(self):
        """Test get_storage_group_demand_report."""
        report = self.provisioning.get_storage_group_demand_report()
        if not report:
            self.assertIsInstance(report, dict)
            self.assertIn(constants.STORAGE_GROUP_DEMAND, report)
            self.assertIsInstance(
                report[constants.STORAGE_GROUP_DEMAND], list)
            self.assertIsNone(report[constants.STORAGE_GROUP_DEMAND])
        else:
            self._validate_srp_demand_report(report)

    def test_get_storage_group_list(self):
        """Test get_storage_group_list."""
        storage_group_list = self.provisioning.get_storage_group_list()
        self.assertIsNotNone(storage_group_list)
        self.assertIsInstance(storage_group_list, list)
        for storage_group in storage_group_list:
            self.assertIsNotNone(storage_group)
            self.assertIsInstance(storage_group, str)

    def test_get_masking_view_from_storage_group(self):
        """Test get_masking_view_from_storage_group."""
        ref_masking_view_name, ref_masking_view_details = (
            self.create_masking_view())
        storage_group = ref_masking_view_details[
            constants.STORAGE_GROUP_ID_CAMEL]
        masking_view_list = (
            self.provisioning.get_masking_view_from_storage_group(
                storage_group))
        self.assertIsInstance(masking_view_list, list)
        self.assertIsNotNone(masking_view_list)
        self.assertEqual(ref_masking_view_name, masking_view_list[0])

    def test_get_mv_from_sg(self):
        """Test get_mv_from_sg."""
        ref_masking_view_name, ref_masking_view_details = (
            self.create_masking_view())
        storage_group = ref_masking_view_details[
            constants.STORAGE_GROUP_ID_CAMEL]
        masking_view_list = self.provisioning.get_mv_from_sg(storage_group)
        self.assertIsInstance(masking_view_list, list)
        self.assertIsNotNone(masking_view_list)
        self.assertEqual(ref_masking_view_name, masking_view_list[0])

    def test_get_num_vols_in_storage_group(self):
        """Test get_num_vols_in_storage_group."""
        storage_group_name = self.create_empty_storage_group()
        volume_count = self.provisioning.get_num_vols_in_storage_group(
            storage_group_name)
        self.assertIsInstance(volume_count, int)
        self.assertEqual(0, volume_count)
        volume_name = self.generate_name()
        device_id = (
            self.conn.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, '1', cap_unit='GB'))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        volume_count = self.provisioning.get_num_vols_in_storage_group(
            storage_group_name)
        self.assertIsInstance(volume_count, int)
        self.assertEqual(1, volume_count)

    def test_get_num_vols_in_sg(self):
        """Test get_num_vols_in_sg."""
        storage_group_name = self.create_empty_storage_group()
        volume_count = self.provisioning.get_num_vols_in_sg(
            storage_group_name)
        self.assertIsInstance(volume_count, int)
        self.assertEqual(0, volume_count)
        volume_name = self.generate_name()
        device_id = (
            self.conn.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, '1', cap_unit='GB'))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        volume_count = self.provisioning.get_num_vols_in_sg(
            storage_group_name)
        self.assertIsInstance(volume_count, int)
        self.assertEqual(1, volume_count)

    def test_is_child_storage_group_in_parent_storage_group(self):
        """Test is_child_storage_group_in_parent_storage_group."""
        parent_storage_group = self.create_empty_storage_group()
        child_storage_group = self.create_empty_storage_group()
        result = (
            self.provisioning.is_child_storage_group_in_parent_storage_group(
                child_storage_group, parent_storage_group))
        self.assertIsInstance(result, bool)
        self.assertFalse(result)
        self.provisioning.add_child_storage_group_to_parent_group(
            child_storage_group, parent_storage_group)
        result = (
            self.provisioning.is_child_storage_group_in_parent_storage_group(
                child_storage_group, parent_storage_group))
        # Remove to aid cleanup
        self.provisioning.remove_child_storage_group_from_parent_group(
            child_storage_group, parent_storage_group)
        # Auto-generated child storage-groups appear, clean it
        storage_group_list = self.provisioning.get_storage_group_list()
        auto_created_child = '{psg}_1'.format(psg=parent_storage_group)
        if auto_created_child in storage_group_list:
            self.provisioning.remove_child_storage_group_from_parent_group(
                auto_created_child, parent_storage_group)
            self.addCleanup(self.delete_storage_group, auto_created_child)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_is_child_sg_in_parent_sg(self):
        """Test is_child_sg_in_parent_sg."""
        parent_storage_group = self.create_empty_storage_group()
        child_storage_group = self.create_empty_storage_group()
        result = self.provisioning.is_child_sg_in_parent_sg(
            child_storage_group, parent_storage_group)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)
        self.provisioning.add_child_storage_group_to_parent_group(
            child_storage_group, parent_storage_group)
        result = self.provisioning.is_child_sg_in_parent_sg(
            child_storage_group, parent_storage_group)
        # Remove to aid cleanup
        self.provisioning.remove_child_storage_group_from_parent_group(
            child_storage_group, parent_storage_group)
        # Auto-generated child storage-groups appear, clean it
        storage_group_list = self.provisioning.get_storage_group_list()
        auto_created_child = '{psg}_1'.format(psg=parent_storage_group)
        if auto_created_child in storage_group_list:
            self.provisioning.remove_child_storage_group_from_parent_group(
                auto_created_child, parent_storage_group)
            self.addCleanup(self.delete_storage_group, auto_created_child)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_is_child_sg_in_parent_sg_legacy_add_remove(self):
        """Test is_child_sg_in_parent_sg legacy add/remove."""
        parent_storage_group = self.create_empty_storage_group()
        child_storage_group = self.create_empty_storage_group()
        result = self.provisioning.is_child_sg_in_parent_sg(
            child_storage_group, parent_storage_group)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)
        self.provisioning.add_child_sg_to_parent_sg(
            child_storage_group, parent_storage_group)
        result = self.provisioning.is_child_sg_in_parent_sg(
            child_storage_group, parent_storage_group)
        # Remove to aid cleanup
        self.provisioning.remove_child_sg_from_parent_sg(
            child_storage_group, parent_storage_group)
        # Auto-generated child storage-groups appear, clean it
        storage_group_list = self.provisioning.get_storage_group_list()
        auto_created_child = '{psg}_1'.format(psg=parent_storage_group)
        if auto_created_child in storage_group_list:
            self.provisioning.remove_child_sg_from_parent_sg(
                auto_created_child, parent_storage_group)
            self.addCleanup(self.delete_storage_group, auto_created_child)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_get_child_storage_groups_from_parent(self):
        """Test get_child_storage_groups_from_parent."""
        parent_storage_group_name = self.create_empty_storage_group()
        child_storage_group_name = self.create_empty_storage_group()
        self.provisioning.add_child_storage_group_to_parent_group(
            child_storage_group_name, parent_storage_group_name)
        child_list = self.provisioning.get_child_storage_groups_from_parent(
            parent_storage_group_name)
        self.assertIsInstance(child_list, list)
        self.assertIsNot(0, len(child_list))
        self.assertIn(child_storage_group_name, child_list)
        for child in child_list:
            self.provisioning.remove_child_storage_group_from_parent_group(
                child, parent_storage_group_name)
            self.provisioning.delete_storage_group(child)

    def test_get_child_sg_from_parent(self):
        """Test get_child_sg_from_parent."""
        parent_storage_group_name = self.create_empty_storage_group()
        child_storage_group_name = self.create_empty_storage_group()
        self.provisioning.add_child_storage_group_to_parent_group(
            child_storage_group_name, parent_storage_group_name)
        child_list = self.provisioning.get_child_sg_from_parent(
            parent_storage_group_name)
        self.assertIsInstance(child_list, list)
        self.assertIsNot(0, len(child_list))
        self.assertIn(child_storage_group_name, child_list)
        for child in child_list:
            self.provisioning.remove_child_storage_group_from_parent_group(
                child, parent_storage_group_name)
            self.provisioning.delete_storage_group(child)

    def test_create_storage_group_async(self):
        """Test create_storage_group async."""
        storage_group_name = self.generate_name('sg')
        volume_name = self.generate_name()
        job = self.provisioning.create_storage_group(
            self.SRP, storage_group_name, self.SLO, _async=True,
            vol_name=volume_name)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self.conn.common.wait_for_job_complete(job)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)

    def test_create_storage_group_disable_compression_allocate_full(self):
        """Test create_storage_group disable compression allocate full."""
        storage_group_name = self.generate_name('sg')
        storage_group_details = self.provisioning.create_storage_group(
            self.SRP, storage_group_name, self.SLO,
            do_disable_compression=True, allocate_full=True)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)

    def test_create_storage_group_mobility_id(self):
        """Test create_storage_group with mobility ID enabled."""
        storage_group_name = self.generate_name('sg')
        self.provisioning.create_storage_group(
            self.SRP, storage_group_name, self.SLO,
            enable_mobility_id=True, num_vols=1, cap_unit='GB', vol_size=1)
        storage_group_volumes = (
            self.provisioning.get_volumes_from_storage_group(
                storage_group_name))
        vol_details = self.provisioning.get_volume(storage_group_volumes[0])
        self.addCleanup(self.delete_storage_group, storage_group_name)
        for volume in storage_group_volumes:
            self.addCleanup(self.delete_volume, storage_group_name, volume)
        self.assertTrue(vol_details.get('mobility_id_enabled'))

    def test_create_storage_group_return_id_mobility_enabled(self):
        """Test create_storage_group_return_id with mobility_enabled."""
        storage_group_name = self.create_empty_storage_group()
        volume_name = self.generate_name()
        device = (
            self.conn.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, 1, enable_mobility_id=True))
        device_details = self.provisioning.get_volume(device)
        self.assertTrue(device_details.get('mobility_id_enabled'))
        self.addCleanup(self.delete_storage_group, storage_group_name)

    def test_create_storage_group_mobility_id_disabled(self):
        """Test test_create_storage_group mobility_id disabled."""
        storage_group_name = self.generate_name('sg')
        self.provisioning.create_storage_group(
            self.SRP, storage_group_name, self.SLO,
            enable_mobility_id=False, num_vols=1, cap_unit='GB', vol_size=1)
        storage_group_volumes = (
            self.provisioning.get_volumes_from_storage_group(
                storage_group_name))
        vol_details = self.provisioning.get_volume(storage_group_volumes[0])
        self.addCleanup(self.delete_storage_group, storage_group_name)
        for volume in storage_group_volumes:
            self.addCleanup(self.delete_volume, storage_group_name, volume)
        self.assertFalse(vol_details.get('mobility_id_enabled'))

    def test_create_non_empty_storage_group(self):
        """Test create_non_empty_storage_group."""
        storage_group_name = self.generate_name('sg')
        result = self.provisioning.create_non_empty_storage_group(
            self.SRP, storage_group_name, self.SLO, None, 1, '1', 'GB')
        time.sleep(10)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self._validate_storage_group_details(storage_group_name, result)
        volumes = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        self.assertEqual(1, len(volumes))
        for volume in volumes:
            self.addCleanup(self.delete_volume, storage_group_name, volume)

    def test_create_non_empty_storagegroup(self):
        """Test create_non_empty_storagegroup."""
        storage_group_name = self.generate_name('sg')
        result = self.provisioning.create_non_empty_storagegroup(
            self.SRP, storage_group_name, self.SLO, None, 1, '1', 'GB')
        time.sleep(10)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self._validate_storage_group_details(storage_group_name, result)
        volumes = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        self.assertEqual(1, len(volumes))
        for volume in volumes:
            self.addCleanup(self.delete_volume, storage_group_name, volume)

    def test_create_no_slo_storage_group_with_volumes(self):
        """Test create_empty_storage_group with no service level and vols."""
        storage_group_name = self.generate_name('sg')
        storage_group_details = self.provisioning.create_storage_group(
            self.SRP, storage_group_name, slo=None, workload=None,
            num_vols=3, vol_size=1)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        volume_count = storage_group_details[constants.NUM_OF_VOLS]
        self.assertEqual(3, volume_count)
        self.assertEqual('NONE', storage_group_details[constants.SLO])
        self.assertTrue(storage_group_details[constants.COMPRESSION])

    def test_create_empty_storage_group(self):
        """Test create_empty_storage_group."""
        storage_group_name = self.generate_name('sg')
        storage_group_details = self.provisioning.create_empty_storage_group(
            self.SRP, storage_group_name, self.SLO, None)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)
        volume_count = storage_group_details[constants.NUM_OF_VOLS]
        self.assertEqual(0, volume_count)

    def test_create_empty_sg(self):
        """Test create_empty_sg."""
        storage_group_name = self.generate_name('sg')
        storage_group_details = self.provisioning.create_empty_sg(
            self.SRP, storage_group_name, self.SLO, None)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)
        volume_count = storage_group_details[constants.NUM_OF_VOLS]
        self.assertEqual(0, volume_count)

    def test_remove_child_storage_group_from_parent_group(self):
        """Test remove_child_storage_group_from_parent_group."""
        parent_storage_group_name = self.create_empty_storage_group()
        child_storage_group_name = self.create_empty_storage_group()
        self.provisioning.add_child_storage_group_to_parent_group(
            child_storage_group_name, parent_storage_group_name)
        parent_storage_group_details = self.provisioning.get_storage_group(
            parent_storage_group_name)
        child_storage_group = 'child_storage_group'
        self.assertIn(child_storage_group, parent_storage_group_details)
        child_list = parent_storage_group_details[child_storage_group]
        self.assertIn(child_storage_group_name, child_list)
        for child in child_list:
            self.provisioning.remove_child_storage_group_from_parent_group(
                child, parent_storage_group_name)
            self.provisioning.delete_storage_group(child)
        parent_storage_group_details = self.provisioning.get_storage_group(
            parent_storage_group_name)
        self.assertNotIn(child_storage_group, parent_storage_group_details)
        self.assertIs(
            0, parent_storage_group_details[constants.NUM_OF_CHILD_SGS])

    def test_add_existing_volume_to_storage_group(self):
        """Test add_existing_volume_to_storage_group."""
        volume_name = self.generate_name()
        storage_group_name = self.create_empty_storage_group()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, '1'))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        self.provisioning.remove_volume_from_storage_group(
            storage_group_name, device_id)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(0, storage_group_details[constants.NUM_OF_VOLS])
        self.provisioning.add_existing_volume_to_storage_group(
            storage_group_name, device_id)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(1, storage_group_details[constants.NUM_OF_VOLS])
        volume_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        self.assertIn(device_id, volume_list)

    def test_add_existing_vol_to_sg(self):
        """Test add_existing_vol_to_sg."""
        volume_name = self.generate_name()
        storage_group_name = self.create_empty_storage_group()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, '1'))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        self.provisioning.remove_volume_from_storage_group(
            storage_group_name, device_id)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(0, storage_group_details[constants.NUM_OF_VOLS])
        self.provisioning.add_existing_vol_to_sg(
            storage_group_name, device_id)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(1, storage_group_details[constants.NUM_OF_VOLS])
        volume_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        self.assertIn(device_id, volume_list)

    def test_add_new_volume_to_storage_group(self):
        """Test add_new_volume_to_storage_group."""
        storage_group_name = self.create_empty_storage_group()
        storage_group_details = (
            self.provisioning.add_new_volume_to_storage_group(
                storage_group_name, 1, '1', 'GB', create_new_volumes=True))
        time.sleep(10)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(1, storage_group_details[constants.NUM_OF_VOLS])
        volume_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        for volume in volume_list:
            self.addCleanup(self.delete_volume, storage_group_name, volume)

    def test_add_new_volume_to_storage_group_mobility_id_enabled(self):
        """Test add_new_volume_to_storage_group with mobility id."""
        storage_group_name = self.create_empty_storage_group()
        storage_group_details = (
            self.provisioning.add_new_volume_to_storage_group(
                storage_group_name, 1, '1', 'GB', create_new_volumes=True,
                enable_mobility_id=True))
        time.sleep(10)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(1, storage_group_details[constants.NUM_OF_VOLS])
        volume_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        volume_details = self.provisioning.get_volume(volume_list[0])
        self.assertTrue(volume_details.get('mobility_id_enabled'))
        for volume in volume_list:
            self.addCleanup(self.delete_volume, storage_group_name, volume)

    def test_add_new_vol_to_storagegroup(self):
        """Test add_new_vol_to_storagegroup."""
        storage_group_name = self.create_empty_storage_group()
        storage_group_details = self.provisioning.add_new_vol_to_storagegroup(
            storage_group_name, 1, '1', 'GB')
        time.sleep(10)
        self._validate_storage_group_details(
            storage_group_name, storage_group_details)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(1, storage_group_details[constants.NUM_OF_VOLS])
        volume_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        for volume in volume_list:
            self.addCleanup(self.delete_volume, storage_group_name, volume)

    def test_add_new_vol_to_srdf_storage_group(self):
        """Tests adding a volume to a storage group that is replicated"""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        self.provisioning.add_new_volume_to_storage_group(
            storage_group_id=sg_name, vol_size=1, num_vols=1, cap_unit='GB',
            remote_array_1_id=self.conn.remote_array,
            remote_array_1_sgs=[sg_name])
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name=sg_name)
        self.assertEqual(2, storage_group_details[constants.NUM_OF_VOLS])

    def test_remove_volume_from_storage_group(self):
        """Test remove_volume_from_storage_group."""
        volume_name = self.generate_name()
        storage_group_name = self.create_empty_storage_group()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, '1'))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        self.provisioning.remove_volume_from_storage_group(
            storage_group_name, device_id)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(0, storage_group_details[constants.NUM_OF_VOLS])
        self.provisioning.add_existing_volume_to_storage_group(
            storage_group_name, device_id)

    def test_remove_volume_from_srdf_storage_group(self):
        """Tests adding a volume to a storage group that is replicated"""
        sg_name, srdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        self.provisioning.add_new_volume_to_storage_group(
            storage_group_id=sg_name, vol_size=1, num_vols=1, cap_unit='GB',
            remote_array_1_id=self.conn.remote_array,
            remote_array_1_sgs=[sg_name])
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name=sg_name)
        self.assertEqual(2, storage_group_details[constants.NUM_OF_VOLS])
        self.provisioning.remove_volume_from_storage_group(
            storage_group_id=sg_name, vol_id=device_id,
            remote_array_1_id=self.conn.remote_array,
            remote_array_1_sgs=[sg_name])
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name=sg_name)
        self.assertEqual(1, storage_group_details[constants.NUM_OF_VOLS])

    def test_remove_vol_from_storagegroup(self):
        """Test remove_vol_from_storagegroup."""
        volume_name = self.generate_name()
        storage_group_name = self.create_empty_storage_group()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, '1'))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        self.provisioning.remove_vol_from_storagegroup(
            storage_group_name, device_id)
        storage_group_details = self.provisioning.get_storage_group(
            storage_group_name)
        self.assertEqual(0, storage_group_details[constants.NUM_OF_VOLS])
        self.provisioning.add_existing_volume_to_storage_group(
            storage_group_name, device_id)

    def test_move_volumes_between_storage_groups(self):
        """Test move_volumes_between_storage_groups."""
        storage_group_name_1 = self.create_empty_storage_group()
        storage_group_name_2 = self.create_empty_storage_group()
        volume_name = self.generate_name()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name_1, '1'))
        time.sleep(10)
        storage_group_details_1 = self.provisioning.get_storage_group(
            storage_group_name_1)
        storage_group_details_2 = self.provisioning.get_storage_group(
            storage_group_name_2)
        self.assertEqual(1, storage_group_details_1[constants.NUM_OF_VOLS])
        self.assertEqual(0, storage_group_details_2[constants.NUM_OF_VOLS])
        self.provisioning.move_volumes_between_storage_groups(
            device_id, storage_group_name_1, storage_group_name_2)
        self.addCleanup(self.delete_volume, storage_group_name_2, device_id)
        storage_group_details_1 = self.provisioning.get_storage_group(
            storage_group_name_1)
        storage_group_details_2 = self.provisioning.get_storage_group(
            storage_group_name_2)
        self.assertEqual(0, storage_group_details_1[constants.NUM_OF_VOLS])
        self.assertEqual(1, storage_group_details_2[constants.NUM_OF_VOLS])

    def test_update_storage_group_qos_all(self):
        """Test update_storage_group_qos."""
        storage_group_name = self.create_empty_storage_group()
        max_iops = 'maxIOPS'
        iops = '3000'
        mbps = '4000'
        distribution = 'Never'
        qos_update = {max_iops: iops, constants.MAX_MBPS: mbps,
                      constants.DISTRIBUTION_TYPE: distribution}
        update_results = self.provisioning.update_storage_group_qos(
            storage_group_name, qos_update)
        qos_specs = update_results[constants.HOST_IO_LIMIT]
        self._validate_qos_specs(iops, mbps, distribution, qos_specs)

    def test_update_storagegroup_qos_all(self):
        """Test update_storagegroup_qos."""
        storage_group_name = self.create_empty_storage_group()
        max_iops = 'maxIOPS'
        iops = '3000'
        mbps = '4000'
        distribution = 'Never'
        qos_update = {max_iops: iops, constants.MAX_MBPS: mbps,
                      constants.DISTRIBUTION_TYPE: distribution}
        update_results = self.provisioning.update_storagegroup_qos(
            storage_group_name, qos_update)
        qos_specs = update_results[constants.HOST_IO_LIMIT]
        self._validate_qos_specs(iops, mbps, distribution, qos_specs)

    def test_update_storage_group_qos_exception(self):
        """Test update_storage_group_qos exception."""
        storage_group_name = self.create_empty_storage_group()
        qos_update = {constants.MAX_MBPS: '3000',
                      constants.DISTRIBUTION_TYPE: 'Invalid Type'}
        self.assertRaises(exception.InvalidInputException,
                          self.provisioning.update_storage_group_qos,
                          storage_group_name, qos_update)

    def test_set_host_io_limit_iops_or_mbps(self):
        """Test set_host_io_limit_iops_or_mbps."""
        storage_group_name = self.create_empty_storage_group()
        iops = 3000
        distribution_type = 'Always'
        mbps = 5000
        modify_result = self.provisioning.set_host_io_limit_iops_or_mbps(
            storage_group_name, iops, distribution_type, mbps)
        qos_specs = self.provisioning.get_storage_group(
            storage_group_name)[constants.HOST_IO_LIMIT]
        self._validate_qos_specs(str(iops), str(mbps), distribution_type,
                                 modify_result[constants.HOST_IO_LIMIT])
        self._validate_qos_specs(str(iops), str(mbps), distribution_type,
                                 qos_specs)

    def test_delete_storage_group(self):
        """Test delete_storage_group."""
        storage_group_name = self.create_empty_storage_group()
        storage_group_list = self.provisioning.get_storage_group_list()
        self.assertIn(storage_group_name, storage_group_list)
        self.provisioning.delete_storage_group(storage_group_name)
        storage_group_list = self.provisioning.get_storage_group_list()
        self.assertNotIn(storage_group_name, storage_group_list)

    def test_delete_storagegroup(self):
        """Test delete_storagegroup."""
        storage_group_name = self.create_empty_storage_group()
        storage_group_list = self.provisioning.get_storage_group_list()
        self.assertIn(storage_group_name, storage_group_list)
        self.provisioning.delete_storagegroup(storage_group_name)
        storage_group_list = self.provisioning.get_storage_group_list()
        self.assertNotIn(storage_group_name, storage_group_list)

    def test_get_volume_known_volume(self):
        """Test get_volume known volume contents."""
        volume = self.create_volume()
        volume_details = self.provisioning.get_volume(
            volume[constants.DEVICE_ID])
        self._validate_volume_details(volume_details)
        self.assertEqual(volume[constants.VOLUME_NAME],
                         volume_details[constants.VOLUME_IDENTIFIER])
        self.assertEqual(volume['storage_group'],
                         volume_details[constants.STORAGE_GROUP_ID_CAMEL][0])
        self.assertEqual(volume[constants.DEVICE_ID],
                         volume_details[constants.VOLUME_ID_CAMEL])

    def test_get_volume(self):
        """Test get_volume all volumes."""
        volume_list = self.provisioning.get_volume_list()
        self.assertIsInstance(volume_list, list)
        for volume in volume_list:
            self.assertIsInstance(volume, str)
            volume_details = self.provisioning.get_volume(volume)
            self._validate_volume_details(volume_details)

    def test_get_volume_list(self):
        """Test get_volume_list."""
        volume_list = self.provisioning.get_volume_list()
        self.assertIsInstance(volume_list, list)
        for volume in volume_list:
            self.assertIsInstance(volume, str)

    def test_get_volume_effective_wwn_details_84(self):
        """Test test_get_volume_effective_wwn_details_84."""
        volume_list = self.provisioning.get_volume_list()
        selected_volume_list = list()
        selected_volume_details = None
        for volume in volume_list:
            volume_details = self.provisioning.get_volume(volume)
            if volume_details[constants.HAS_EFFECTIVE_WWN]:
                selected_volume_list.append(volume)
                selected_volume_details = volume_details
                break
        if selected_volume_details is None:
            self.skipTest('test_get_volume_effective_wwn_details_84 - could '
                          'not find a volume with effective wwn flag set to '
                          'true.')
        csv_file_name = 'test.csv'
        temp_dir = self.create_temp_directory()
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        self.provisioning.get_vol_effective_wwn_details_84(
            selected_volume_list, csv_file_path)
        parsed_values = file_handler.read_csv_values(csv_file_path)
        self.assertIsInstance(parsed_values, dict)
        self.assertIn(constants.VOLUME_ID_CAMEL, parsed_values)
        self.assertIn(constants.WWN, parsed_values)
        self.assertIn(constants.HAS_EFFECTIVE_WWN, parsed_values)
        self.assertIn(constants.EFFECTIVE_WWN, parsed_values)
        self.assertIn(constants.STORAGE_GROUP_ID_CAMEL, parsed_values)
        self.assertEqual(
            selected_volume_details[constants.VOLUME_ID_CAMEL], parsed_values[
                constants.VOLUME_ID_CAMEL][0])
        self.assertEqual(selected_volume_details[constants.WWN],
                         parsed_values[constants.WWN][0])
        self.assertEqual(
            str(selected_volume_details[constants.HAS_EFFECTIVE_WWN]),
            parsed_values[constants.HAS_EFFECTIVE_WWN][0])
        self.assertEqual(
            selected_volume_details[constants.EFFECTIVE_WWN],
            parsed_values[constants.EFFECTIVE_WWN][0])
        if selected_volume_details.get('num_of_storage_groups', 0) > 0:
            if constants.STORAGE_GROUP_ID_CAMEL in selected_volume_details:
                storage_group_reference = selected_volume_details[
                    constants.STORAGE_GROUP_ID_CAMEL]
            else:
                storage_group_reference = None
            self.assertEqual(
                str(storage_group_reference),
                parsed_values[constants.STORAGE_GROUP_ID_CAMEL][0])

    def test_get_volume_effective_wwn_details(self):
        """Test get_volume_effective_wwn_details."""
        volume_list = self.provisioning.get_volume_list()
        selected_volume_list = list()
        selected_volume_details = None
        for volume in volume_list:
            volume_details = self.provisioning.get_volume(volume)
            if volume_details[constants.HAS_EFFECTIVE_WWN]:
                selected_volume_list.append(volume)
                selected_volume_details = volume_details
                break
        if selected_volume_details is None:
            self.skipTest('test_get_volume_effective_wwn_details - could not '
                          'find a volume with effective wwn flag set to '
                          'true.')
        csv_file_name = 'test.csv'
        temp_dir = self.create_temp_directory()
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        self.provisioning.get_volume_effective_wwn_details(
            selected_volume_list, csv_file_path)
        parsed_values = file_handler.read_csv_values(csv_file_path)
        self._validate_effective_wwn_details(
            selected_volume_details, parsed_values)

    def test_get_volume_effective_wwn_details_no_output_file(self):
        """Test get_volume_effective_wwn_details."""
        volume_list = self.provisioning.get_volume_list()
        selected_volume_list = list()
        selected_volume_details = None
        for volume in volume_list:
            volume_details = self.provisioning.get_volume(volume)
            if volume_details[constants.HAS_EFFECTIVE_WWN]:
                selected_volume_list.append(volume)
                selected_volume_details = volume_details
                break
        if selected_volume_details is None:
            self.skipTest(
                'test_get_volume_effective_wwn_details_no_output_file - '
                'could not find a volume with effective wwn flag set '
                'to true.')
        wwn_details_list = self.provisioning.get_volume_effective_wwn_details(
            selected_volume_list)[0]
        # Return value with output file are different to no output file
        # Need to create dict from return data and known keys.
        keys_list = [
            constants.VOLUME_ID, constants.EFFECTIVE_WWN, constants.WWN,
            constants.HAS_EFFECTIVE_WWN, constants.STORAGE_GROUP_ID]
        _zip = zip(keys_list, wwn_details_list)
        wwn_details_dict = dict(_zip)
        # Need to update this dicts values to be nested inside lists.
        for key, val in wwn_details_dict.items():
            wwn_details_dict[key] = [val]
        self._validate_effective_wwn_details(
            selected_volume_details, wwn_details_dict)

    def test_get_volumes_from_storage_group(self):
        """Test get_volumes_from_storage_group."""
        storage_group_name = self.create_empty_storage_group()
        volume_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        self.assertEqual(list(), volume_list)
        self.assertIsInstance(volume_list, list)
        volume_name = self.generate_name()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, 1))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        volume_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_name)
        self.assertIsInstance(volume_list, list)
        self.assertIn(device_id, volume_list)
        for volume in volume_list:
            self.assertIsInstance(volume, str)

    def test_get_vols_from_storagegroup(self):
        """Test get_vols_from_storagegroup."""
        storage_group_name = self.create_empty_storage_group()
        volume_list = self.provisioning.get_vols_from_storagegroup(
            storage_group_name)
        self.assertEqual(list(), volume_list)
        self.assertIsInstance(volume_list, list)
        volume_name = self.generate_name()
        self.provisioning.create_volume_from_storage_group_return_id(
            volume_name, storage_group_name, 1)
        time.sleep(10)
        device_id = self.provisioning.find_volume_device_id(volume_name)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        volume_list = self.provisioning.get_vols_from_storagegroup(
            storage_group_name)
        self.assertIsInstance(volume_list, list)
        self.assertIn(device_id, volume_list)
        for volume in volume_list:
            self.assertIsInstance(volume, str)

    def test_get_storage_group_from_volume(self):
        """Test get_storage_group_from_volume."""
        storage_group_name = self.create_empty_storage_group()
        volume_name = self.generate_name()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, 1))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        storage_group_list = self.provisioning.get_storage_group_from_volume(
            device_id)
        self.assertIsNotNone(storage_group_list)
        self.assertIsInstance(storage_group_list, list)
        self.assertIn(storage_group_name, storage_group_list)
        for storage_group in storage_group_list:
            self.assertIsInstance(storage_group, str)

    def test_get_storagegroup_from_vol(self):
        """Test get_storagegroup_from_vol."""
        storage_group_name = self.create_empty_storage_group()
        volume_name = self.generate_name()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, 1))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        storage_group_list = self.provisioning.get_storagegroup_from_vol(
            device_id)
        self.assertIsNotNone(storage_group_list)
        self.assertIsInstance(storage_group_list, list)
        self.assertIn(storage_group_name, storage_group_list)
        for storage_group in storage_group_list:
            self.assertIsInstance(storage_group, str)

    def test_is_volume_in_storage_group_true(self):
        """Test is_volume_in_storage_group True result."""
        storage_group_name = self.create_empty_storage_group()
        volume_name = self.generate_name()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, 1))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        result = self.provisioning.is_volume_in_storage_group(
            device_id, storage_group_name)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_is_volume_in_storage_group_true_legacy_create(self):
        """Test is_volume_in_storage_group True result legacy vol create."""
        storage_group_name = self.create_empty_storage_group()
        device_id = (
            self.provisioning.create_volume_from_sg_return_dev_id(
                self.generate_name(), storage_group_name, 1))
        time.sleep(10)
        self.addCleanup(self.delete_volume, storage_group_name, device_id)
        result = self.provisioning.is_volume_in_storage_group(
            device_id, storage_group_name)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_is_volume_in_storage_group_false(self):
        """Test is_volume_in_storage_group False result."""
        storage_group_name = self.create_empty_storage_group()
        device_id = self.create_volume()[constants.DEVICE_ID]
        result = self.provisioning.is_volume_in_storage_group(
            device_id, storage_group_name)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_is_volume_in_storagegroup(self):
        """Test is_volume_in_storagegroup."""
        storage_group_name = self.create_empty_storage_group()
        device_id = self.create_volume()[constants.DEVICE_ID]
        result = self.provisioning.is_volume_in_storagegroup(
            device_id, storage_group_name)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_find_volume_device_id(self):
        """Test find_volume_device_id."""
        volume_details = self.create_volume()
        volume_name = volume_details[constants.VOLUME_NAME]
        device_id = self.provisioning.find_volume_device_id(volume_name)
        self.assertIsNotNone(device_id)
        self.assertIsInstance(device_id, str)
        self.assertEqual(volume_details[constants.DEVICE_ID], device_id)

    def test_find_volume_identifier(self):
        """Test find_volume_identifier."""
        volume_details = self.create_volume()
        device_id = volume_details[constants.DEVICE_ID]
        identifier = self.provisioning.find_volume_identifier(device_id)
        self.assertIsNotNone(identifier)
        self.assertIsInstance(identifier, str)
        self.assertEqual(volume_details[constants.VOLUME_NAME], identifier)

    def test_get_size_of_device_on_array(self):
        """Test get_size_of_device_on_array."""
        volume_details = self.create_volume()
        device_id = volume_details[constants.DEVICE_ID]
        device_size = self.provisioning.get_size_of_device_on_array(device_id)
        self.assertIsNotNone(device_size)
        self.assertIsInstance(device_size, float)
        self.assertEqual(1, device_size)

    def test_modify_volume(self):
        """Test _modify_volume."""
        volume_details = self.create_volume()
        device_id = volume_details[constants.DEVICE_ID]
        old_name = volume_details[constants.VOLUME_NAME]
        volume_details = self.provisioning.get_volume(device_id)
        self.assertEqual(
            old_name, volume_details[constants.VOLUME_IDENTIFIER])
        new_name = self.generate_name()
        identifier_name = 'identifier_name'
        payload = (
            {'editVolumeActionParam': {
                'modifyVolumeIdentifierParam': {
                    'volumeIdentifier': {
                        identifier_name: new_name,
                        'volumeIdentifierChoice': identifier_name}}}})
        self.provisioning._modify_volume(device_id, payload)
        volume_details = self.provisioning.get_volume(device_id)
        self.assertEqual(
            new_name, volume_details[constants.VOLUME_IDENTIFIER])

    def test_extend_volume(self):
        """Test extend_volume."""
        volume_details = self.create_volume()
        device_id = volume_details[constants.DEVICE_ID]
        self.provisioning.get_volume(device_id)
        old_size = self.provisioning.get_volume(device_id)[constants.CAP_GB]
        new_size = old_size + 1
        job = self.provisioning.extend_volume(
            device_id, new_size, _async=True)
        self.conn.common.wait_for_job_complete(job)
        volume_details = self.provisioning.get_volume(device_id)
        self._validate_volume_details(volume_details)
        self.assertEqual(new_size, volume_details[constants.CAP_GB])

    def test_extend_volume_rdf(self):
        """Test extend_volume for rdf protected volume."""
        sg_name, rdf_group_number, device_id, remote_volume = (
            self.create_rdf_sg())
        old_size = self.provisioning.get_volume(device_id)[constants.CAP_GB]
        new_size = old_size + 1
        job = self.provisioning.extend_volume(
            device_id, new_size, _async=True, rdf_group_num=rdf_group_number)
        self.conn.common.wait_for_job_complete(job)
        volume_details = self.provisioning.get_volume(device_id)
        self._validate_volume_details(volume_details)
        self.assertEqual(new_size, volume_details[constants.CAP_GB])

    def test_rename_volume(self):
        """Test rename_volume."""
        volume_details = self.create_volume()
        device_id = volume_details[constants.DEVICE_ID]
        new_name = self.generate_name()
        self.provisioning.rename_volume(device_id, new_name)
        identifier = self.provisioning.find_volume_identifier(device_id)
        self.assertEqual(identifier, new_name)

    def test_delete_volume(self):
        """Test delete_volume."""
        volume_name = self.generate_name()
        storage_group_name = self.create_empty_storage_group()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, storage_group_name, '1'))
        time.sleep(10)
        volume_list = self.provisioning.get_volume_list()
        self.assertIn(device_id, volume_list)
        self.provisioning.remove_volume_from_storage_group(
            storage_group_name, device_id)
        self.provisioning.delete_volume(device_id)
        volume_list = self.provisioning.get_volume_list()
        self.assertNotIn(device_id, volume_list)

    def test_find_low_volume_utilization(self):
        """Test find_low_volume_utilization."""
        csv_file_name = 'test.csv'
        temp_dir = self.create_temp_directory()
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        self.provisioning.find_low_volume_utilization(10, csv_file_path)
        parsed_values = file_handler.read_csv_values(csv_file_path)
        self.assertIsNotNone(parsed_values)
        self.assertIsInstance(parsed_values, dict)
        sg_name = 'sg_name'
        identifier = 'identifier'
        capacity = 'capacity'
        self.assertIn(sg_name, parsed_values)
        self.assertIn(constants.VOLUME_ID, parsed_values)
        self.assertIn(identifier, parsed_values)
        self.assertIn(capacity, parsed_values)
        self.assertIn(constants.ALLOCATED_PERCENT, parsed_values)
        self.assertIsInstance(parsed_values[sg_name], list)
        self.assertIsInstance(parsed_values[constants.VOLUME_ID], list)
        self.assertIsInstance(parsed_values[identifier], list)
        self.assertIsInstance(parsed_values[capacity], list)
        self.assertIsInstance(
            parsed_values[constants.ALLOCATED_PERCENT], list)

    def test_get_workload_settings(self):
        """Test get_workload_settings."""
        workload_settings = self.provisioning.get_workload_settings()
        self.assertIsNotNone(workload_settings)
        self.assertIsInstance(workload_settings, list)

    def test_get_any_director_port(self):
        """Test get_any_director_port."""
        fa_directors = self.provisioning.get_fa_directors()
        fa_director = fa_directors[0]
        port = self.provisioning.get_any_director_port(fa_director)
        self.assertIsNotNone(port)
        self.assertIsInstance(port, str)

    def test_format_director_port(self):
        """Test format_director_port."""
        fa_directors = self.provisioning.get_fa_directors()
        if fa_directors:
            fa_director = fa_directors[0]
            port = self.provisioning.get_any_director_port(fa_director)
            result = self.provisioning.format_director_port(fa_director, port)
            formatted_director_port = '{d}:{p}'.format(d=fa_director, p=port)
            self.assertEqual(result, formatted_director_port)

    def test_get_active_masking_view_connections(self):
        """Test get_active_masking_view_connections."""
        masking_view, connections = (
            self.provisioning.get_active_masking_view_connections())
        if masking_view:
            self.assertIsInstance(masking_view, str)
        if connections:
            self.assertIsInstance(connections, list)
            for connection in connections:
                self._validiate_masking_view_connection(connection)

    def test_get_fa_directors(self):
        """Test get_fa_directors."""
        fa_directors = self.provisioning.get_fa_directors()
        self.assertIsNotNone(fa_directors)
        self.assertIsInstance(fa_directors, list)
        for fa_director in fa_directors:
            self.assertIsInstance(fa_director, str)
            self.assertIsNotNone(
                re.match(constants.DIRECTOR_SEARCH_PATTERN, fa_director))

    def test_get_available_initiator(self):
        """Test get_available_initiator."""
        initiator = self.provisioning.get_available_initiator()
        if initiator:
            self.assertIsInstance(initiator, str)
            self.assertIsNotNone(
                re.match(constants.INITIATOR_SEARCH_PATTERN, initiator))
        else:
            self.skipTest("test_get_available_initiator "
                          "- Unable to get an available initiator.")

    def test_get_in_use_initiator(self):
        """Test get_in_use_initiator."""
        initiator = self.provisioning.get_in_use_initiator()
        if initiator:
            self.assertIsInstance(initiator, str)
            self.assertIsNotNone(
                re.match(constants.INITIATOR_SEARCH_PATTERN, initiator))
        else:
            self.skipTest("test_get_available_initiator "
                          "- Unable to get an in-use initiator.")

    def test_get_available_initiator_wwn_as_list(self):
        """Test get_available_initiator_wwn_as_list."""
        initiator = self.provisioning.get_available_initiator_wwn_as_list()
        if initiator:
            self.assertIsInstance(initiator, list)
            self.assertIsNotNone(
                re.match(constants.WWN_SEARCH_PATTERN_16, initiator[0]))
        else:
            self.skipTest("test_get_available_initiator "
                          "- Unable to get an available initiator.")

    ##############
    # Validators #
    ##############

    def _validate_port_group_details(
            self, port_group_name, port_group_details,
            director_port_list=None, ref_port_count=1, ref_view_count=0,
            ref_type='Fibre'):
        """Validate the contents of port group return dictionary.

        :param port_group_name: name to validate -- str
        :param port_group_details: return details of port group -- dict
        :param director_port_list: director and port ids to validate -- list
        :param ref_port_count: reference port count to check for -- int
        :param ref_view_count: reference view count to check for -- int
        :param ref_type: reference connection type to check for -- str
        """
        port_group_list = self.provisioning.get_port_group_list()
        self.assertIn(port_group_name, port_group_list)

        self.assertIn(constants.PORT_GROUP_ID, port_group_details)
        port_group_id = port_group_details[constants.PORT_GROUP_ID]
        self.assertEqual(port_group_name, port_group_id)
        self.assertIsInstance(port_group_id, str)

        self.assertIn(constants.SYMMETRIX_PORT_KEY, port_group_details)
        symmetrix_port_key = port_group_details[constants.SYMMETRIX_PORT_KEY]
        self.assertIsInstance(symmetrix_port_key, list)
        for port_key in symmetrix_port_key:
            self.assertIsInstance(port_key, dict)
            self.assertIn(constants.DIRECTOR_ID, port_key)
            director_id = port_key[constants.DIRECTOR_ID]
            self.assertIsNotNone(re.match(constants.DIRECTOR_SEARCH_PATTERN,
                                          director_id))
            self.assertIsInstance(director_id, str)
            self.assertIn(constants.PORT_ID, port_key)
            port_id = port_key[constants.PORT_ID]
            self.assertIsNotNone(
                re.match(constants.PORT_SEARCH_PATTERN, port_id))
            self.assertIsInstance(port_id, str)
            if director_port_list:
                director_port = self.provisioning.format_director_port(
                    director_id, port_id)
                self.assertIn(director_port, director_port_list)

        self.assertIn(constants.NUM_OF_PORTS, port_group_details)
        num_of_ports = port_group_details[constants.NUM_OF_PORTS]
        self.assertIsInstance(num_of_ports, int)
        self.assertEqual(ref_port_count, num_of_ports)

        self.assertIn(constants.NUM_OF_MASKING_VIEWS, port_group_details)
        num_of_masking_views = port_group_details[
            constants.NUM_OF_MASKING_VIEWS]
        self.assertIsInstance(num_of_masking_views, int)
        self.assertEqual(ref_view_count, num_of_masking_views)

        self.assertIn(constants.TYPE, port_group_details)
        connection_type = port_group_details[constants.TYPE]
        self.assertIsInstance(connection_type, str)
        self.assertEqual(ref_type, connection_type)

    def _validate_initiator_details(self, initiator_details):
        """Validate the return contents of initiator requests.

        :param initiator_details: content of initiator -- dict
        """
        num_of_host_groups = 'num_of_host_groups'
        num_of_powerpath_hosts = 'num_of_powerpath_hosts'
        self.assertIsInstance(initiator_details, dict)
        self.assertIn(constants.INITIATOR_ID, initiator_details)
        self.assertIn(constants.SYMMETRIX_PORT_KEY, initiator_details)
        self.assertIn(constants.TYPE, initiator_details)
        self.assertIn(constants.LOGGED_IN, initiator_details)
        self.assertIn(constants.ON_FABRIC, initiator_details)
        self.assertIn(constants.NUM_OF_VOLS, initiator_details)
        self.assertIn(num_of_host_groups, initiator_details)
        self.assertIn(constants.NUM_OF_MASKING_VIEWS, initiator_details)
        self.assertIn(num_of_powerpath_hosts, initiator_details)
        self.assertIsInstance(initiator_details[constants.INITIATOR_ID], str)
        self.assertIsInstance(
            initiator_details[constants.SYMMETRIX_PORT_KEY], list)
        self.assertIsInstance(initiator_details[constants.TYPE], str)
        self.assertIsInstance(initiator_details[constants.LOGGED_IN], bool)
        self.assertIsInstance(initiator_details[constants.ON_FABRIC], bool)
        self.assertIsInstance(initiator_details[constants.NUM_OF_VOLS], int)
        self.assertIsInstance(initiator_details[num_of_host_groups], int)
        self.assertIsInstance(
            initiator_details[constants.NUM_OF_MASKING_VIEWS], int)
        self.assertIsInstance(initiator_details[num_of_powerpath_hosts], int)

        flags_in_effect = 'flags_in_effect'
        masking_view = 'maskingview'
        port_flags_override = 'port_flags_override'
        fabric_name = 'fabric_name'
        fcid_lockdown = 'fcid_lockdown'
        if flags_in_effect in initiator_details:
            self.assertIsInstance(initiator_details[flags_in_effect], str)
        if masking_view in initiator_details:
            self.assertIsInstance(initiator_details[masking_view], list)
        if constants.HOST in initiator_details:
            self.assertIsInstance(initiator_details[constants.HOST], str)
        if port_flags_override in initiator_details:
            self.assertIsInstance(
                initiator_details[port_flags_override], bool)
        if fabric_name in initiator_details:
            self.assertIsInstance(initiator_details[fabric_name], str)
        if constants.ALIAS in initiator_details:
            self.assertIsInstance(initiator_details[constants.ALIAS], str)
        if constants.FCID in initiator_details:
            self.assertIsInstance(initiator_details[constants.FCID], str)
        if fcid_lockdown in initiator_details:
            self.assertIsInstance(initiator_details[fcid_lockdown], str)

    def _validate_service_level_details(
            self, service_level_id, service_level_details):
        """Validate the return contents of service level requests.

        :param service_level_id: reference id to check for -- str
        :param service_level_details: content of service level -- dict
        """
        slo_base_id = 'sloBaseId'
        average_expected_response_time = 'average_expected_response_time_ms'
        num_of_workloads = 'num_of_workloads'
        workload_id = 'workloadId'
        self.assertIsNotNone(service_level_details)
        self.assertIsInstance(service_level_details, dict)
        self.assertIn(constants.SLO_ID, service_level_details)
        self.assertIn(slo_base_id, service_level_details)
        self.assertIn(average_expected_response_time, service_level_details)
        self.assertIn(num_of_workloads, service_level_details)
        self.assertIn(constants.NUM_OF_STORAGE_GROUPS, service_level_details)
        self.assertIn(workload_id, service_level_details)
        self.assertIsInstance(service_level_details[constants.SLO_ID], str)
        self.assertIsInstance(service_level_details[slo_base_id], str)
        self.assertIs(
            str, type(service_level_details[average_expected_response_time]))
        self.assertIsInstance(service_level_details[num_of_workloads], int)
        self.assertIs(
            int, type(service_level_details[constants.NUM_OF_STORAGE_GROUPS]))
        self.assertIsInstance(service_level_details[workload_id], list)
        self.assertEqual(
            service_level_id, service_level_details[constants.SLO_ID])
        for workload_id in service_level_details[workload_id]:
            self.assertIsInstance(workload_id, str)
        if constants.STORAGE_GROUP_ID_CAMEL in service_level_details:
            self.assertIs(
                list, type(
                    service_level_details[constants.STORAGE_GROUP_ID_CAMEL]))
            storage_groups = service_level_details[
                constants.STORAGE_GROUP_ID_CAMEL]
            for storage_group in storage_groups:
                self.assertIsInstance(storage_group, str)

    def _validate_storage_group_details(
            self, storage_group_id, storage_group_details):
        """Validate the return contents of storage group requests.

        :param storage_group_id: reference id to check for -- str
        :param storage_group_details: content of storage group -- dict
        """
        self.assertIsNotNone(storage_group_details)
        self.assertIn(constants.STORAGE_GROUP_ID_CAMEL, storage_group_details)
        self.assertIn(constants.SLO, storage_group_details)
        self.assertIn(constants.SERVICE_LEVEL, storage_group_details)
        self.assertIn(constants.BASE_SLO_NAME, storage_group_details)
        self.assertIn(constants.SRP, storage_group_details)
        self.assertIn(constants.SLO_COMPLIANCE, storage_group_details)
        self.assertIn(constants.NUM_OF_VOLS, storage_group_details)
        self.assertIn(constants.NUM_OF_CHILD_SGS, storage_group_details)
        self.assertIn(constants.NUM_OF_PARENT_SGS, storage_group_details)
        self.assertIn(constants.NUM_OF_MASKING_VIEWS, storage_group_details)
        self.assertIn(constants.NUM_OF_SNAPSHOTS, storage_group_details)
        self.assertIn(constants.CAP_GB, storage_group_details)
        self.assertIn(constants.DEVICE_EMULATION, storage_group_details)
        self.assertIn(constants.TYPE, storage_group_details)
        self.assertIn(constants.UNPROTECTED, storage_group_details)
        self.assertIsInstance(
            storage_group_details[constants.STORAGE_GROUP_ID_CAMEL], str)
        self.assertIsInstance(storage_group_details[constants.SLO], str)
        self.assertIsInstance(
            storage_group_details[constants.SERVICE_LEVEL], str)
        self.assertIsInstance(
            storage_group_details[constants.BASE_SLO_NAME], str)
        self.assertIsInstance(storage_group_details[constants.SRP], str)
        self.assertIsInstance(
            storage_group_details[constants.SLO_COMPLIANCE], str)
        self.assertIsInstance(
            storage_group_details[constants.NUM_OF_VOLS], int)
        self.assertIsInstance(
            storage_group_details[constants.NUM_OF_CHILD_SGS], int)
        self.assertIsInstance(
            storage_group_details[constants.NUM_OF_PARENT_SGS], int)
        self.assertIs(
            int, type(storage_group_details[constants.NUM_OF_MASKING_VIEWS]))
        self.assertIsInstance(
            storage_group_details[constants.NUM_OF_SNAPSHOTS], int)
        self.assertIsInstance(storage_group_details[constants.CAP_GB], float)
        self.assertIsInstance(
            storage_group_details[constants.DEVICE_EMULATION], str)
        self.assertIsInstance(storage_group_details[constants.TYPE], str)
        self.assertIsInstance(
            storage_group_details[constants.UNPROTECTED], bool)
        self.assertIsInstance(
            storage_group_details[constants.COMPRESSION], bool)
        self.assertEqual(
            storage_group_id,
            storage_group_details[constants.STORAGE_GROUP_ID_CAMEL])
        if constants.COMPRESSION in storage_group_details:
            self.assertIsInstance(
                storage_group_details[constants.COMPRESSION], bool)

    def _validate_volume_details(self, volume_details):
        """Validate the return contents of volume requests.

        :param volume_details: content of volume -- dict
        """
        self.assertIn(constants.VOLUME_ID_CAMEL, volume_details)
        self.assertIn(constants.TYPE, volume_details)
        self.assertIn(constants.EMULATION, volume_details)
        self.assertIn(constants.SSID, volume_details)
        self.assertIn(constants.ALLOCATED_PERCENT, volume_details)
        self.assertIn(constants.CAP_GB, volume_details)
        self.assertIn(constants.CAP_MB, volume_details)
        self.assertIn(constants.CAP_CYL, volume_details)
        self.assertIn(constants.STATUS, volume_details)
        self.assertIn(constants.RESERVED, volume_details)
        self.assertIn(constants.PINNED, volume_details)
        self.assertIn(constants.ENCAPSULATED, volume_details)
        self.assertIn(constants.NUM_OF_STORAGE_GROUPS, volume_details)
        self.assertIn(constants.NUM_OF_FRONT_END_PATHS, volume_details)
        self.assertIn(constants.SNAPVX_SOURCE, volume_details)
        self.assertIn(constants.SNAPVX_TARGET, volume_details)
        self.assertIn(constants.HAS_EFFECTIVE_WWN, volume_details)
        self.assertIn(constants.MOBILITY_ID_ENABLED, volume_details)
        self.assertIsInstance(volume_details[constants.VOLUME_ID_CAMEL], str)
        self.assertIsInstance(volume_details[constants.TYPE], str)
        self.assertIsInstance(volume_details[constants.EMULATION], str)
        self.assertIsInstance(volume_details[constants.SSID], str)
        self.assertIsInstance(
            volume_details[constants.ALLOCATED_PERCENT], int)
        self.assertIsInstance(volume_details[constants.CAP_GB], float)
        self.assertIsInstance(volume_details[constants.CAP_MB], float)
        self.assertIsInstance(volume_details[constants.CAP_CYL], int)
        self.assertIsInstance(volume_details[constants.STATUS], str)
        self.assertIsInstance(volume_details[constants.RESERVED], bool)
        self.assertIsInstance(volume_details[constants.PINNED], bool)
        self.assertIsInstance(volume_details[constants.ENCAPSULATED], bool)
        self.assertIsInstance(
            volume_details[constants.NUM_OF_STORAGE_GROUPS], int)
        self.assertIsInstance(
            volume_details[constants.NUM_OF_FRONT_END_PATHS], int)
        self.assertIsInstance(volume_details[constants.SNAPVX_SOURCE], bool)
        self.assertIsInstance(volume_details[constants.SNAPVX_TARGET], bool)
        self.assertIsInstance(
            volume_details[constants.HAS_EFFECTIVE_WWN], bool)
        self.assertIsInstance(
            volume_details[constants.MOBILITY_ID_ENABLED], bool)

        if constants.VOLUME_IDENTIFIER in volume_details:
            self.assertIsInstance(
                volume_details[constants.VOLUME_IDENTIFIER], str)
        if constants.STORAGE_GROUP_ID_CAMEL in volume_details:
            self.assertIsInstance(
                volume_details[constants.STORAGE_GROUP_ID_CAMEL], list)
        if volume_details[constants.HAS_EFFECTIVE_WWN]:
            self.assertIn(constants.EFFECTIVE_WWN, volume_details)
            self.assertIsInstance(
                volume_details[constants.EFFECTIVE_WWN], str)
        if constants.WWN in volume_details:
            self.assertIsInstance(volume_details[constants.WWN], str)
            self.assertIsNotNone(re.match(constants.WWN_SEARCH_PATTERN_32,
                                          volume_details[constants.WWN]))
            self.assertIsNotNone(
                re.match(constants.WWN_SEARCH_PATTERN_32,
                         volume_details[constants.EFFECTIVE_WWN]))

    def _validate_qos_specs(self, iops, mbps, distribution, qos_specs):
        """Validate return contents of qos specs requests.

        :param iops: host_io_limit_io_sec reference value -- str
        :param mbps: host_io_limit_mb_sec reference value -- str
        :param distribution: dynamic_distribution reference value -- str
        :param qos_specs: qos update result to validate -- dict
        """
        self.assertIsInstance(qos_specs, dict)
        self.assertIn(constants.HOST_IO_LIMIT_IO_SEC, qos_specs)
        self.assertIn(constants.HOST_IO_LIMIT_MB_SEC, qos_specs)
        self.assertIn(constants.DYNAMIC_DISTRIBUTION, qos_specs)
        self.assertIsInstance(qos_specs[constants.HOST_IO_LIMIT_IO_SEC], str)
        self.assertIsInstance(qos_specs[constants.HOST_IO_LIMIT_MB_SEC], str)
        self.assertIsInstance(qos_specs[constants.DYNAMIC_DISTRIBUTION], str)
        self.assertEqual(iops, qos_specs[constants.HOST_IO_LIMIT_IO_SEC])
        self.assertEqual(mbps, qos_specs[constants.HOST_IO_LIMIT_MB_SEC])
        self.assertEqual(
            distribution, qos_specs[constants.DYNAMIC_DISTRIBUTION])

    def _validate_effective_wwn_details(
            self, reference_details, actual_details):
        """Helper method for validating parsed effective wwn values.

        :param reference_details: volume details -- dict
        :param actual_details: parsed effective wwn details -- dict
        """
        self.assertIsInstance(actual_details, dict)
        self.assertIn(constants.VOLUME_ID, actual_details)
        self.assertIn(constants.WWN, actual_details)
        self.assertIn(constants.HAS_EFFECTIVE_WWN, actual_details)
        self.assertIn(constants.EFFECTIVE_WWN, actual_details)
        self.assertIn(constants.STORAGE_GROUP_ID, actual_details)
        self.assertEqual(
            reference_details[constants.VOLUME_ID_CAMEL],
            str(actual_details[constants.VOLUME_ID][0]))
        self.assertEqual(reference_details[constants.WWN],
                         str(actual_details[constants.WWN][0]))
        self.assertEqual(
            str(reference_details[constants.HAS_EFFECTIVE_WWN]),
            str(actual_details[constants.HAS_EFFECTIVE_WWN][0]))
        self.assertEqual(
            reference_details[constants.EFFECTIVE_WWN],
            str(actual_details[constants.EFFECTIVE_WWN][0]))
        if reference_details.get('num_of_storage_groups', 0) > 0:
            if constants.STORAGE_GROUP_ID_CAMEL in reference_details:
                storage_group_reference = reference_details[
                    constants.STORAGE_GROUP_ID_CAMEL]
            else:
                storage_group_reference = ''
            self.assertEqual(
                str(storage_group_reference),
                str(actual_details[constants.STORAGE_GROUP_ID][0]))

    def _validate_srp_details(self, srp_details):
        """Helper method for validating srp return details.

        :param srp_details: srp details -- dict
        """
        self._validate_srp_general(srp_details)
        self._validate_srp_check_capacity(srp_details)
        self._validate_srp_check_efficiency(srp_details)

    def _validate_srp_general(self, srp_details):
        """Helper method for validating srp return details.

        :param srp_details: srp details -- dict
        """
        self.assertIn(constants.SRP_ID, srp_details)
        self.assertIn(constants.NUM_OF_DISK_GROUPS, srp_details)
        self.assertIn(constants.EMULATION, srp_details)
        self.assertIn(constants.RESERVED_CAP_PERCENT, srp_details)
        self.assertIn(constants.TOTAL_SRDF_DSE_ALLOCATED_CAP_GB, srp_details)
        self.assertIn(constants.RDFA_DSE, srp_details)
        self.assertIn(constants.DISK_GROUP_ID, srp_details)
        self.assertIn(constants.SRP_CAPACITY, srp_details)
        self.assertIn(constants.SRP_CAPACITY, srp_details)
        self.assertIsInstance(srp_details[constants.SRP_ID], str)
        self.assertIsInstance(srp_details[constants.NUM_OF_DISK_GROUPS], int)
        self.assertIsInstance(srp_details[constants.EMULATION], str)
        self.assertIsInstance(
            srp_details[constants.RESERVED_CAP_PERCENT], int)
        self.assertIs(float, type(
            srp_details[constants.TOTAL_SRDF_DSE_ALLOCATED_CAP_GB]))
        self.assertIsInstance(srp_details[constants.RDFA_DSE], bool)
        self.assertIsInstance(srp_details[constants.DISK_GROUP_ID], list)

    def _validate_srp_check_capacity(self, srp_details):
        """Helper method for validating srp return details.

        :param srp_details: srp details -- dict
        """
        subscribed_allocated_tb = 'subscribed_allocated_tb'
        subscribed_total_tb = 'subscribed_total_tb'
        snapshot_modified_tb = 'snapshot_modified_tb'
        snapshot_total_tb = 'snapshot_total_tb'
        usable_used_tb = 'usable_used_tb'
        usable_total_tb = 'usable_total_tb'
        effective_used_capacity_percent = 'effective_used_capacity_percent'
        srp_capacity = srp_details[constants.SRP_CAPACITY]
        self.assertIsInstance(srp_capacity, dict)
        self.assertIn(subscribed_allocated_tb, srp_capacity)
        self.assertIn(subscribed_total_tb, srp_capacity)
        self.assertIn(snapshot_modified_tb, srp_capacity)
        self.assertIn(snapshot_total_tb, srp_capacity)
        self.assertIn(usable_used_tb, srp_capacity)
        self.assertIn(usable_total_tb, srp_capacity)
        self.assertIn(effective_used_capacity_percent, srp_capacity)
        self.assertIs(float, type(
            srp_capacity[subscribed_allocated_tb]))
        self.assertIsInstance(srp_capacity[subscribed_total_tb], float)
        self.assertIsInstance(srp_capacity[snapshot_modified_tb], float)
        self.assertIsInstance(srp_capacity[snapshot_total_tb], float)
        self.assertIsInstance(srp_capacity[usable_used_tb], float)
        self.assertIsInstance(srp_capacity[usable_total_tb], float)
        self.assertIs(int, type(
            srp_capacity[effective_used_capacity_percent]))

    def _validate_srp_check_efficiency(self, srp_details):
        """Helper method for validating srp return details.

        :param srp_details: srp details -- dict
        """
        compression_state = 'compression_state'
        data_reduction_enabled_percent = 'data_reduction_enabled_percent'
        overall_efficiency_ratio_to_one = 'overall_efficiency_ratio_to_one'
        data_reduction_ratio_to_one = 'data_reduction_ratio_to_one'
        virtual_provisioning_savings_ratio_to_one = (
            'virtual_provisioning_savings_ratio_to_one')
        snapshot_savings_ratio_to_one = 'snapshot_savings_ratio_to_one'
        srp_efficiency = srp_details[constants.SRP_EFFICIENCY]
        self.assertIsInstance(srp_efficiency, dict)
        self.assertIn(compression_state, srp_efficiency)
        self.assertIn(data_reduction_enabled_percent, srp_efficiency)
        self.assertIsInstance(srp_efficiency[compression_state], str)
        self.assertIs(float, type(
            srp_efficiency[data_reduction_enabled_percent]))
        if overall_efficiency_ratio_to_one in srp_efficiency:
            self.assertIs(float, type(
                srp_efficiency[overall_efficiency_ratio_to_one]))
        if data_reduction_ratio_to_one in srp_efficiency:
            self.assertIs(float, type(
                srp_efficiency[data_reduction_ratio_to_one]))
        if virtual_provisioning_savings_ratio_to_one in srp_efficiency:
            self.assertIs(float, type(
                srp_efficiency[
                    virtual_provisioning_savings_ratio_to_one]))
        if snapshot_savings_ratio_to_one in srp_efficiency:
            self.assertIs(float, type(
                srp_efficiency[
                    snapshot_savings_ratio_to_one]))

    def _validate_director_port(self, port_details):
        """Helper method for validating get director port return details.

        :param port_details: port details -- dict
        """
        symmetrix_port = 'symmetrixPort'
        port_interface = 'port_interface'
        port_status = 'port_status'
        director_status = 'director_status'
        num_of_hypers = 'num_of_hypers'
        max_speed = 'max_speed'
        self.assertIsInstance(port_details, dict)
        self.assertIn(symmetrix_port, port_details)
        port_details = port_details[symmetrix_port]
        symmetrix_port_key = port_details[constants.SYMMETRIX_PORT_KEY]
        self.assertIsInstance(symmetrix_port_key, dict)
        self.assertIn(constants.DIRECTOR_ID, symmetrix_port_key)
        self.assertIn(constants.PORT_ID, symmetrix_port_key)
        self.assertIsInstance(symmetrix_port_key[constants.PORT_ID], str)
        director_id = symmetrix_port_key[constants.DIRECTOR_ID]
        self.assertIsInstance(director_id, str)
        self.assertIsNotNone(
            re.match(constants.DIRECTOR_SEARCH_PATTERN, director_id))
        if port_interface in port_details:
            self.assertIsInstance(port_details[port_interface], str)
        if port_status in port_details:
            self.assertIsInstance(port_details[port_status], str)
        if director_status in port_details:
            self.assertIsInstance(port_details[director_status], str)
        if constants.TYPE in port_details:
            self.assertIsInstance(port_details[constants.TYPE], str)
        if constants.NUM_OF_CORES in port_details:
            self.assertIsInstance(port_details[constants.NUM_OF_CORES], int)
        if num_of_hypers in port_details:
            self.assertIsInstance(port_details[num_of_hypers], int)
        if max_speed in port_details:
            self.assertIsInstance(port_details[max_speed], str)

    def _validate_srp_demand_report(self, srp_report):
        """Helper method to validate SRP demand report contents.

        :param srp_report:  SRP demand report -- dict
        """
        self.assertIsInstance(srp_report, dict)
        self.assertIn(constants.STORAGE_GROUP_DEMAND, srp_report)
        self.assertIsInstance(
            srp_report[constants.STORAGE_GROUP_DEMAND], list)
        subscribed_gb = 'subscribed_gb'
        allocated_gb = 'allocated_gb'
        used_gb = 'used_gb'
        snapshot_allocated_gb = 'snapshot_allocated_gb'
        snapshot_used_gb = 'snapshot_used_gb'
        compression_ratio_to_one = 'compression_ratio_to_one'
        for report in srp_report[constants.STORAGE_GROUP_DEMAND]:
            self.assertIsInstance(report, dict)
            self.assertIn(constants.STORAGE_GROUP_ID_CAMEL, report)
            self.assertIn(constants.EMULATION, report)
            self.assertIn(subscribed_gb, report)
            self.assertIn(allocated_gb, report)
            self.assertIn(constants.ALLOCATED_PERCENT, report)
            self.assertIn(used_gb, report)
            self.assertIn(snapshot_allocated_gb, report)
            self.assertIn(snapshot_used_gb, report)
            self.assertIsInstance(
                report[constants.STORAGE_GROUP_ID_CAMEL], str)
            self.assertIsInstance(report[constants.EMULATION], str)
            self.assertIsInstance(report[subscribed_gb], float)
            self.assertIsInstance(report[allocated_gb], float)
            self.assertIsInstance(report[constants.ALLOCATED_PERCENT], int)
            self.assertIsInstance(report[used_gb], float)
            self.assertIsInstance(report[snapshot_allocated_gb], float)
            self.assertIsInstance(report[snapshot_used_gb], float)
            if compression_ratio_to_one in report:
                self.assertIs(
                    float, type(report[compression_ratio_to_one]))

    def _validiate_masking_view_connection(self, connection):
        """Helper method to validate masking view connection details.

        :param connection:  connection details -- dict
        """
        self.assertIsInstance(connection, dict)
        self.assertIn(constants.VOLUME_ID_CAMEL, connection)
        self.assertIn(constants.HOST_LUN_ADDRESS, connection)
        self.assertIn(constants.CAP_GB, connection)
        self.assertIn(constants.INITIATOR_ID, connection)
        self.assertIn(constants.ALIAS, connection)
        self.assertIn('dir_port', connection)
        self.assertIn(constants.LOGGED_IN, connection)
        self.assertIn(constants.ON_FABRIC, connection)

    def test_add_existing_volume_to_storage_group_srdf(self):
        """Test add_existing_volume_to_storage_group."""
        volume_name = self.generate_name()
        storage_group_name, srdf_group_number, local_volume, remote_volume = (
            self.create_rdf_sg())
        temp_storage_group_name = self.create_empty_storage_group()
        device_id = (
            self.provisioning.create_volume_from_storage_group_return_id(
                volume_name, temp_storage_group_name, '1'))
        time.sleep(10)
        self.provisioning.remove_volume_from_storage_group(
            storage_group_id=temp_storage_group_name, vol_id=device_id)
        self.provisioning.add_existing_volume_to_storage_group(
            storage_group_id=storage_group_name, vol_ids=device_id,
            remote_array_1_id=self.conn.remote_array,
            remote_array_1_sgs=storage_group_name)
        vol_list = self.provisioning.get_volumes_from_storage_group(
            storage_group_id=storage_group_name)
        self.provisioning.delete_storage_group(temp_storage_group_name)
        self.assertIn(device_id, vol_list)
        self.assertEqual(2, len(vol_list))
        vol_details = self.provisioning.get_volume(device_id)
        self.assertEqual('RDF1+TDEV', vol_details.get('type'))
