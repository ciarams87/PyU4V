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
"""test_pyu4v_replication.py."""

import testtools

from unittest import mock

from PyU4V import common
from PyU4V import replication
from PyU4V import rest_requests
from PyU4V.tests.unit_tests import pyu4v_common_data as pcd
from PyU4V.tests.unit_tests import pyu4v_fakes as pf
from PyU4V import univmax_conn
from PyU4V.utils import exception


class PyU4VReplicationTest(testtools.TestCase):
    """Test replication."""

    def setUp(self):
        """Setup."""
        super(PyU4VReplicationTest, self).setUp()
        self.data = pcd.CommonData()
        self.conf_file, self.conf_dir = (
            pf.FakeConfigFile.create_fake_config_file())
        univmax_conn.file_path = self.conf_file
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=pf.FakeRequestsSession()):
            self.conn = univmax_conn.U4VConn(array_id=self.data.array)
            self.provisioning = self.conn.provisioning
            self.replication = self.conn.replication

    def tearDown(self):
        """tearDown."""
        super(PyU4VReplicationTest, self).tearDown()
        pf.FakeConfigFile.delete_fake_config_file(
            self.conf_file, self.conf_dir)

    def test_get_replication_info(self):
        """Test get_replication_info."""
        rep_info = self.replication.get_replication_info()
        self.assertEqual(self.data.rep_info, rep_info)

    def test_check_snap_capabilities(self):
        """Test get_array_replication_capabilities."""
        capabilities = self.replication.get_array_replication_capabilities(
            array_id=self.data.array)
        self.assertEqual(
            self.data.capabilities['symmetrixCapability'][1], capabilities)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.no_capabilities)
    def test_check_no_snap_capabilities(self, mck_get):
        """Test get_array_replication_capabilities."""
        no_capabilities = self.replication.get_array_replication_capabilities()
        self.assertEqual(no_capabilities,
                         self.data.no_capabilities['symmetrixCapability'][1])

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=list())
    def test_check_snap_cabilitities_no_response(self, mck_get):
        capabilities = (
            self.replication.get_array_replication_capabilities())
        self.assertEqual(capabilities, dict())
        self.assertFalse(capabilities)

    def test_is_snapvx_licensed(self):
        """Test is_snapvx_licensed."""
        is_licensed = self.replication.is_snapvx_licensed()
        self.assertTrue(is_licensed)

    @mock.patch.object(replication.ReplicationFunctions,
                       'get_array_replication_capabilities', return_value=None)
    def test_is_snapvx_licensed_exception(self, mck_get):
        """Test is_snapvx_licensed."""
        is_licensed = self.replication.is_snapvx_licensed()
        self.assertFalse(is_licensed)

    def test_get_storage_group_rep(self):
        """Test get_storage_group_rep."""
        rep_details = self.replication.get_storage_group_rep(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_details_rep[0], rep_details)

    def test_get_storage_group_rep_list(self):
        """Test get_storage_group_rep_list sgs with snapshots."""
        with mock.patch.object(self.replication, 'get_resource') as mock_mod:
            self.replication.get_storage_group_rep_list(has_snapshots=True)
            mock_mod.assert_called_once_with(
                category='replication', resource_level='symmetrix',
                resource_level_id=self.data.array,
                resource_type='storagegroup', params={'hasSnapshots': 'true'})

    def test_get_srdf_storage_group_rep_list(self):
        """Test get_storage_group_rep_list."""
        with mock.patch.object(self.replication, 'get_resource') as mock_mod:
            self.replication.get_storage_group_rep_list(
                has_srdf=True, has_snapshots=True)
            mock_mod.assert_called_once_with(
                category='replication', resource_level='symmetrix',
                resource_level_id=self.data.array,
                resource_type='storagegroup', params={'hasSrdf': 'true',
                                                      'hasSnapshots': 'true'})

    def test_get_sg_with_snap_srdf_storage_group_rep_list(self):
        """Test get_storage_group_rep_list."""
        with mock.patch.object(self.replication, 'get_resource') as mock_mod:
            self.replication.get_storage_group_rep_list(has_srdf=True)
            mock_mod.assert_called_once_with(
                category='replication', resource_level='symmetrix',
                resource_level_id=self.data.array,
                resource_type='storagegroup', params={'hasSrdf': 'true'})

    def test_get_storagegroup_snapshot_list(self):
        """Test get_storagegroup_snapshot_list."""
        snap_list = self.replication.get_storagegroup_snapshot_list(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_snap_list['name'], snap_list)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=list())
    def test_get_storage_group_snapshot_empty_list(self, mck_get):
        """Test get_storagegroup_snapshot_list."""
        snap_list = self.replication.get_storagegroup_snapshot_list(
            self.data.storagegroup_name)
        self.assertEqual(snap_list, list())

    def test_create_storage_group_snap(self):
        """Test create_storagegroup_snap."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_storagegroup_snap(
                self.data.storagegroup_name, 'snap_name')
            self.replication.create_storagegroup_snap(
                self.data.storagegroup_name, 'snap_name', ttl=2, hours=True)
            self.assertEqual(2, mock_create.call_count)

    def test_create_storage_group_snapshot_secure(self):
        """Test create_storage_group_snapshot."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_storage_group_snapshot(
                self.data.storagegroup_name, 'snap_name')
            self.replication.create_storage_group_snapshot(
                self.data.storagegroup_name, 'snap_name', ttl=2, hours=True,
                secure=True)
            self.assertEqual(2, mock_create.call_count)

    def test_get_storagegroup_snapshot_generation_list(self):
        """Test get_storagegroup_snapshot_generation_list."""
        gen_list = self.replication.get_storagegroup_snapshot_generation_list(
            self.data.storagegroup_name, 'snap_name')
        self.assertEqual(self.data.sg_snap_gen_list['generations'], gen_list)

    def test_get_storage_group_snapshot_snap_id_list(self):
        """Test get_storage_group_snapshot_snap_id_list."""
        snap_id_list = (
            self.replication.get_storage_group_snapshot_snap_id_list(
                self.data.storagegroup_name, 'snap_name'))
        self.assertEqual(self.data.sg_snap_id_list['snapids'], snap_id_list)

    def test_get_snapshot_generation_details(self):
        """Test get_snapshot_generation_details."""
        snap_details = self.replication.get_snapshot_generation_details(
            self.data.storagegroup_name, self.data.group_snapshot_name, 0)
        self.assertEqual(self.data.group_snap_vx, snap_details)

    def test_get_snapshot_snap_id_details(self):
        """Test get_snapshot_snap_id_details."""
        snap_details = self.replication.get_snapshot_snap_id_details(
            self.data.storagegroup_name, self.data.group_snapshot_name,
            self.data.sg_snap_id)
        self.assertEqual(self.data.group_snap_vx, snap_details)

    @mock.patch.object(replication.ReplicationFunctions,
                       'get_snapshot_generation_details',
                       return_value=pcd.CommonData.expired_snap)
    @mock.patch.object(replication.ReplicationFunctions,
                       'get_storage_group_snapshot_generation_list',
                       return_value=pcd.CommonData.sg_snap_gen_list)
    def test_find_expired_snapvx_snapshots(self, mock_gen_list, mock_snap):
        """Test find_expired_snapvx_snapshots."""
        expired_snap_list = (
            self.replication.find_expired_snapvx_snapshots())
        self.assertIsInstance(expired_snap_list, list)

    @mock.patch.object(replication.ReplicationFunctions,
                       'get_snapshot_generation_details',
                       return_value=pcd.CommonData.non_expired_snap)
    @mock.patch.object(replication.ReplicationFunctions,
                       'get_storage_group_snapshot_generation_list',
                       return_value=pcd.CommonData.sg_snap_gen_list)
    def test_find_expired_snapvx_snapshots_not_expired(
            self, mock_gen_list, mock_snap):
        """Test find_expired_snapvx_snapshots."""
        expired_snap_list = (
            self.replication.find_expired_snapvx_snapshots())
        self.assertIsInstance(expired_snap_list, list)
        self.assertFalse(expired_snap_list)

    @mock.patch.object(replication.ReplicationFunctions,
                       'get_snapshot_snap_id_details',
                       return_value=pcd.CommonData.expired_snap_id)
    @mock.patch.object(replication.ReplicationFunctions,
                       'get_storage_group_snapshot_snap_id_list',
                       return_value=pcd.CommonData.sg_snap_id_list)
    def test_find_expired_snapvx_snapshots_by_snap_id(
            self, mock_gen_list, mock_snap):
        """Test find_expired_snapvx_snapshots by snap id."""
        expired_snap_list = (
            self.replication.find_expired_snapvx_snapshots_by_snap_ids())
        self.assertIsInstance(expired_snap_list, list)
        self.assertTrue(expired_snap_list)

    @mock.patch.object(replication.ReplicationFunctions,
                       'get_snapshot_snap_id_details',
                       return_value=pcd.CommonData.non_expired_snap_id)
    @mock.patch.object(replication.ReplicationFunctions,
                       'get_storage_group_snapshot_snap_id_list',
                       return_value=pcd.CommonData.sg_snap_id_list)
    def test_find_expired_snapvx_snapshots_by_snap_id_not_expired(
            self, mock_gen_list, mock_snap):
        """Test find_expired_snapvx_snapshots by snap id."""
        expired_snap_list = (
            self.replication.find_expired_snapvx_snapshots_by_snap_ids())
        self.assertIsInstance(expired_snap_list, list)
        self.assertFalse(expired_snap_list)

    def test_modify_storagegroup_snap(self):
        """Test modify_storagegroup_snap."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.modify_storage_group_snapshot(
                self.data.storagegroup_name,
                self.data.target_group_name, self.data.group_snapshot_name,
                restore=True)
            mock_mod.assert_called_once_with(
                category='replication', object_type='generation',
                object_type_id='0', payload=self.data.snap_restore_payload,
                resource='snapshot', resource_id='Grp_snapshot',
                resource_level='symmetrix', resource_level_id=self.data.array,
                resource_type='storagegroup',
                resource_type_id='PU-mystoragegroup-SG')

    def test_modify_storage_group_snap_by_snap_id(self):
        """Test modify_storage_group_snapshot_by_snap_id."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.modify_storage_group_snapshot_by_snap_id(
                self.data.storagegroup_name,
                self.data.target_group_name, self.data.group_snapshot_name,
                self.data.sg_snap_id, restore=True)
            mock_mod.assert_called_once_with(
                category='replication', object_type='snapid',
                object_type_id=self.data.sg_snap_id,
                payload=self.data.snap_restore_payload,
                resource='snapshot', resource_id='Grp_snapshot',
                resource_level='symmetrix', resource_level_id=self.data.array,
                resource_type='storagegroup',
                resource_type_id='PU-mystoragegroup-SG')

    def test_rename_snapshot(self):
        """Test rename_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.rename_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                'new-snap-name')
            mock_mod.assert_called_once()

    def test_rename_snapshot_by_snap_id(self):
        """Test rename_snapshot_by_snap_id."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.rename_snapshot_by_snap_id(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                'new-snap-name', self.data.sg_snap_id)
            mock_mod.assert_called_once()

    def test_restore_snapshot(self):
        """Test rename_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.restore_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                0)
            mock_mod.assert_called_once()

    def test_restore_snapshot_by_snap_id(self):
        """Test restore_snapshot_by_snap_id."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.restore_snapshot_by_snap_id(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                self.data.sg_snap_id)
            mock_mod.assert_called_once()

    def test_link_gen_snapshot(self):
        """Test link_gen_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.link_gen_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                self.data.target_group_name, _async=True)
            mock_mod.assert_called_once()

    def test_link_snapshot_by_snap_id(self):
        """Test link_snapshot_by_snap_id."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.link_snapshot_by_snap_id(
                self.data.storagegroup_name, self.data.target_group_name,
                self.data.group_snapshot_name, self.data.sg_snap_id,
                _async=True)
            mock_mod.assert_called_once()

    def test_relink_snapshot_by_snap_id(self):
        """Test relink_snapshot_by_snap_id."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.modify_storage_group_snapshot_by_snap_id(
                self.data.storagegroup_name, self.data.target_group_name,
                self.data.group_snapshot_name, self.data.sg_snap_id,
                relink=True)
            mock_mod.assert_called_once()

    def test_unlink_gen_snapshot(self):
        """Test unlink_gen_snapshot."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.unlink_gen_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                self.data.target_group_name, _async=True)
            mock_mod.assert_called_once()

    def test_unlink_snapshot_by_snap_id(self):
        """Test unlink_snapshot_by_snap_id."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.unlink_snapshot_by_snap_id(
                self.data.storagegroup_name, self.data.target_group_name,
                self.data.group_snapshot_name, self.data.sg_snap_id,
                _async=True)
            mock_mod.assert_called_once()

    def test_delete_storagegroup_snapshot(self):
        """Test delete_storagegroup_snapshot."""
        with mock.patch.object(
                self.replication, 'delete_resource') as mock_delete:
            self.replication.delete_storagegroup_snapshot(
                self.data.storagegroup_name, self.data.group_snapshot_name)
            mock_delete.assert_called_once()

    def test_delete_storage_group_snapshot_by_snap_id(self):
        """Test delete_storage_group_snapshot_by_snap_id."""
        with mock.patch.object(
                self.replication, 'delete_resource') as mock_delete:
            self.replication.delete_storage_group_snapshot_by_snap_id(
                self.data.storagegroup_name, self.data.group_snapshot_name,
                self.data.sg_snap_id)
            mock_delete.assert_called_once()

    @mock.patch('builtins.input', return_value='1')
    @mock.patch.object(replication.ReplicationFunctions,
                       'get_storagegroup_snapshot_list',
                       return_value=['snap-1', 'snap-2', 'snap-3'])
    def test_choose_snapshot_from_list_in_console(self, mck_snap_list,
                                                  mck_choice):
        """Test choose_snapshot_from_list_in_console."""
        output = self.replication.choose_snapshot_from_list_in_console(
            self.data.storagegroup_name)
        self.assertEqual('snap-2', output)

    def test_is_vol_in_rep_session(self):
        """Test is_vol_in_rep_session."""
        snap_tgt, snap_src, rdf_grp = (
            self.replication.is_volume_in_replication_session(
                self.data.device_id))
        self.assertTrue(snap_src)
        self.assertEqual(self.data.rdf_group_num_91, rdf_grp)
        self.assertTrue(snap_tgt)

    @mock.patch.object(replication.ReplicationFunctions,
                       'is_volume_in_replication_session',
                       return_value=pcd.CommonData.device_id)
    def test_is_vol_in_rep_session_84(self, mck):
        self.replication.is_vol_in_rep_session(pcd.CommonData.device_id)
        mck.assert_called_once()

    def test_get_rdf_group(self):
        """Test get_rdf_group."""
        rdfg_details = self.replication.get_rdf_group(self.data.rdf_group_no)
        self.assertEqual(self.data.rdf_group_details, rdfg_details)

    def test_get_rdf_group_list(self):
        """Test get_rdf_group_list."""
        rdfg_list = self.replication.get_rdf_group_list()
        self.assertEqual(self.data.rdf_group_list['rdfGroupID'], rdfg_list)

    def test_get_rdf_group_volume(self):
        """Test get_rdf_group_volume."""
        rdfg_vol = self.replication.get_rdf_group_volume(
            self.data.rdf_group_no, self.data.device_id)
        self.assertEqual(self.data.rdf_group_vol_details, rdfg_vol)

    def test_get_rdf_group_volume_list(self):
        """Test get_rdf_group_volume_list."""
        rdfg_vol_list = self.replication.get_rdf_group_volume_list(
            self.data.rdf_group_no)
        self.assertEqual(self.data.rdf_group_vol_list['name'], rdfg_vol_list)

    def test_are_volumes_rdf_paired(self):
        """Test are_vols_rdf_paired."""
        paired, _, _ = self.replication.are_volumes_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id2, self.data.rdf_group_no)
        self.assertTrue(paired)
        paired2, _, _ = self.replication.are_volumes_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id3, self.data.rdf_group_no)
        self.assertFalse(paired2)
        paired3, _, _ = self.replication.are_volumes_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id4, self.data.rdf_group_no)
        self.assertFalse(paired3)

    def test_are_vols_rdf_paired(self):
        """Test are_vols_rdf_paired."""
        paired, _, _ = self.replication.are_vols_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id2, self.data.rdf_group_no)
        self.assertTrue(paired)
        paired2, _, _ = self.replication.are_vols_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id3, self.data.rdf_group_no)
        self.assertFalse(paired2)
        paired3, _, _ = self.replication.are_vols_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id4, self.data.rdf_group_no)
        self.assertFalse(paired3)

    @mock.patch.object(replication.ReplicationFunctions,
                       'get_rdf_group_volume',
                       return_value=None)
    def test_are_volumes_not_rdf_paired(self, mck):
        """Test are_vols_rdf_paired."""
        self.replication.are_volumes_rdf_paired(
            self.data.remote_array, self.data.device_id,
            self.data.device_id2, self.data.rdf_group_no)
        mck.assert_called_once()

    @mock.patch.object(replication.ReplicationFunctions, 'get_rdf_group',
                       return_value=None)
    def test_get_rdf_group_number(self, mck_get):
        """Test get_rdf_group_number."""
        rdfn = self.replication.get_rdf_group_number(
            self.data.rdf_group_name_91)
        self.assertIsNone(rdfn)

    def test_get_storagegroup_srdfg_list(self):
        """Test get_storagegroup_srdfg_list."""
        rdfg_list = self.replication.get_storagegroup_srdfg_list(
            self.data.storagegroup_name)
        self.assertEqual(self.data.sg_rdf_list['rdfgs'], rdfg_list)

    def test_get_storagegroup_srdf_details(self):
        """Test get_storagegroup_srdf_details."""
        sg_rdf_details = self.replication.get_storagegroup_srdf_details(
            self.data.storagegroup_name, self.data.rdf_group_no)
        self.assertEqual(self.data.sg_rdf_details[0], sg_rdf_details)

    @mock.patch.object(replication.ReplicationFunctions,
                       'create_storagegroup_srdf_pairings',
                       return_value=dict)
    def test_create_storagegroup_srdf_pairings(self, mck):
        """Test create_storagegroup_srdf_pairings."""
        self.replication.create_storagegroup_srdf_pairings(
            self.data.storagegroup_name, self.data.remote_array, 'Synchronous')
        mck.assert_called_once()

    @mock.patch.object(replication.ReplicationFunctions,
                       'create_storagegroup_srdf_pairings',
                       return_value=dict)
    def test_create_storagegroup_metro_pairings(self, mck):
        """Test create_storagegroup_srdf_pairings with Active input."""
        self.replication.create_storagegroup_srdf_pairings(
            self.data.storagegroup_name, self.data.remote_array, 'Active',
            True, True, self.data.rdf_group_no)
        mck.assert_called_once_with(
            self.data.storagegroup_name, self.data.remote_array, 'Active',
            True, True, self.data.rdf_group_no)

    def test_create_storagegroup_srdf_pairings_newrdfg(self):
        """Test create_storagegroup_srdf_pairings."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_storagegroup_srdf_pairings(
                self.data.storagegroup_name, self.data.remote_array, 'Active')
            mock_create.assert_called_once()
            mock_create.reset_mock()
            self.replication.create_storagegroup_srdf_pairings(
                self.data.storagegroup_name, self.data.remote_array, 'Active',
                True, True, self.data.rdf_group_no, True)
            mock_create.assert_called_once()

    def test_modify_storagegroup_srdf(self):
        """Test test_modify_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            # Lowercase action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'suspend', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()
            # Uppercase action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'SUSPEND', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()
            # Correct case action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'SetMode', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()
            # Mixed case action
            self.replication.modify_storagegroup_srdf(
                self.data.storagegroup_name, 'sEtBIAs', self.data.rdf_group_no,
                options=None, _async=False)
            mock_mod.assert_called_once()
            mock_mod.reset_mock()

        # Invalid action passed, exception raised
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.replication.modify_storagegroup_srdf,
                          self.data.storagegroup_name, 'None',
                          self.data.rdf_group_no,)

    def test_suspend_storagegroup_srdf(self):
        """Test suspend_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.suspend_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no,
                suspend_options={'consExempt': 'true'}, _async=True)
            mock_mod.assert_called_once()

    def test_establish_storagegroup_srdf(self):
        """Test establish_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.establish_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no,
                establish_options={'full': 'true'}, _async=True)
            mock_mod.assert_called_once()

    def test_failover_storagegroup_srdf(self):
        """Test failover_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.failover_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no)
            mock_mod.assert_called_once()

    def test_failback_storagegroup_srdf(self):
        """Test failback_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.failback_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no)
            mock_mod.assert_called_once()

    def test_delete_storagegroup_srdf(self):
        """Test delete_storagegroup_srdf."""
        with mock.patch.object(
                self.replication, 'delete_resource') as mock_delete:
            self.replication.delete_storagegroup_srdf(
                self.data.storagegroup_name, self.data.rdf_group_no)
            mock_delete.assert_called_once_with(
                category='replication', resource_level='symmetrix',
                resource_level_id=self.data.array,
                resource_type='storagegroup',
                resource_type_id=self.data.storagegroup_name,
                resource='rdf_group', resource_id=self.data.rdf_group_no,
                params=None)

    def test_create_rdf_group(self):
        """Test create_rdf_group."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_rdf_group(
                local_director_port_list=self.data.local_rdf_ports,
                local_rdfg_number=1,
                remote_array_id=self.data.remote_array, remote_rdfg_number=1,
                remote_director_port_list=self.data.remote_rdf_ports,
                label='test')
            mock_create.assert_called_once()

    def test_modify_rdf_group_remove_port(self):
        """Test modify_rdf_group removing an RDF port."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.modify_rdf_group(
                action='remove_ports', srdf_group_number=1,
                port_list=['RF-1E:1'])
            mock_mod.assert_called_once()

    def test_modify_rdf_group_add_port(self):
        """Test modify_rdf_group adding an RDF port."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.modify_rdf_group(
                action='remove_ports', srdf_group_number=1,
                port_list=['RF-1E:1'])
            mock_mod.assert_called_once()

    def test_modify_rdf_group_set_label(self):
        """Test modify_rdf_group changing label."""
        with mock.patch.object(
                self.replication, 'modify_resource') as mock_mod:
            self.replication.modify_rdf_group(
                action='set_label', srdf_group_number=1,
                label='new_label')
            mock_mod.assert_called_once()

    def test_modify_rdf_group_raise_error_no_action(self):
        """Test modify_rdf_group no action for error."""
        self.assertRaises(
            exception.VolumeBackendAPIException,
            self.replication.modify_rdf_group, action='badaction',
            srdf_group_number=1, label='new_label')

    def test_modify_rdf_group_raise_error_consistency_exempt(self):
        """Test modify_rdf_group raise consistency error."""
        self.assertRaises(
            exception.VolumeBackendAPIException,
            self.replication.modify_rdf_group, action='Move',
            srdf_group_number=1, label='new_label')

    def test_modify_rdf_group_raise_error_no_ports(self):
        """Test modify_rdf_group raise no port error."""
        self.assertRaises(
            exception.InvalidInputException,
            self.replication.modify_rdf_group, action='add_ports',
            srdf_group_number=1, label='new_label')

    def test_delete_rdf_group(self):
        """Test delete_rdf_group."""
        with mock.patch.object(
                self.replication, 'delete_resource') as mock_delete:
            self.replication.delete_rdf_group(srdf_group_number=1)
            mock_delete.assert_called_once()

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.remote_port_details)
    def test_get_rdf_port_remote_connections(self, mck_get):
        """Test get_rdf_port_remote_connections."""
        remote_port_details = self.replication.get_rdf_port_remote_connections(
            director_id='RF-1D', port_id=4)
        self.assertEqual(pcd.CommonData.remote_port_details,
                         remote_port_details)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.rdf_dir_port_detail)
    def test_get_rdf_director_port_details(self, mck_get):
        """Test get_rdf_director_port_details."""
        rdf_dir_port_details = self.replication.get_rdf_director_port_details(
            director_id='RF-1', port_id='4')
        self.assertEqual(pcd.CommonData.rdf_dir_port_detail,
                         rdf_dir_port_details)

    def test_get_rdf_director_port_list(self):
        """Test get_rdf_director_port_list."""
        rdf_dir_ports = self.replication.get_rdf_director_port_list(
            director_id="RF-1F")
        self.assertIsInstance(rdf_dir_ports, list)

    def test_get_rdf_director_list(self):
        """Test get_rdf_director_list."""
        rdf_dir_list = self.replication.get_rdf_director_list()
        self.assertIsInstance(rdf_dir_list, list)

    @mock.patch.object(common.CommonFunctions, 'get_request',
                       return_value=pcd.CommonData.rdf_dir_detail)
    def test_get_rdf_director_detail(self, mck_get):
        """Test get_rdf_director_detail."""
        rdf_detail = self.replication.get_rdf_director_detail(
            director_id='RF-1F')
        self.assertEqual(self.data.rdf_dir_detail, rdf_detail)

    def test_create_storage_group_from_rdfg(self):
        """Test create_storage_group_from_rdfg."""
        with mock.patch.object(
                self.replication, 'create_resource') as mock_create:
            self.replication.create_storage_group_from_rdfg(
                storage_group_name=self.data.storagegroup_name,
                srdf_group_number=1,
                rdf_type='RDF1',
                remote_storage_group_name=self.data.storagegroup_name)
            mock_create.assert_called_once()
