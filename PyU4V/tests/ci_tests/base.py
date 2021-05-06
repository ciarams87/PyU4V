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
"""base.py."""
import os
import random
import shutil
import string
import tempfile
import testtools
import time

from pathlib import Path

from PyU4V import univmax_conn
from PyU4V.utils import exception
from PyU4V.utils import performance_constants as pc


class TestBaseTestCase(testtools.TestCase):
    """Base test case class for all CI tests."""
    SRP = 'SRP_1'
    SLO = 'Diamond'

    def setUp(self):
        super(TestBaseTestCase, self).setUp()
        self.setup_credentials()
        self.provision = self.conn.provisioning
        self.replication = self.conn.replication
        self.common = self.conn.common
        self.snapshot_policy = self.conn.snapshot_policy
        self.metro_dr = self.conn.metro_dr
        self.migration = self.conn.migration
        self.perf = self.conn.performance

    def setup_credentials(self):
        """Set REST credentials."""
        self.conn = univmax_conn.U4VConn()
        self.assertTrue(self.conn.rest_client.headers.get('user-agent'))
        self.assertTrue(self.conn.rest_client.headers.get('application-type'))

    def create_volume(self):
        """Create a test volume.

        :returns: vol -- dict
        """
        sg_id, device_id = None, None
        vol = dict()
        try:
            sg_id = self.generate_name(object_type='sg')
            volume_name = self.generate_name()
            vol['volume_name'] = volume_name
            self.provision.create_empty_storage_group(
                self.SRP, sg_id, self.SLO, None)
            vol['storage_group'] = sg_id
            device_id = (
                self.provision.create_volume_from_storage_group_return_id(
                    volume_name, sg_id, '1', cap_unit='GB'))
            vol['device_id'] = device_id
            time.sleep(10)
            self.addCleanup(self.delete_volume, sg_id, device_id)
        except Exception:
            self.addCleanup(self.delete_volume, sg_id, device_id)
        return vol

    def find_volume(self, volume_name):
        """Find a volume and return it's device id.

        :param volume_name: volume name - - str
        :returns: device id - - str
        """
        return self.provision.find_volume_device_id(volume_name)

    def delete_volume(self, sg_name, device_id):
        """Delete a test volume.

        :param sg_name: storage group name - - str
        :param device_id: device id - - str
        """
        if sg_name:
            if device_id:
                vols = self.provision.get_volumes_from_storage_group(sg_name)
                if device_id in vols:
                    self.provision.remove_volume_from_storage_group(
                        sg_name, device_id)
            if self.provision.get_num_vols_in_storage_group(sg_name) == 0:
                self.provision.delete_storage_group(sg_name)
        if device_id:
            self.provision.delete_volume(device_id)

    # Replication Functions

    def create_sg_snapshot(self):
        """Create a test storage group snapshot.

        :returns: sg_ss -- dict
                  storage group name - - str
        """
        sg_name, vol, snap_name, sg_ss = None, None, None, None
        try:
            vol = self.create_volume()
            snap_name = self.generate_name(object_type='ss')
            if vol and 'storage_group' in vol:
                sg_name = vol['storage_group']
            sg_ss = self.replication.create_storage_group_snapshot(
                sg_name, snap_name, ttl=1, hours=True)
            self.addCleanup(
                self.delete_sg_snapshot, sg_name, snap_name)
        except Exception:
            if vol and 'storage_group' in vol:
                sg_name = vol['storage_group']
            self.addCleanup(
                self.delete_sg_snapshot, sg_name, snap_name)

        return sg_ss, sg_name

    def get_sg_snapshot(self, sg_name):
        """Get a storage group snapshot.

        :param sg_name: storage group name - - str
        :returns: snapvx name -- str
        """
        return self.replication.get_storage_group_snapshot_list(
            sg_name)[0]

    def delete_sg_snapshot(self, sg_name, snap_name):
        """Delete a test storage group snapshot.

        :param sg_name: storage group name - - str
        :param snap_name: snapvx name - - str
        """
        snap_id = self.replication.get_storage_group_snapshot_snap_id_list(
            sg_name, snap_name)[0]
        snap_details = self.replication.get_snapshot_snap_id_details(
            sg_name, snap_name, snap_id)
        if 'Restored' in snap_details.get('state'):
            try:
                self.replication.delete_storage_group_snapshot_by_snap_id(
                    sg_name, snap_name, snap_id)
            except Exception:
                pass
        self.replication.delete_storage_group_snapshot_by_snap_id(
            sg_name, snap_name, snap_id)

    def create_rdf_sg(self):
        """set up and tear down srdf pairings.

        :returns: sg_name -- str
                  device_id -- int
                  srdf_group_number -- int
                  remote_volume -- int
        """
        # Check remote array exists
        self.check_for_remote_array()

        # Generate SG name and create SG with one 1GB volume
        sg_name = self.generate_name(object_type='sg')
        vol_name = self.generate_name()
        srdf_group_number = None

        try:
            sg_create_success, sg_create_cnt = False, 0
            while not sg_create_success and sg_create_cnt <= 3:
                try:
                    sg_create_cnt += 1
                    storage_group = self.provision.create_storage_group(
                        self.SRP, sg_name, self.SLO, None, False, 1, 1, 'GB',
                        False, False, vol_name)
                    assert storage_group.get('storageGroupId') == sg_name
                    assert storage_group.get('num_of_vols') == 1
                    sg_create_success = True
                except (exception.VolumeBackendAPIException,
                        AssertionError) as error:
                    if sg_create_cnt == 3:
                        raise exception.VolumeBackendAPIException from error
                    else:
                        time.sleep(10)

            # Create SRDF pairing for SG and single volume
            srdf_pair_create_success, srdf_pair_create_cnt = False, 0
            while not srdf_pair_create_success and srdf_pair_create_cnt <= 3:
                try:
                    srdf_pair_create_cnt +=1
                    job = self.replication.create_storage_group_srdf_pairings(
                        storage_group_id=sg_name,
                        remote_sid=self.conn.remote_array,
                        srdf_mode='Synchronous', establish=True,
                        force_new_rdf_group=True, _async=True)
                    self.conn.common.wait_for_job_complete(job)
                    srdf_pair_info = (
                        self.replication.get_storage_group_replication_details(
                            storage_group_id=sg_name))
                    assert srdf_pair_info.get('rdf') is True
                    srdf_pair_create_success = True
                except (exception.VolumeBackendAPIException,
                        AssertionError) as error:
                    if srdf_pair_create_cnt == 3:
                        raise exception.VolumeBackendAPIException from error
                    else:
                        time.sleep(10)

            # Get the device ID of the volume in the local SG
            local_vol_list = self.provision.get_volumes_from_storage_group(
                sg_name)
            assert len(local_vol_list) == 1
            local_volume = local_vol_list[0]

            # Get the SRDF group number associated with our SG
            srdf_group_list = (
                self.replication.get_storage_group_srdf_group_list(sg_name))
            assert len(srdf_group_list) == 1
            srdf_group_number = srdf_group_list[0]

            # Get details of the remote volume
            remote_volume_details = self.replication.get_rdf_group_volume(
                rdf_number=srdf_group_number, device_id=local_volume)
            assert remote_volume_details
            remote_vol_id = remote_volume_details.get('remoteVolumeName')

        except Exception as error:
            raise Exception from error
        finally:
            self.addCleanup(self.cleanup_rdfg, sg_name, srdf_group_number)

        return sg_name, srdf_group_number, local_volume, remote_vol_id

    def check_for_remote_array(self):
        """Check for remote_array tag in configuration file."""
        if not self.conn.remote_array:
            self.skipTest("Skipping test because remote_array is not set")

    def cleanup_rdfg(self, sg_name, srdf_group_number):
        current_rdf_state_list = (
            self.replication.get_storage_group_srdf_details(
                storage_group_id=sg_name, rdfg_num=srdf_group_number).get(
                'states'))
        if 'Synchronized' or 'Consistent' in current_rdf_state_list:
            self.replication.suspend_storage_group_srdf(
                storage_group_id=sg_name, srdf_group_number=srdf_group_number)
        local_volume_list = self.provision.get_volumes_from_storage_group(
            sg_name)
        self.replication.delete_storage_group_srdf(
            storage_group_id=sg_name, srdf_group_number=srdf_group_number)
        self.provision.delete_storage_group(storage_group_id=sg_name)
        for local_volume in local_volume_list:
            self.provision.delete_volume(device_id=local_volume)
        self.conn.set_array_id(array_id=self.conn.remote_array)
        remote_volume_list = self.provision.get_volumes_from_storage_group(
            sg_name)
        self.provision.delete_storage_group(storage_group_id=sg_name)
        for remote_volume in remote_volume_list:
            self.provision.delete_volume(device_id=remote_volume)
        self.replication.delete_rdf_group(
            srdf_group_number=srdf_group_number)

    def get_online_rdf_ports(self):
        """Gets a list of all RDF ports online for local and remote array.

        :returns: list of online ports rdf ports
        """
        local_rdf_director_list = self.replication.get_rdf_director_list(
            filters={'online': True})
        local_online_rdf_ports = list()
        remote_online_rdf_ports = list()
        for director in local_rdf_director_list:
            local_rdf_director_port_list = (
                self.replication.get_rdf_director_port_list(
                    director_id=director, filters={'online': True}))
            for director_port in local_rdf_director_port_list:
                online_port = (director + ':' + director_port)
                local_online_rdf_ports.append(online_port)
        self.conn.set_array_id(self.conn.remote_array)
        remote_rdf_director_list = self.replication.get_rdf_director_list(
            filters={'online': True})
        for director in remote_rdf_director_list:
            remote_rdf_director_port_list = (
                self.replication.get_rdf_director_port_list(
                    director_id=director, array_id=self.conn.remote_array,
                    filters={'online': True}))
            for director_port in remote_rdf_director_port_list:
                online_port = (director + ':' + director_port)
                remote_online_rdf_ports.append(online_port)
        return local_online_rdf_ports, remote_online_rdf_ports

    def get_next_free_srdf_group(self):
        """Helper function to get RDFG on arrays that is free for use.

        :returns: next RDF group number on local and remote array
        """
        local_in_use_rdfg_list = self.replication.get_rdf_group_list(
            array_id=self.conn.array_id)
        remote_in_use_rdfg_list = self.replication.get_rdf_group_list(
            array_id=self.conn.remote_array)

        new_rdfg = 100
        local_list, remote_list = set(), set()
        rdfg_match = False

        for group in local_in_use_rdfg_list:
            local_list.add(group['rdfgNumber'])
        for group in remote_in_use_rdfg_list:
            remote_list.add(group['rdfgNumber'])

        while not rdfg_match and new_rdfg <= 250:
            if (new_rdfg not in local_list) and (new_rdfg not in remote_list):
                return new_rdfg
            new_rdfg += 1

        if not rdfg_match:
            raise exception.VolumeBackendAPIException(
                'There are no free RDFGs available on {arr1} and {arr2} from '
                '100 or higher that can both have the same number.'.format(
                    arr1=self.conn.array_id, arr2=self.conn.remote_array))

    def setup_srdf_group(self):
        local_array = self.conn.array_id
        local_port_list, remote_port_list = self.get_online_rdf_ports()
        srdf_group = self.get_next_free_srdf_group()
        self.conn.set_array_id(local_array)
        self.replication.create_rdf_group(
            local_director_port_list=local_port_list,
            remote_array_id=self.conn.remote_array,
            remote_director_port_list=remote_port_list,
            array_id=local_array, local_rdfg_number=srdf_group,
            remote_rdfg_number=srdf_group, label='pyu4v_' + str(srdf_group))
        return srdf_group, local_port_list, remote_port_list

    # noinspection PyMethodMayBeStatic
    def generate_name(self, object_type='v'):
        """Generate a random name of ascii characters or ints.

        :param object_type: v=volume, sg=storage group, ss=snapvx -- str
        :returns: random name -- str
        """
        vowels = 'aeiou'
        consonents = "".join(set(string.ascii_lowercase) - set(vowels))
        if object_type == 'sg':
            name = 'PyU4V-sg-'
        elif object_type == 'ss':
            name = 'PyU4V-ss-'
        elif object_type == 'host':
            name = 'PyU4V-host-'
        elif object_type == 'host_group':
            name = 'PyU4V-hg-'
        elif object_type == 'masking_view':
            name = 'PyU4V-mv-'
        elif object_type == 'port_group':
            name = 'PyU4V-pg-'
        elif object_type == 'service_level':
            name = 'PyU4V-slo-'
        elif object_type == 'sp':
            name = 'PyU4V-sp-'
        elif object_type == 'metro_dr':
            return 'PyU4V_' + str(random.randint(1, 999))
        else:
            name = 'PyU4V-vol-'
        for i in range(10):
            if i % 2 == 0:
                name += random.choice(consonents)
            else:
                name += random.choice(vowels)
        return name

    def create_temp_directory(self):
        """Create a temporary directory and add cleanup.

        :returns: path to directory -- str
        """
        os.umask(0o77)
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(self.cleanup_files, temp_dir=temp_dir)
        return temp_dir

    @staticmethod
    def cleanup_files(pyu4v_orig=None, temp_file=None, temp_dir=None):
        """Cleanup temporary files created/edited during CI tests.

        :param pyu4v_orig: path to PyU4V.conf and hidden copy -- tuple(str,str)
        :param temp_file: path to temporary file -- str
        :param temp_dir:  path to temporary directory -- str
        """
        # If pyu4v_orig is populated, rename hidden copy of PyU4V.conf to
        # original path, if hidden copy file still exists while original exists
        # delete it
        if pyu4v_orig:
            orig_conf = pyu4v_orig[0]
            hidden_conf = pyu4v_orig[1]
            if os.path.isfile(hidden_conf):
                if not os.path.isfile(orig_conf):
                    os.rename(hidden_conf, orig_conf)
                else:
                    os.remove(hidden_conf)
        # If temp_file is populated and file exists, delete the file at that
        # path
        if temp_file:
            if os.path.isfile(temp_file):
                os.remove(temp_file)
        # If temp_dir is populated and directory exists, delete the directory
        if temp_dir:
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)

    # Migration Functions
    def create_ci_migration_environment(self):
        """Create a migration environment between two arrays.

        :returns: migration environment details -- dict
        """
        array_list = self.conn.common.get_array_list()
        array_list.remove(self.conn.array_id)
        existing_envs = self.migration.get_environment_list()
        if existing_envs:
            for array in existing_envs:
                array_list.remove(array)
        migration_env = dict()
        for array in array_list:
            try:
                migration_env = self.migration.create_migration_environment(
                    array)
                if migration_env and 'message' not in migration_env:
                    break
            except Exception:
                pass
        return migration_env

    def create_host(self, initiator_list=None, host_flags=None,
                    init_file=None, _async=False):
        """Create a host with given initiators.

        :param initiator_list: list of initiators -- list
        :param host_flags: dictionary of optional host flags to apply -- dict
        :param init_file: path to file that contains initiator names -- str
        :param _async: Flag to indicate if call should be _async -- bool
        :returns: new host name -- str
        """
        host_name = self.generate_name('host')
        host_details = self.provision.create_host(
            host_name, initiator_list, host_flags, init_file, _async)
        self.addCleanup(self.delete_host, host_name)
        if _async:
            self.conn.common.wait_for_job_complete(host_details)
        return host_name

    def create_empty_host(self, host_flags=None):
        """Create an empty host with no initiators.

        :param host_flags: dictionary of optional host flags to apply -- dict
        :returns: new host name -- str
        """
        host_name = self.generate_name('host')
        self.provision.create_host(host_name, host_flags=host_flags)
        self.addCleanup(self.delete_host, host_name)
        return host_name

    def modify_host(self):
        """Modify a test host.

        :returns: new host name -- str
        """
        new_host_name, host_name = None, None
        try:
            host_name = self.generate_name(object_type='host')
            self.provision.create_host(host_name)
            new_host_name = self.generate_name(object_type='host')
            self.provision.modify_host(host_name, new_name=new_host_name)
            self.addCleanup(self.delete_host, new_host_name)
            return host_name
        except Exception:
            delete_host = host_name
            if self.get_host_id(new_host_name) == new_host_name:
                delete_host = new_host_name
            self.addCleanup(self.delete_host, delete_host)

    def get_host_id(self, host_name):
        """Get a host id"""
        try:
            host_details = self.provision.get_host(host_name)
            host_id = host_details['hostId']
        except Exception:
            host_id = None
        return host_id

    def delete_host(self, host_name):
        """Delete a host.

        :param host_name: name of host to be delete -- str
        """
        host_list = self.provision.get_host_list()
        if host_name in host_list:
            self.provision.delete_host(host_name)

    def create_host_group(self, host_flags=None, _async=None):
        """Create a host group.

        :param host_flags: dictionary of optional host flags to apply -- dict
        :param _async: Flag to indicate if call should be _async -- bool
        :returns: new host group name -- str
        """
        host_name = self.create_empty_host(host_flags)
        host_group_name = self.generate_name('host_group')
        host_group_details = self.provision.create_host_group(
            host_group_name, [host_name], host_flags, _async)
        self.addCleanup(self.delete_host_group, host_group_name)
        if _async:
            self.conn.common.wait_for_job_complete(host_group_details)
        return host_group_name

    def delete_host_group(self, host_group_name):
        """Delete a host group.

        :param host_group_name: name of host group to delete
        """
        host_group_list = self.provision.get_host_group_list()
        if host_group_name in host_group_list:
            self.provision.delete_host(host_group_name)

    def create_empty_storage_group(self):
        """Create a storage group.

        :returns: new storage group name -- str
        """
        srp_list = self.provision.get_srp_list()
        srp = None
        if srp_list:
            srp1 = 'SRP_1'
            srp = srp1 if srp1 in srp_list else srp_list[0]
        service_level_list = self.provision.get_service_level_list()
        service_level = None
        if service_level_list:
            service_level = service_level_list[0]
        storage_group_name = self.generate_name('sg')
        self.provision.create_empty_storage_group(
            srp, storage_group_name, service_level, None)
        self.addCleanup(self.delete_storage_group, storage_group_name)
        return storage_group_name

    def delete_storage_group(self, storage_group):
        """Delete a storage group.

        :param storage_group: name of storage group to delete
        """
        storage_groups = self.provision.get_storage_group_list()
        if storage_group in storage_groups:
            self.provision.delete_storage_group(storage_group)

    def create_port_group(self, number_of_ports=1):
        """Create a port group.

        :param number_of_ports: minimum port count to add -- int
        :returns: new port group details -- tuple
        """
        directors = self.provision.get_director_list()
        fa_directors = list()
        for d in directors:
            if 'FA-' in d:
                fa_directors.append(d)

        selected_director_ports = list()
        for director in fa_directors:
            if len(selected_director_ports) < number_of_ports:
                ports = self.provision.get_director_port_list(
                    director, filters='aclx=true')
                # avoid GOS ports
                ports = [p for p in ports if int(p['portId']) < 30]
                selected_director_ports.append(ports[0])

        port_group_name = self.generate_name('port-group')
        if number_of_ports == 1:
            director = selected_director_ports[0]['directorId']
            port = selected_director_ports[0]['portId']
            port_group_details = self.provision.create_port_group(
                port_group_name, director, port)
        else:
            port_group_details = (
                self.provision.create_multiport_port_group(
                    port_group_name, selected_director_ports))

        self.addCleanup(self.delete_port_group, port_group_name)
        return port_group_name, port_group_details

    def delete_port_group(self, port_group_name):
        """Delete a port group.

        :param port_group_name: port group to delete
        """
        port_group_list = self.provision.get_port_group_list()
        if port_group_name in port_group_list:
            self.provision.delete_port_group(port_group_name)

    def create_masking_view(self, use_host_group=False, _async=False):
        """Create a new masking view.

        :param use_host_group: create view using host group -- bool
        :param _async: call the create command asynchronously -- bool
        :returns: masking view details -- dict
        """
        masking_view_name = self.generate_name('masking_view')
        port_group_name, _ = self.create_port_group()
        storage_group_name = self.create_empty_storage_group()
        device = (
            self.provision.create_volume_from_storage_group_return_id(
                self.generate_name(), storage_group_name, 1))
        self.addCleanup(self.delete_volume, storage_group_name, device)
        if not use_host_group:
            host_name = self.create_empty_host()
            masking_view_details = (
                self.provision.
                create_masking_view_existing_components(
                    port_group_name, masking_view_name, storage_group_name,
                    host_name, _async=_async))
        else:
            host_group_name = self.create_host_group()
            masking_view_details = (
                self.provision.
                create_masking_view_existing_components(
                    port_group_name, masking_view_name, storage_group_name,
                    host_group_name=host_group_name, _async=_async))
        self.addCleanup(self.delete_masking_view, masking_view_name)
        if _async:
            self.conn.common.wait_for_job_complete(masking_view_details)
        return masking_view_name, masking_view_details

    def delete_masking_view(self, masking_view_name):
        """Delete a masking view.

        :param masking_view_name: masking view to delete
        """
        masking_view_list = self.provision.get_masking_view_list()
        if masking_view_name in masking_view_list:
            self.provision.delete_masking_view(masking_view_name)

    # Performance Functions
    def run_performance_test_asserts(self, category, id_tag, key_func,
                                     metrics_func):
        """Given a performance category, run get keys and stats tests.

        :param category: performance category -- str
        :param id_tag: the corresponding ID tag used in calls -- str
        :param key_func: the get keys function -- func
        :param metrics_func: the get metrics function -- func
        """
        keys = None
        try:
            keys = key_func()
            if not keys:
                raise exception.ResourceNotFoundException()
        except exception.ResourceNotFoundException:
            self.skipTest(
                '{cat} is not enabled or there are no provisioned assets of '
                'this kind.'.format(cat=category))
        for key in keys:
            self.assertIn(id_tag, key.keys())
            self.assertIn(pc.FA_DATE, key.keys())
            self.assertIn(pc.LA_DATE, key.keys())
        metric_list = self.perf.get_performance_metrics_list(category)
        dead_metrics = list()
        asset_id = keys[0].get(id_tag)
        if category == pc.ISCSI_TGT:
            id_tag = pc.ISCSI_TGT_ID_METRICS
        for metric in metric_list:
            try:
                metrics = metrics_func(asset_id, metric)
                self.assertTrue(metrics)
                self.assertIsInstance(metrics, dict)
                self.assertEqual(metrics.get(pc.ARRAY_ID), self.conn.array_id)
                self.assertEqual(
                    metrics.get(self.common.convert_to_snake_case(id_tag)),
                    asset_id)
                self.assertEqual(self.common.convert_to_snake_case(category),
                                 metrics.get(pc.REP_LEVEL))
                perf_results = metrics.get(pc.RESULT)[0]
                self.assertIn(metric, perf_results.keys())
            except exception.VolumeBackendAPIException:
                dead_metrics.append(metric)
        self.assertFalse(dead_metrics)

    def run_extended_input_performance_test_asserts(
            self, category, outer_tag, inner_tag, outer_keys_func,
            inner_key_func, inner_metrics_func):
        """Test backend emulation performance function for director ports.

        :param category: performance category -- str
        :param outer_tag: tag required for dir key extraction -- str
        :param inner_tag: tag required for port key extraction -- str
        :param outer_keys_func: method for obtaining dir keys -- func
        :param inner_key_func: method for obtaining port keys -- func
        :param inner_metrics_func: method for obtaining port metrics -- func
        """
        outer_keys, inner_keys = None, None
        outer_id, inner_id = None, None
        try:
            outer_keys = outer_keys_func()
            outer_id = outer_keys[0].get(outer_tag)
            inner_keys = inner_key_func(outer_id)
            inner_id = inner_keys[0].get(inner_tag)
        except (exception.VolumeBackendAPIException,
                exception.ResourceNotFoundException) as e:
            self.skipTest(e.msg)

        self.assertTrue(inner_keys)
        for time_key in inner_keys:
            self.assertIn(inner_tag, time_key.keys())
            self.assertIn(pc.FA_DATE, time_key.keys())
            self.assertIn(pc.LA_DATE, time_key.keys())

        # Test get_backend_port_stats.
        metric_list = self.perf.get_performance_metrics_list(category)
        dead_metrics = list()
        for metric in metric_list:
            try:
                metrics = inner_metrics_func(
                    outer_id, inner_id, metric)
                self.assertTrue(metrics)
                self.assertIsInstance(metrics, dict)
                self.assertEqual(metrics.get(pc.ARRAY_ID), self.conn.array_id)
                self.assertEqual(
                    metrics.get(self.common.convert_to_snake_case(outer_tag)),
                    outer_id)
                self.assertEqual(
                    metrics.get(self.common.convert_to_snake_case(inner_tag)),
                    inner_id)
                perf_results = metrics.get(pc.RESULT)[0]
                self.assertIn(metric, perf_results.keys())
            except exception.VolumeBackendAPIException:
                dead_metrics.append(metric)
        self.assertFalse(dead_metrics)

    def create_snapshot_policy(self):
        snapshot_policy_name = self.generate_name(object_type='sp')
        snapshot_policy_interval = '10 Minutes'

        self.snapshot_policy.create_snapshot_policy(
            snapshot_policy_name, snapshot_policy_interval,
            local_snapshot_policy_snapshot_count=30)

        snapshot_policy_details = (
            self.snapshot_policy.get_snapshot_policy(snapshot_policy_name))
        self.addCleanup(self.delete_snapshot_policy, snapshot_policy_name)
        return snapshot_policy_details.get(
            'snapshot_policy_name') if snapshot_policy_details else None

    def delete_snapshot_policy(self, snapshot_policy_name):
        self.snapshot_policy.delete_snapshot_policy(snapshot_policy_name)

    # Metro DR Functions
    def setup_metro_dr(self):
        """Setup a Metro DR Environment.

        :returns: sg_name, environment_name --str
        """
        environment_name = self.generate_name(object_type='metro_dr')
        metro_r1_array_id = self.conn.array_id
        metro_r2_array_id = self.conn.remote_array
        dr_array_id = self.conn.remote_array_2
        sg_name = self.generate_name(object_type='sg')
        self.provision.create_non_empty_storage_group(
            storage_group_id=sg_name, service_level='Diamond',
            num_vols=1, vol_size=1, cap_unit='GB', srp_id='SRP_1',
            workload=None)
        job = self.metro_dr.create_metrodr_environment(
            storage_group_name=sg_name, environment_name=environment_name,
            metro_r1_array_id=metro_r1_array_id,
            metro_r2_array_id=metro_r2_array_id, dr_array_id=dr_array_id,
            dr_replication_mode='adaptivecopydisk')
        self.common.wait_for_job_complete(job=job)
        self.addCleanup(self.cleanup_metro_dr, sg_name, environment_name)

        return sg_name, environment_name

    def cleanup_metro_dr(self, sg_name, environment_name):
        """Cleanup Metro DR created SG and Environments."""
        # Sleep added to give time to synchronize
        time.sleep(180)

        # Instantiate array cleanup dict
        cleanup_details = {self.conn.array_id: list(),
                           self.conn.remote_array: list(),
                           self.conn.remote_array_2: list()}
        # Get the RDFGs associated with the SG on each metro DR array
        for array in cleanup_details.keys():
            sg_rdf_list = self.replication.get_storage_group_srdf_group_list(
                sg_name, array_id=array)
            cleanup_details[array] = sg_rdf_list

        # Delete metro DR environment
        self.metro_dr.delete_metrodr_environment(
            environment_name=environment_name)

        # Suspend RDF and delete RDF pairs
        for rdfg in cleanup_details.get(self.conn.array_id):
            self.replication.suspend_storage_group_srdf(
                storage_group_id=sg_name, srdf_group_number=rdfg)
            self.replication.delete_storage_group_srdf(
                storage_group_id=sg_name, srdf_group_number=rdfg)

        # For each array in the metro DR env..
        for array in cleanup_details.keys():
            # Set the array ID
            self.conn.set_array_id(array_id=array)
            # Get a list of volumes in target SG
            volume_list = (self.provision.get_volumes_from_storage_group(
                sg_name))
            # Delete the SG
            self.provision.delete_storage_group(storage_group_id=sg_name)
            # Delete each volume from old SG
            for volume in volume_list:
                self.provision.delete_volume(volume)
            # Delete each RDFGs associated with the source SG
            for rdfg in cleanup_details.get(array):
                try:
                    self.replication.delete_rdf_group(rdfg)
                except exception.ResourceNotFoundException:
                    pass

    @staticmethod
    def cleanup_pyu4v_zip_files_in_directory(directory):
        """Cleanup PyU4V zip archives in a given directory.

        :param directory: path to directory -- str
        """
        assert Path(directory).is_dir() is True
        p = Path(directory).glob('PyU4V-*.zip')
        files = [x for x in p if x.is_file()]
        for file in files:
            file.unlink()
