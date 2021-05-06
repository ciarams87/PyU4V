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
"""pyu4v_common_data.py."""


class CommonData(object):
    """Common array data."""
    U4P_VERSION = '92'

    array = '000197800123'
    remote_array = '000197800124'
    remote_array2 = '000197800125'
    srp = 'SRP_1'
    slo = 'Diamond'
    workload = 'DSS'
    port_group_name_f = 'PU-fibre-PG'
    port_group_name_i = 'PU-iscsi-PG'
    masking_view_name_f = 'PU-HostX-F-MV'
    masking_view_name_i = 'PU-HostX-I-MV'
    initiatorgroup_name_f = 'PU-HostX-F-IG'
    initiatorgroup_name_i = 'PU-HostX-I-IG'
    hostgroup_id = 'PU-HostGroup-F-HG'
    storagegroup_name = 'PU-mystoragegroup-SG'
    failed_resource = 'PU-failed-resource'
    volume_wwn = '600000345'
    device_id = '00001'
    device_id2 = '00002'
    device_id3 = '00003'
    device_id4 = '00004'
    rdf_group_name = 'Group1'
    rdf_group_name_91 = 'Group1'
    rdf_group_num_91 = 1
    rdf_group_no = '70'
    u4v_version = '92'
    parent_sg = 'PU-HostX-SG'
    storagegroup_name_1 = 'PU-mystoragegroup1-SG'
    storagegroup_name_2 = 'PU-mystoragegroup2-SG'
    group_snapshot_name = 'Grp_snapshot'
    target_group_name = 'Grp_target'
    qos_storagegroup = 'PU-QOS-SG'
    snapshot_name = 'snap_01234'
    sg_snap_id = 118749976833

    # director port info
    director_id1 = 'FA-1D'
    port_id1 = '4'
    director_id2 = 'SE-4E'
    port_id2 = '0'
    port_key1 = {'directorId': director_id1, 'portId': port_id1}
    port_key2 = {'directorId': director_id2, 'portId': port_id2}

    # Connector info
    wwpn1 = '123456789012345'
    wwpn2 = '123456789054321'
    wwnn1 = '223456789012345'
    initiator = 'iqn.1993-08.org.debian: 01: 222'
    initiator2 = 'iqn.1993-08.com.emc: 01: 222'
    ip, ip2 = u'123.4.56.78', u'123.45.67.89'
    ipv6 = u'2001:1:22:333:4444:dbfa:a7f7:8000'
    iqn = u'iqn.1992-04.com.emc:600009700bca30c01e3e012e00000001,t,0x0001'
    iqn2 = u'iqn.1992-04.com.emc:600009700bca30c01e3e012e00000002,t,0x0001'

    # PowerMax data
    # SLO provisioning
    compression_info = {'symmetrixId': ['000197800128']}
    director_info = {'directorId': director_id1,
                     'num_of_cores': 7,
                     'director_slot_number': 1,
                     'availability': 'Online',
                     'num_of_ports': 5}
    director_list = {'directorId': [director_id1, director_id2]}
    host_list = {'hostId': [initiatorgroup_name_f, initiatorgroup_name_i]}
    initiatorgroup = [{'initiator': [wwpn1],
                       'hostId': initiatorgroup_name_f,
                       'maskingview': [masking_view_name_f]},
                      {'initiator': [initiator],
                       'hostId': initiatorgroup_name_i,
                       'maskingview': [masking_view_name_i]}]

    hostgroup = {'num_of_hosts': 1,
                 'num_of_initiators': 4,
                 'num_of_masking_views': 1,
                 'host': [initiatorgroup[0]],
                 'type': 'Fibre',
                 'hostGroupId': hostgroup_id,
                 'maskingview': [masking_view_name_f]}

    hostgroup_list = {'hostGroupId': [hostgroup_id]}

    initiator_list = [{'host': initiatorgroup_name_f,
                       'initiatorId': wwpn1,
                       'maskingview': [masking_view_name_f]},
                      {'host': initiatorgroup_name_i,
                       'initiatorId': initiator,
                       'maskingview': [masking_view_name_i]},
                      {'initiatorId': [
                          'FA-1D:4:' + wwpn1,
                          'SE-4E:0:' + initiator]}]

    maskingview = [{'maskingViewId': masking_view_name_f,
                    'portGroupId': port_group_name_f,
                    'storageGroupId': storagegroup_name,
                    'hostId': initiatorgroup_name_f,
                    'maskingViewConnection': [
                        {'host_lun_address': '0003'}]},
                   {'maskingViewId': masking_view_name_i,
                    'portGroupId': port_group_name_i,
                    'storageGroupId': storagegroup_name_1,
                    'hostId': initiatorgroup_name_i,
                    'maskingViewConnection': [
                        {'host_lun_address': '0003'}]},
                   {'maskingViewId': [masking_view_name_f,
                                      masking_view_name_i]}]

    portgroup = [{'portGroupId': port_group_name_f,
                  'symmetrixPortKey': [
                      {'directorId': director_id1,
                       'portId': 'FA-1D:4'}],
                  'maskingview': [masking_view_name_f]},
                 {'portGroupId': port_group_name_i,
                  'symmetrixPortKey': [
                      {'directorId': director_id2,
                       'portId': 'SE-4E:0'}],
                  'maskingview': [masking_view_name_i]}]

    pg_list = {'portGroupId': [port_group_name_i, port_group_name_f]}

    port_key_list = {'symmetrixPortKey': [port_key1, port_key2]}

    port_list = [
        {'symmetrixPort': {'num_of_masking_views': 1,
                           'maskingview': [masking_view_name_f],
                           'identifier': wwnn1,
                           'symmetrixPortKey': port_key1,
                           'portgroup': [port_group_name_f]}},
        {'symmetrixPort': {'identifier': initiator,
                           'symmetrixPortKey': port_key2,
                           'ip_addresses': [ip],
                           'num_of_masking_views': 1,
                           'maskingview': [masking_view_name_i],
                           'portgroup': [port_group_name_i]}}]
    port_details = {
        'symmetrixPort': {
            'director_status': 'Online',
            'no_participating': False,
            'num_of_cores': 7,
            'aclx': True,
            'environ_set': False,
            'num_of_mapped_vols': 0,
            'iscsi_target': False,
            'num_of_masking_views': 0,
            'wwn_node': '5000097398027004',
            'enable_auto_negotiate': True,
            'type': 'FibreChannel (563)',
            'avoid_reset_broadcast': False,
            'disable_q_reset_on_ua': False,
            'sunapee': False,
            'port_status': 'PendOn',
            'init_point_to_point': True,
            'volume_set_addressing': False,
            'vnx_attached': False,
            'scsi_support1': True,
            'hp_3000_mode': False,
            'identifier': '5000097398027005',
            'symmetrixPortKey': {
                'directorId': 'FA-1D',
                'portId': '5'
            },
            'max_speed': '16',
            'negotiate_reset': False,
            'spc2_protocol_version': True,
            'unique_wwn': True,
            'siemens': False,
            'num_of_port_groups': 0,
            'common_serial_number': True,
            'scsi_3': True,
            'soft_reset': False
        }
    }
    sg_details = [{'srp': srp,
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': storagegroup_name,
                   'slo': slo,
                   'workload': workload},
                  {'srp': srp,
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': storagegroup_name_1,
                   'slo': slo,
                   'workload': workload,
                   'maskingview': [masking_view_name_f],
                   'parent_storage_group': [parent_sg]},
                  {'srp': srp,
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': storagegroup_name_2,
                   'slo': slo,
                   'workload': workload,
                   'maskingview': [masking_view_name_i]},
                  {'srp': 'None',
                   'num_of_vols': 2,
                   'cap_gb': 2,
                   'storageGroupId': parent_sg,
                   'child_storage_group': [storagegroup_name_1],
                   'maskingview': [masking_view_name_f]},
                  {'srp': srp, 'num_of_vols': 2, 'cap_gb': 2,
                   'storageGroupId': qos_storagegroup,
                   'slo': slo, 'workload': workload,
                   'hostIOLimit': {'host_io_limit_io_sec': '4000',
                                   'dynamicDistribution': 'Always',
                                   'host_io_limit_mb_sec': '4000'}}]

    sg_details_rep = [{'childNames': list(),
                       'numDevicesNonGk': 2,
                       'isLinkTarget': False,
                       'rdf': True,
                       'capacityGB': 2.0,
                       'name': storagegroup_name,
                       'snapVXSnapshots': [group_snapshot_name],
                       'symmetrixId': array,
                       'numSnapVXSnapshots': 1}]

    sg_expand_payload_multi_site = {
        'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addSpecificVolumeParam': {
                    'volumeId': [
                        '00123'
                    ],
                    'remoteSymmSGInfoParam': {
                        'remote_symmetrix_2_id': remote_array2,
                        'remote_symmetrix_1_id': remote_array,
                        'remote_symmetrix_1_sgs': [
                            storagegroup_name
                        ],
                        'remote_symmetrix_2_sgs': [
                            storagegroup_name
                        ]}}}}}

    sg_expand_payload_basic_srdf = {
        'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addSpecificVolumeParam': {
                    'volumeId': [
                        '00123'
                    ],
                    'remoteSymmSGInfoParam': {
                        'remote_symmetrix_1_id': remote_array,
                        'remote_symmetrix_1_sgs': [
                            storagegroup_name
                        ]}}}}}

    sg_details_migration = [{'targetArray': remote_array,
                             'sourceArray': array,
                             'totalCapacity': 8.0,
                             'targetMaskingView': [masking_view_name_f],
                             'state': 'Synchronized',
                             'sourceMaskingView': [masking_view_name_i],
                             'remainingCapacity': 0.0,
                             'devicePairs': [{
                                 'invalidSrc': False,
                                 'srcVolumeName': 'my-vol',
                                 'invalidTgt': False,
                                 'tgtVolumeName': 'my-vol2',
                                 'missingSrc': False,
                                 'missingTgt': False}],
                             'storageGroup': storagegroup_name}]

    sg_rdf_details = [{'storageGroupName': storagegroup_name,
                       'symmetrixId': array,
                       'modes': ['Synchronous'],
                       'rdfGroupNumber': rdf_group_no,
                       'states': ['Synchronized']}]

    sg_list = {'storageGroupId': [storagegroup_name,
                                  storagegroup_name_1,
                                  storagegroup_name_2]}

    sg_list_rep = {'name': [storagegroup_name]}
    sg_rdf_list = {'rdfgs': [rdf_group_no]}

    sg_list_migration = {'name': sg_list['storageGroupId'],
                         'migratingName': [storagegroup_name]}

    srp_details = {'srpSloDemandId': ['Bronze', 'Diamond', 'Gold',
                                      'None', 'Optimized', 'Silver'],
                   'srpId': srp,
                   'total_used_cap_gb': 5244.7,
                   'total_usable_cap_gb': 20514.4,
                   'total_subscribed_cap_gb': 84970.1,
                   'fba_used_capacity': 5244.7,
                   'reserved_cap_percent': 10}

    srp_list = {'srpId': [srp, 'SRP_2']}

    compr_report = {'storageGroupCompressibility': [
        {'num_of_volumes': 6, 'storageGroupId': storagegroup_name,
         'allocated_cap_gb': 0.0, 'used_cap_gb': 0.0,
         'compression_enabled': 'false'}, ]}

    volume_details = [{'cap_gb': 2,
                       'num_of_storage_groups': 1,
                       'volumeId': device_id,
                       'volume_identifier': 'my-vol',
                       'wwn': volume_wwn,
                       'snapvx_target': 'false',
                       'snapvx_source': 'false',
                       'storageGroupId': [storagegroup_name],
                       'allocated_percent': 5,
                       'rdfGroupId': 1},
                      {'cap_gb': 1,
                       'num_of_storage_groups': 1,
                       'volumeId': device_id2,
                       'wwn': '600012345',
                       'storageGroupId': [storagegroup_name_1],
                       'allocated_percent': 5},
                      {'cap_gb': 1,
                       'num_of_storage_groups': 0,
                       'volumeId': device_id3,
                       'volume_identifier': 'my-vol3',
                       'wwn': '600012345',
                       'allocated_percent': 50}]

    volume_list = [
        {'resultList': {'result': [{'volumeId': device_id}]}},
        {'resultList': {'result': [{'volumeId': device_id2}]}},
        {'expirationTime': 1517830955979, 'count': 2, 'maxPageSize': 1000,
         'id': '123', 'resultList': {'result': [{'volumeId': device_id},
                                                {'volumeId': device_id2}]}}]

    workloadtype = {'workloadId': ['OLTP', 'OLTP_REP', 'DSS', 'DSS_REP']}
    slo_list = {'sloId': ['Bronze', 'Diamond', 'Gold',
                          'Optimized', 'Platinum', 'Silver']}
    slo_details = {'sloBaseId': slo, 'num_of_workloads': 5, 'sloId': slo,
                   'num_of_storage_groups': 1230,
                   'workloadId': workloadtype['workloadId'],
                   'storageGroupId': [storagegroup_name,
                                      storagegroup_name_1,
                                      storagegroup_name_2]}

    array_slo_details = {
        'default_fba_srp': srp,
        'symmetrixId': array,
        'system_capacity': {
            'usable_total_tb': 61.12, 'subscribed_total_tb': 149.99,
            'subscribed_allocated_tb': 3.73, 'snapshot_total_tb': 1492.07,
            'subscribed_usable_capacity_percent': 246.0,
            'usable_used_tb': 6.24, 'snapshot_modified_tb': 0.0},
        'physicalCapacity': {
            'used_capacity_gb': 76290.38, 'total_capacity_gb': 76290.38},
        'host_visible_device_count': 6848,
        'system_efficiency': {
            'overall_efficiency_ratio_to_one': 445.1,
            'virtual_provisioning_savings_ratio_to_one': 40.6,
            'data_reduction_enabled_percent': 0.0,
            'pattern_detection_savings_tb': 0.0,
            'drr_on_reducible_only_to_one': 0.0,
            'snapshot_savings_ratio_to_one': 1.14096688E7,
            'deduplication_and_compression_savings_tb': 0.0,
            'unreducible_data_tb': 0.0, 'reducible_data_tb': 0.0},
        'sloCompliance': {
            'slo_marginal': 0, 'no_slo': 157, 'slo_stable': 251,
            'slo_critical': 9},
        'meta_data_usage': {
            'backend_meta_data_used_percent': 47.0,
            'replication_cache_used_percent': 0,
            'system_meta_data_used_percent': 34.0,
            'frontend_meta_data_used_percent': 13.0},
        'model': 'PowerMax_2000',
        'ucode': '5978.669.669',
        'device_count': 7168,
        'local': True}

    # replication
    capabilities = {'symmetrixCapability': [{'rdfCapable': True,
                                             'snapVxCapable': True,
                                             'symmetrixId': '0001111111'},
                                            {'symmetrixId': array,
                                             'snapVxCapable': True,
                                             'rdfCapable': True}]}

    no_capabilities = {'symmetrixCapability': [{'rdfCapable': False,
                                                'snapVxCapable': False,
                                                'symmetrixId': '0001111111'},
                                               {'symmetrixId': array,
                                                'snapVxCapable': False,
                                                'rdfCapable': False}]}

    snap_restore_payload = {'action': 'Restore'}

    group_snap_vx = {'generation': 0,
                     'snapid': sg_snap_id,
                     'isLinked': False,
                     'numUniqueTracks': 0,
                     'isRestored': False,
                     'name': group_snapshot_name,
                     'numStorageGroupVolumes': 1,
                     'state': ['Established'],
                     'timeToLiveExpiryDate': 'N/A',
                     'isExpired': False,
                     'numSharedTracks': 0,
                     'timestamp': '00:30:50 Fri, 02 Jun 2017 IST +0100',
                     'numSourceVolumes': 1}
    expired_snap = (
        {'generation': 0,
         'isLinked': True,
         'name': group_snapshot_name,
         'numStorageGroupVolumes': 1,
         'state': ['Established'],
         'timeToLiveExpiryDate': '01:30:50 Fri, 02 Jun 2017 IST ',
         'isExpired': True,
         'linkedStorageGroup': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2017 IST +0100',
         'numSourceVolumes': 1})
    non_expired_snap = (
        {'generation': 0,
         'isLinked': True,
         'name': group_snapshot_name,
         'numStorageGroupVolumes': 1,
         'state': ['Established'],
         'timeToLiveExpiryDate': '01:30:50 Fri, 02 Jun 2017 IST ',
         'isExpired': False,
         'linkedStorageGroup': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2017 IST +0100',
         'numSourceVolumes': 1})
    expired_snap_id = (
        {'generation': 0,
         'snapid': 118749976834,
         'linked': True,
         'name': group_snapshot_name,
         'num_storage_group_volumes': 1,
         'state': ['Established'],
         'time_to_live_expiry_date': '01:30:50 Fri, 02 Jun 2020 IST ',
         'expired': True,
         'linked_storage_group': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2020 IST +0100',
         'num_source_volumes': 1})
    non_expired_snap_id = (
        {'generation': 0,
         'snapid': 118749976834,
         'linked': True,
         'name': group_snapshot_name,
         'num_storage_group_volumes': 1,
         'state': ['Established'],
         'time_to_live_expiry_date': '01:30:50 Fri, 02 Jun 2020 IST ',
         'isExpired': False,
         'linked_storage_group': [{'name': target_group_name}],
         'timestamp': '00:30:50 Fri, 02 Jun 2020 IST +0100',
         'num_source_volumes': 1})

    sg_snap_list = {'name': [group_snapshot_name]}
    sg_snap_gen_list = {'generations': [0]}
    sg_snap_id_list = {'snapids': [sg_snap_id]}

    rdf_group_list_91 = [{'rdfgNumber': 1, 'label': 'Group1'},
                         {'rdfgNumber': 2, 'label': 'Group2'},
                         {'rdfgNumber': 3, 'label': 'Group3'},
                         {'rdfgNumber': 4, 'label': 'Group4'}]

    rdf_group_list = {'rdfGroupID': [{'rdfgNumber': rdf_group_no,
                                      'label': rdf_group_name}]}

    rdf_group_details = {'modes': ['Synchronous'],
                         'remoteSymmetrix': remote_array,
                         'label': rdf_group_name,
                         'type': 'Dynamic',
                         'numDevices': 1,
                         'remoteRdfgNumber': rdf_group_no,
                         'rdfgNumber': rdf_group_no}
    rdf_group_vol_details = {'remoteRdfGroupNumber': rdf_group_no,
                             'localSymmetrixId': array,
                             'volumeConfig': 'RDF1+TDEV',
                             'localRdfGroupNumber': rdf_group_no,
                             'localVolumeName': device_id,
                             'rdfpairState': 'Synchronized',
                             'remoteVolumeName': device_id2,
                             'localVolumeState': 'Ready',
                             'rdfMode': 'Synchronous',
                             'remoteVolumeState': 'Write Disabled',
                             'remoteSymmetrixId': remote_array}
    rdf_group_vol_list = {'name': [device_id, device_id2]}

    rep_info = {'symmetrixId': array, 'storageGroupCount': 1486,
                'replicationCacheUsage': 0, 'rdfGroupCount': 7}

    local_rdf_ports = ['RF-1E:8', 'RF-2E:8']

    remote_rdf_ports = ['RF-1E:8', 'RF-2E:8']

    rdf_ports = [4, 5]

    rdf_director_list = ['RF-1F', 'RF-2F']

    rdf_dir_detail = {
        'gige': False,
        'symmetrixID': '000197600156',
        'fiber': True,
        'directorNumber': 81,
        'directorId': 'RF-1F',
        'hwCompressionSupported': True,
        'online': True
    }

    rdf_dir_port_detail = {
        'symmetrixID': '000197600156',
        'directorNumber': 81,
        'directorId': 'RF-1F',
        'online': True,
        'portNumber': 4,
        'wwn': '5000097398027004'
    }

    remote_port_details = {
        'remotePort': [
            {
                'symmetrixID': '000197900111',
                'directorNumber': 81,
                'directorId': 'RF-1F',
                'online': True,
                'portNumber': 4,
                'wwn': '50000973B001BC04'
            }
        ]
    }

    # migration
    migration_info = {'symmetrixId': array, 'storageGroupCount': 1486,
                      'local': True, 'migrationSessionCount': 10}
    migration_capabilities = {'storageArrayCapability': [{
        'srdfsTarget': True,
        'dmSource': True,
        'srdfsSource': True,
        'dmTarget': True,
        'compression': True,
        'arrayId': array}]}
    migration_environment_list = {'arrayId': [array]}
    migration_environment_details = {'symmetrixId': array,
                                     'otherSymmetrixId': remote_array,
                                     'invalid': False,
                                     'state': 'OK'}

    # system
    job_list = [{'status': 'SUCCEEDED',
                 'jobId': '12345',
                 'result': 'created',
                 'resourceLink': 'storagegroup/%s' % storagegroup_name},
                {'status': 'RUNNING', 'jobId': '55555'},
                {'status': 'FAILED', 'jobId': '09999'}]
    symmetrix = [{'symmetrixId': array,
                  'model': 'VMAX250F',
                  'ucode': '5977.1091.1092'}]
    symm_list = {'symmetrixId': [array, remote_array]}
    server_version = {'version': 'V9.2.0.0'}
    alert_list = {'alertId': ['15a15a58-26a0-4127-9e63-00ca162df789',
                  '2d9e481b-552a-4a33-a586-4bb1d11605c5']}
    alert_id = '15a15a58-26a0-4127-9e63-00ca162df789'
    alert_details = {'alertId': '15a15a58-26a0-4127-9e63-00ca162df789',
                     'state': 'NEW',
                     'severity': 'NORMAL',
                     'type': 'ARRAY',
                     'array': '000197900111',
                     'object': 'RF-1F:5',
                     'object_type': 'Port',
                     'created_date': 'Mar-19-2020 11:51:56.000',
                     'created_date_milliseconds': 1584618716000,
                     'description': 'Port state has changed to Online. '
                                    '- Object is: 000197900111:RF-1F:5',
                     'acknowledged': False}
    alert_summary = {'serverAlertSummary': {
        'alert_count': 0, 'all_unacknowledged_count': 0,
        'fatal_unacknowledged_count': 0,
        'critical_unacknowledged_count': 0,
        'warning_unacknowledged_count': 0,
        'info_unacknowledged_count': 0,
        'minor_unacknowledged_count': 0,
        'normal_unacknowledged_count': 0,
        'all_acknowledged_count': 0,
        'fatal_acknowledged_count': 0,
        'critical_acknowledged_count': 0,
        'warning_acknowledged_count': 0,
        'info_acknowledged_count': 0,
        'minor_acknowledged_count': 0,
        'normal_acknowledged_count': 0},
        'symmAlertSummary': list()}

    ip_interface_address = '192.168.0.3'
    ip_interface_address_network = '192.168.0.3-9'
    ip_interface_list = {'ipInterfaceId': [ip_interface_address_network]}
    ip_interface_details = {
        'ip_interface_id': ip_interface_address_network, 'network_id': 9,
        'ip_prefix_length': 24, 'vlan_id': 0, 'mtu': 1500,
        'iscsi_target_director': director_id2, 'iscsi_target_port': 0,
        'ip_address': ip_interface_address}

    # wlp
    wlp_info = {'symmetrixId': array, 'lastProcessed': 1569417000000,
                'nextUpdate': 795}
    headroom_array = {'gbHeadroom': [{'srpId': 'SRP_TEST', 'emulation': 'FBA',
                                      'capacity': 58555.9}]}
    wlp_capabilities = {'symmetrixCapability': [
        {'symmetrixId': array, 'workloadDetailCapable': True,
         'componentUtilizationCapable': True, 'characterizationCapable': True,
         'headroomGbCapable': True, 'suitabilityTestCapable': True,
         'provisioningTemplateCapable': True, 'slComplianceCapable': True,
         'headroomIopsCapable': True},
        {'symmetrixId': remote_array, 'workloadDetailCapable': True,
         'componentUtilizationCapable': True,
         'characterizationCapable': True,
         'headroomGbCapable': True, 'suitabilityTestCapable': True,
         'provisioningTemplateCapable': True, 'slComplianceCapable': True,
         'headroomIopsCapable': True}]}

    # iterator
    iterator_page = {'result': [{'volumeId': '00002'}], 'from': 2, 'to': 2}

    vol_with_pages = {'expirationTime': 1572358809878, 'count': 6,
                      'maxPageSize': 5, 'from': 1, 'to': 1,
                      'id': '0edbcf48-65f0-4271-999b-22412c457cd5_0',
                      'resultList': {'result': [{'volumeId': '00001'}]}}

    # Health
    array_health = {
        'num_failed_disks': 0, 'health_score_metric': [{
            'cached_date': 1573660846922, 'expired': False,
            'metric': 'SERVICE_LEVEL_COMPLIANCE',
            'instance_metrics': [{
                'health_score': 95.0, 'data_date': 1573660846922,
                'health_score_instance_metric': [{
                    'severity': 'Critical',
                    'instance_name': 'Storage Group Py1 is out of compliance',
                    'metric_name': 'Service Level Health Score',
                    'health_score_reduction': 5.0,
                    'metric_category': 'SG'}]}]}]}

    array_health_check_list = {'health_check_id': ['1573664112128']}

    perform_health_check_response = {
        'jobId': '1573664112132', 'name': 'CI-Test', 'status': 'RUNNING',
        'username': 'test', 'last_modified_date': 'Nov-13-2019 16:55:12.133',
        'last_modified_date_milliseconds': 1573664112133,
        'completed_date_milliseconds': 0, 'task': [{
            'execution_order': 1, 'description': 'CI-Test'}],
        'resourceLink': 'test', 'result': 'Started'}

    health_check_response = {'testResult': [
        {'item_name': 'Vault State Test ', 'result': True},
        {'item_name': 'Spare Drives Test ', 'result': True},
        {'item_name': 'Memory Test ', 'result': True},
        {'item_name': 'Locks Test ', 'result': True},
        {'item_name': 'Emulations Test ', 'result': True},
        {'item_name': 'Environmentals Test ', 'result': False},
        {'item_name': 'Battery Test ', 'result': True},
        {'item_name': 'General Test ', 'result': True},
        {'item_name': 'Compression And Dedup Test ', 'result': True}],
        'execution_status': 'FAILED', 'symmetrixId': array,
        'description': 'CI-Test', 'date': 1573728472714}

    disk_list = {'disk_ids': [
        '0', '1', '10', '11', '12', '13', '2', '3', '4', '5', '6', '7', '8',
        '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8A', '8B',
        '8C', '8D', '9', 'A', 'B', 'C', 'D', 'E', 'F']}

    disk_info = {'spindle_id': '0', 'type': 'INCSTRM_0', 'vendor': 'Intel',
                 'capacity': 354.78}

    tag_list = {'tag_name': ['CLBCK', 'Payroll']}

    tagged_objects = {'array_ids': ['000297600111']}

    # migrate array info
    m_array = '000197800123'
    m_portgroup = 'myportgroup'
    m_initiatorgroup = 'myinitiatorgroup'
    m_sg_name = 'mystoragegroup'
    m_host_name = 'myhost'

    # Old masking views
    smis_mv_1 = 'OS-myhost-No_SLO-I-MV'
    smis_mv_2 = 'OS-myhost-SRP_1-Diamond-NONE-I-CD-MV'
    smis_mv_3 = 'OS-myhost-SRP_1-Diamond-DSS-I-MV'
    smis_mv_4 = 'OS-myhost-SRP_1-Silver-NONE-I-MV'
    smis_mv_5 = 'OS-myhost-SRP_1-Bronze-OLTP-I-CD-MV'
    smis_mv_6 = 'OS-myhost-SRP_1-Diamond-OLTP-I-RE-MV'
    smis_mv_7 = 'OS-host-with-dashes-No_SLO-I-MV'
    smis_mv_8 = 'OS-host-with-dashes-SRP_1-Diamond-NONE-I-MV'

    # New masking view
    rest_mv_1 = 'OS-myhost-I-myportgroup-MV'
    rest_mv_2 = 'OS-myhost-I-portgroup-with-dashes-MV'
    rest_mv_3 = 'OS-host-with-dash-I-myportgroup-MV'

    # Old storage groups
    smis_sg_1 = 'OS-myhost-No_SLO-I-SG'
    smis_sg_2 = 'OS-myhost-SRP_1-Diamond-NONE-I-SG'
    smis_sg_3 = 'OS-myhost-SRP_1-Diamond-DSS-I-SG'
    smis_sg_4 = 'OS-myhost-SRP_1-Silver-NONE-I-CD-SG'
    smis_sg_5 = 'OS-myhost-SRP_1-Diamond-OLTP-I-CD-SG'
    smis_sg_6 = 'OS-myhost-SRP_1-Bronze-OLTP-I-RE-SG'
    smis_sg_7 = 'OS-host-with_dashes-SRP_1-Diamond-OLTP-I-RE-SG'
    smis_sg_8 = 'OS-myhost-SRP_1-Diamond-NONE-I-CD-SG'

    # New parent storage groups
    rest_parent_sg = 'OS-myhost-I-myportgroup-SG'

    # New storage groups
    rest_sg_1 = 'OS-myhost-No_SLO-os-iscsi-pg'
    rest_sg_2 = 'OS-myhost-SRP_1-DiamodNONE-os-iscsi-pg-CD'
    rest_sg_3 = 'OS-myhost-SRP_1-DiamodNONE-os-iscsi-pg'
    rest_sg_4 = 'OS-myhost-SRP_1-DiamodOLTP-os-iscsi-pg-RE'
    rest_sg_5 = 'OS-host-with-dashes-SRP_1-DiamodOLTP-myportgroup-RE'
    rest_sg_6 = 'OS-myhost-SRP_1-DiamodOLTP-myportgroup-CD'

    m_storagegroup = {'slo': 'Diamond',
                      'workload': 'OLTP',
                      'storageGroupId': 'test'}

    m_maskingview = {'portGroupId': m_portgroup,
                     'hostId': m_host_name,
                     'storageGroupId': rest_parent_sg,
                     'maskingViewId': rest_mv_1}

    element_dict = {'new_mv_name': 'OS-myhost-I-myportgroup-MV',
                    'workload': 'NONE',
                    'new_sg_name': 'OS-myhost-SRP_1-DiamodNONE-myportgroup',
                    'srp': 'SRP_1', 'port_group': 'myportgroup',
                    'initiator_group': 'myinitiatorgroup',
                    'new_sg_parent_name': 'OS-myhost-I-myportgroup-SG',
                    'service_level': 'Diamond'}

    element_dict_revert = {
        'service_level': 'Diamond',
        'port_group': 'myportgroup',
        'initiator_group': 'myinitiatorgroup',
        'srp': 'SRP_1',
        'new_mv_name': 'OS-myhost-SRP_1-Diamond-NONE-I-CD-MV',
        'new_sg_name': 'OS-myhost-SRP_1-Diamond-NONE-I-CD-SG',
        'workload': 'NONE'}

    mv_components = {'portGroupId': m_portgroup,
                     'hostId': m_host_name,
                     'storageGroupId': rest_sg_1,
                     'maskingViewId': rest_mv_1}

    device_list = ['0064F', '0088E', '00890', '00891', '00DF2', '00DF3']

    host_io_limit_source = {'host_io_limit_mb_sec': '2000',
                            'host_io_limit_io_sec': '2000',
                            'dynamicDistribution': 'Always'}

    host_io_limit_target = {'host_io_limit_mb_sec': '4000',
                            'host_io_limit_io_sec': '4000',
                            'dynamicDistribution': 'Never'}

    source_sg_details = {'storageGroupId': smis_sg_2,
                         'slo': 'Diamond',
                         'srp': 'SRP_1',
                         'hostIOLimit': host_io_limit_source}

    target_sg_details = {'storageGroupId': rest_sg_3,
                         'slo': 'Diamond',
                         'srp': 'SRP_1',
                         'hostIOLimit': host_io_limit_target}

    snapshot_policy_list = {
        'name': [
            '10_minute',
            '10_min_7_past',
            '10_minute_policy_2',
            'HourlyDefault',
            'WeeklyDefault',
            '10_min_5_past',
            '10_min_on_hour',
            '10_min_3_past',
            'DailyDefault',
            'Hourly_16past']}

    snapshot_policy_name = '10_minute'
    snapshot_policy_info = {'symmetrixID': array,
                            'snapshot_count': 20,
                            'offset_minutes': 0,
                            'interval_minutes': 360,
                            'secure': False,
                            'suspended': False,
                            'snapshot_policy_name': snapshot_policy_name}

    snapshot_policy_sg_list = ['sg1', 'sg2']
    # Metro DR

    metro_dr_detail = {
        'metro_witness_state': 'Available',
        'metro_r2_connectivity_health': 'Degraded',
        'dr_state': 'Synchronized',
        'metro_remain_capacity_to_copy_mb': 0,
        'metro_r1_connectivity_health': 'Degraded',
        'dr_link_state': 'Online',
        'dr_exempt': False,
        'environment_exempt': False,
        'metro_link_state': 'Online',
        'dr_percent_complete': 100,
        'metro_r2_array_health': 'Normal',
        'metro_r1_array_health': 'Normal',
        'valid': True,
        'metro_exempt': False,
        'dr_service_state': 'Active',
        'environment_state': 'Degraded, Manual Recovery',
        'dr_remain_capacity_to_copy_mb': 0,
        'metro_state': 'ActiveActive',
        'name': 'PyU4V_Metro',
        'capacity_gb': 2.003,
        'metro_service_state': 'Active_HA',
        'metro_percent_complete': 100,
        'dr_rdf_mode': 'Adaptive Copy'}

    response_string_dict_success = {'success': True, 'message': 'OK'}
    response_string_dict_fail = {'success': False, 'message': 'FAIL'}

    audit_log_list = {
        'expirationTime': 1600159200802, 'count': 5, 'maxPageSize': 1000,
        'id': 'a2b42abe-977d-4858-bd18-0322d1eb3a43_0', 'from': 1, 'to': 5,
        'resultList': {'result': [
            {'record_id': 747855,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': ('STARTING on PyU4V-sg(Storage group) "CREATE" '
                         'operation. Symm=000111222333, '
                         'SERVICE_LEVEL_NAME=Diamond SRP_NAME=SRP_1 '),
             'entry_date': 1599519722,
             'username': 'C:10.10.10.10\\pyu4v_user'},
            {'record_id': 747856,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': ('Successfully created Storage Group PyU4V-sg '
                         '(index 0xD69) '),
             'entry_date': 1599519722, 'username': ''},
            {'record_id': 747857,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': 'Set SLO 0x1 and SRP 0x1 on devices from SG 0xD69 ',
             'entry_date': 1599519722, 'username': ''},
            {'record_id': 747858,
             'entry_date_string': 'Tue Sep 8 2020 00:02:02',
             'message': ('On Storage group PyU4V-sg operation "CREATE" '
                         'SUCCESSFULLY COMPLETED'),
             'entry_date': 1599519722,
             'username': 'C:10.10.10.10\\pyu4v_user'},
            {'record_id': 747859,
             'entry_date_string': 'Tue Sep 8 2020 00:02:05',
             'message': ('STARTING a TDEV Create Device operation on Symm '
                         '000111222333.'),
             'entry_date': 1599519725,
             'username': 'C:10.10.10.10\\pyu4v_user'}]}}

    audit_record = {
        'function_class': 'BaseCtrl', 'process_id': '5228',
        'api_library': 'SEK', 'action_code': 'Create', 'task_id': '4584',
        'api_version': 'V9.2.0.1', 'application_id': 'UNIVMAX',
        'entry_date': 1599519722, 'audit_class': 'Base', 'record_id': 747855,
        'entry_date_string': 'Tue Sep 8 2020 00:02:02',
        'records_in_sequence': '1', 'hostname': 'PyU4V-Client',
        'offset_in_sequence': '1', 'os_type': 'WinNT',
        'os_revision': '10.0.14393', 'vendor_id': 'EMC Corp',
        'activity_id': 'SE1e3b9f5c45', 'client_host': '',
        'username': 'C:10.10.10.10\\pyu4v_user',
        'application_version': '9.2.0.1',
        'message': (
            'STARTING on PyU4V-sg(Storage group) "CREATE" '
            'operation. Symm=000111222333, SERVICE_LEVEL_NAME=Diamond '
            'SRP_NAME=SRP_1 ')}

    compliance_details = {
        'storage_group_name': storagegroup_name,
        'compliance': 'GREEN', 'sl_count': 1,
        'sl_compliance': [
            {'sl_name': 'DailyDefault',
             'calculation_time': '2020-12-01T12:05',
             'compliance': 'GREEN'}
        ]
    }
