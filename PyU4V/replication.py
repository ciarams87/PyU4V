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
"""replication.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.utils import console
from PyU4V.utils import constants
from PyU4V.utils import decorators
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

# Replication constants
ESTABLISH = constants.ESTABLISH
FAILBACK = constants.FAILBACK
FAILOVER = constants.FAILOVER
RESTORE = constants.RESTORE
RESUME = constants.RESUME
SETBIAS = constants.SETBIAS
SETMODE = constants.SETMODE
ENABLECONSISTENCY = constants.ENABLECONSISTENCY
DISABLECONSISTENCY = constants.DISABLECONSISTENCY
SPLIT = constants.SPLIT
SUSPEND = constants.SUSPEND
SWAP = constants.SWAP
SNAP_ID = constants.SNAP_ID

# Resource constants
ASYNC_UPDATE = constants.ASYNC_UPDATE
REPLICATION = constants.REPLICATION
SYMMETRIX = constants.SYMMETRIX
CAPABILITIES = constants.CAPABILITIES
STORAGEGROUP = constants.STORAGEGROUP
SNAPSHOT = constants.SNAPSHOT
GENERATION = constants.GENERATION
RDFG = constants.RDFG
VOLUME = constants.VOLUME
RDF_DIRECTOR = constants.RDF_DIRECTOR
PORT = constants.PORT
REMOTE_PORT = constants.REMOTE_PORT
RDF_GROUP = constants.RDF_GROUP


class ReplicationFunctions(object):
    """ReplicationFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.provisioning = ProvisioningFunctions(array_id, rest_client)
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.array_id = array_id

    def get_replication_info(self):
        """Return replication information for an array.

        :returns: replication details -- dict
        """
        return self.get_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=self.array_id)

    def get_array_replication_capabilities(self, array_id=None):
        """Check what replication facilities are available.

        :returns: replication capability details -- dict
        """
        array_id = array_id if array_id else self.array_id
        capabilities = self.get_resource(
            category=REPLICATION, resource_level=CAPABILITIES,
            resource_type=SYMMETRIX)
        symm_list = capabilities.get(
            'symmetrixCapability', list()) if capabilities else list()
        array_capabilities = dict()
        for symm in symm_list:
            if symm['symmetrixId'] == array_id:
                array_capabilities = symm
                break
        return array_capabilities

    def is_snapvx_licensed(self):
        """Check if the snapVx feature is licensed and enabled.

        :returns: bool
        """
        snap_capability = False
        capabilities = self.get_array_replication_capabilities()
        if capabilities:
            snap_capability = capabilities.get('snapVxCapable', False)
        else:
            LOG.error('Cannot access replication capabilities '
                      'for array {arr}'.format(arr=self.array_id))
        return snap_capability

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'get_storage_group_srdf_details', 9.1, 10.0)
    def get_storage_group_rep(self, storage_group_name):
        """Given a name, return storage group srdf info.

        DEPRECATION NOTICE: ReplicationFunctions.get_storage_group_rep()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.get_storage_group_srdf_details(). For further
        information please consult PyU4V 9.1 release notes.

        :param storage_group_name: storage group id -- str
        :returns: storage group replication details -- dict
        """
        return self.get_storage_group_replication_details(storage_group_name)

    def get_storage_group_replication_details(self, storage_group_id):
        """Given a storage group id, return storage group srdf info.

        :param storage_group_id: storage group id -- str
        :returns: storage group replication details -- dict
        """
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'get_replication_enabled_storage_groups',
        9.1, 10.0)
    def get_storage_group_rep_list(self, has_snapshots=False, has_srdf=False):
        """Return list of storage groups with replication.

        :param has_snapshots: return only storage groups with snapshots
        :param has_srdf: return only storage groups with SRDF
        :returns: list of storage groups with associated replication
        """
        return self.get_replication_enabled_storage_groups(has_snapshots,
                                                           has_srdf)

    def get_replication_enabled_storage_groups(self, has_snapshots=False,
                                               has_srdf=False):
        """Return list of storage groups with replication.

        :param has_snapshots: return only storage groups with snapshots
        :param has_srdf: return only storage groups with SRDF
        :returns: list of storage groups with associated replication
        """
        filters = dict()
        if has_snapshots:
            filters.update({'hasSnapshots': 'true'})
        if has_srdf:
            filters.update({'hasSrdf': 'true'})
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, params=filters)
        storage_group_list = (
            response.get('name', list()) if response else list())
        return storage_group_list

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'get_storage_group_snapshot_list', 9.1, 10.0)
    def get_storagegroup_snapshot_list(self, storagegroup_id):
        """Get a list of snapshots associated with a storage group.

        DEPRECATION NOTICE:
        ReplicationFunctions.get_storagegroup_snapshot_list() will be
        refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.get_storage_group_snapshot_list(). For further
        information please consult PyU4V 9.1 release notes.

        :param storagegroup_id: storage group id -- str
        :returns: snapshot ids -- list
        """
        return self.get_storage_group_snapshot_list(storagegroup_id)

    def get_storage_group_snapshot_list(self, storage_group_id):
        """Get a list of snapshots associated with a storage group.

        :param storage_group_id: storage group id -- str
        :returns: snapshot ids -- list
        """
        try:
            response = self.get_resource(
                category=REPLICATION,
                resource_level=SYMMETRIX, resource_level_id=self.array_id,
                resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
                resource=SNAPSHOT)
        except exception.ResourceNotFoundException:
            return list()
        return response.get('name', list()) if response else list()

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'create_storage_group_snap', 9.1, 10.0)
    def create_storagegroup_snap(
            self, sg_name, snap_name, ttl=None, hours=False):
        """Create a snapVx snapshot of a storage group.

        DEPRECATION NOTICE: ReplicationFunctions.create_storagegroup_snap()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.create_storage_group_snap(). For further
        information please consult PyU4V 9.1 release notes.

        To establish a new generation of an existing SnapVX snapshot for a
        source SG, use the same name as the existing snapshot for the new
        snapshot.

        :param sg_name: source storage group id -- str
        :param snap_name: snapshot name -- str
        :param ttl: Time To Live -- str
        :param hours: if TTL is in hours instead of days -- bool
        :returns: snapshot details -- dict
        """
        return self.create_storage_group_snapshot(sg_name, snap_name, ttl,
                                                  hours)

    def create_storage_group_snapshot(
            self, storage_group_id, snap_name, ttl=None, hours=False,
            secure=False):
        """Create a snapVx snapshot of a storage group.

        To establish a new generation of an existing SnapVX snapshot for a
        source SG, use the same name as the existing snapshot for the new
        snapshot.

        :param storage_group_id: source storage group id -- str
        :param snap_name: snapshot name -- str
        :param ttl: Time To Live -- str
        :param hours: if TTL is in hours instead of days -- bool
        :param secure: sets secure snapshot, snapshot created with secure
               option can not be deleted before ttl expires -- bool
        :returns: snapshot details -- dict
        """
        payload = {'snapshotName': snap_name}
        if ttl:
            if secure:
                payload.update({'secure': ttl})
            else:
                payload.update({'timeToLive': ttl})
            if hours:
                payload.update({'timeInHours': 'True'})
        return self.create_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=SNAPSHOT, payload=payload)

    @decorators.refactoring_notice(
        'ReplicationFunctions',
        'get_storage_group_snapshot_generation_list', 9.1, 10.0)
    def get_storagegroup_snapshot_generation_list(
            self, storagegroup_id, snap_name):
        """Get a snapshot and its generation count information for an sg.

        DEPRECATION NOTICE:
        ReplicationFunctions.get_storagegroup_snapshot_generation_list()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.get_storage_group_snapshot_generation_list(). For
        further information please consult PyU4V 9.1 release notes.

        The most recent snapshot will have a gen number of 0. The oldest
        snapshot will have a gen number = genCount - 1 (i.e. if there are 4
        generations of particular snapshot, the oldest will have a gen num
        of 3).

        :param storagegroup_id: name of the storage group -- str
        :param snap_name: the name of the snapshot -- str
        :returns: generation numbers -- list
        """
        return self.get_storage_group_snapshot_generation_list(
            storagegroup_id, snap_name)

    def get_storage_group_snapshot_generation_list(
            self, storage_group_id, snap_name):
        """Get a snapshot and its generation count information for an sg.

        This is for arrays with microcode less than 5978.669.669.
        Please use get_storage_group_snapshot_snap_id_list for microcode
        greater than 5978.669.669.

        The most recent snapshot will have a gen number of 0. The oldest
        snapshot will have a gen number = genCount - 1 (i.e. if there are 4
        generations of particular snapshot, the oldest will have a gen num
        of 3).

        :param storage_group_id: name of the storage group -- str
        :param snap_name: the name of the snapshot -- str
        :returns: generation numbers -- list
        """
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=GENERATION)
        return response.get('generations', list()) if response else list()

    def get_storage_group_snapshot_snap_id_list(
            self, storage_group_id, snap_name):
        """Get a snapshot and its snap id information for an sg.

        Each snapid is unique.  These have replaced generations starting
        at U4P9.2. Snap ids are only available on microcode 5978.669.669
        and greater.

        :param storage_group_id: name of the storage group -- str
        :param snap_name: the name of the snapshot -- str
        :returns: snapids -- list
        """
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=SNAP_ID)
        return response.get('snapids', list()) if response else list()

    def get_snapshot_generation_details(self, sg_id, snap_name, gen_num):
        """Get the details for a particular snapshot generation.

        This is for arrays with microcode less than 5978.669.669.
        Please use get_snapshot_snap_id_details for microcode greater than
        5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param gen_num: generation number -- int
        :returns: snapshot generation details -- dict
        """
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=sg_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=GENERATION, object_type_id=str(gen_num))

    def get_snapshot_snap_id_details(self, sg_id, snap_name, snap_id):
        """Get the details for a particular snapshot snap_id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param snap_id: unique snap id -- int
        :returns: snapshot snap id details -- dict
        """
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=sg_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=SNAP_ID, object_type_id=snap_id)

    def find_expired_snapvx_snapshots(self):
        """Find all expired snapvx snapshots.

        This is for arrays with microcode less than 5978.669.669.
        Please use find_expired_snapvx_snapshots_by_snap_ids for microcode
        greater than 5978.669.669.

        Parses through all Snapshots for array and lists those that have
        snapshots where the expiration date has passed however snapshots
        have not been deleted as they have links.

        :returns: expired snapshot details -- list
        """
        expired_snap_list = list()
        sg_list = self.get_replication_enabled_storage_groups(
            has_snapshots=True)
        for sg in sg_list:
            snap_list = self.get_storage_group_replication_details(sg)
            for snapshot_name in snap_list['snapVXSnapshots']:
                snap_gen_list = (
                    self.get_storage_group_snapshot_generation_list(
                        sg, snapshot_name))
                for x in snap_gen_list:
                    snap_details = self.get_snapshot_generation_details(
                        sg, snapshot_name, x)
                    expired = snap_details.get(
                        'isExpired') if snap_details.get(
                        'isExpired') else snap_details.get('expired')
                    if expired:
                        snap_creation_time = snap_details.get('timestamp')
                        for linked_sg in snap_details.get(
                                'linkedStorageGroup', list()):
                            linked_sg_name = linked_sg['name']
                            LOG.debug(
                                'Storage group {sg} has expired snapshot. '
                                'Snapshot name {ss}, Generation Number {gen}, '
                                'linked storage group name is {sg_l}'.format(
                                    sg=sg, ss=snapshot_name, gen=x,
                                    sg_l=linked_sg_name))
                            expired_snap_details = ({
                                'storagegroup_name': sg,
                                'snapshot_name': snapshot_name,
                                'generation_number': x,
                                'linked_sg_name': linked_sg_name,
                                'snap_creation_time': snap_creation_time})
                            expired_snap_list.append(expired_snap_details)
        return expired_snap_list

    def find_expired_snapvx_snapshots_by_snap_ids(self):
        """Find all expired snapvx snapshots using snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        Parses through all Snapshots for array and lists those that have
        snapshots where the expiration date has passed however snapshots
        have not been deleted as they have links.

        :returns: expired snapshot details -- list
        """
        expired_snap_list = list()
        sg_list = self.get_replication_enabled_storage_groups(
            has_snapshots=True)
        for sg in sg_list:
            snap_list = self.get_storage_group_replication_details(sg)
            for snapshot_name in snap_list['snapVXSnapshots']:
                snap_id_list = (
                    self.get_storage_group_snapshot_snap_id_list(
                        sg, snapshot_name))
                for x in snap_id_list:
                    snap_details = self.get_snapshot_snap_id_details(
                        sg, snapshot_name, x)
                    expired = snap_details.get(
                        'isExpired') if snap_details.get(
                        'isExpired') else snap_details.get('expired')
                    if expired:
                        snap_creation_time = snap_details.get('timestamp')
                        for linked_sg in snap_details.get(
                                'linked_storage_group', list()):
                            linked_sg_name = linked_sg['name']
                            LOG.debug(
                                'Storage group {sg} has expired snapshot. '
                                'Snapshot name {ss}, Snap Id {snap_id}, '
                                'linked storage group name is {sg_l}'.format(
                                    sg=sg, ss=snapshot_name, snap_id=x,
                                    sg_l=linked_sg_name))
                            expired_snap_details = ({
                                'storagegroup_name': sg,
                                'snapshot_name': snapshot_name,
                                'snap_id': x,
                                'linked_sg_name': linked_sg_name,
                                'snap_creation_time': snap_creation_time})
                            expired_snap_list.append(expired_snap_details)
        return expired_snap_list

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'modify_storage_group_snapshot', 9.1, 10.0)
    def modify_storagegroup_snap(
            self, source_sg_id, target_sg_id, snap_name, link=False,
            unlink=False, restore=False, new_name=None, gen_num=0,
            _async=False):
        """Modify a storage group snapshot.

        DEPRECATION NOTICE: ReplicationFunctions.modify_storagegroup_snap()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.modify_storage_group_snapshot(). For further
        information please consult PyU4V 9.1 release notes.

        Please note that only one parameter can be modified at a time.
        Default action is not to create full copy

        :param source_sg_id: source sg id -- str
        :param target_sg_id: target sg id (Can be None) -- str
        :param snap_name: snapshot name -- str
        :param link: link action required -- bool
        :param unlink: unlink action required -- bool
        :param restore: restore action required -- bool
        :param new_name: new name for the snapshot -- str
        :param gen_num: generation number -- int
        :param _async: if call should be async -- bool
        :returns: modified storage group snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            source_sg_id, target_sg_id, snap_name, link, unlink, restore,
            new_name, gen_num, _async)

    def modify_storage_group_snapshot(
            self, src_storage_grp_id, tgt_storage_grp_id, snap_name,
            link=False, unlink=False, restore=False, new_name=None,
            gen_num=0, _async=False, relink=False):
        """Modify a storage group snapshot.

        This is for arrays with microcode less than 5978.669.669.
        Please use modify_storage_group_snapshot_by_snap_id for microcode
        greater than 5978.669.669.

        Please note that only one parameter can be modified at a time.
        Default action is not to create full copy.

        :param src_storage_grp_id: name of the storage group -- str
        :param tgt_storage_grp_id: target sg id (Can be None) -- str
        :param snap_name: snapshot name -- str
        :param link: link action required -- bool
        :param unlink: unlink action required -- bool
        :param restore: restore action required -- bool
        :param new_name: new name for the snapshot -- str
        :param gen_num: generation number -- int
        :param _async: if call should be async -- bool
        :param relink: relink action required -- bool
        :returns: modified storage group snapshot details -- dict
        """
        payload = dict()
        if link:
            payload = ({'action': 'Link', 'link': {
                'linkStorageGroupName': tgt_storage_grp_id,
                'copy': False}})
        elif unlink:
            payload = ({'action': 'Unlink', 'unlink': {
                'unlinkStorageGroupName': tgt_storage_grp_id}})
        elif restore:
            payload = {'action': 'Restore'}
        elif new_name:
            payload = ({'rename': {'newSnapshotName': new_name},
                        'action': 'Rename'})
        elif relink:
            payload = ({'action': 'Relink', 'relink': {
                'relinkStorageGroupName': tgt_storage_grp_id}})
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=src_storage_grp_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=GENERATION, object_type_id=str(gen_num),
            payload=payload)

    def modify_storage_group_snapshot_by_snap_id(
            self, src_storage_grp_id, tgt_storage_grp_id, snap_name,
            snap_id, link=False, unlink=False, restore=False, new_name=None,
            _async=False, relink=False):
        """Modify a storage group snapshot using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        Please note that only one parameter can be modified at a time.
        Default action is not to create full copy

        :param src_storage_grp_id: name of the storage group -- str
        :param tgt_storage_grp_id: target sg id (Can be None) -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snap id -- int
        :param link: link action required -- bool
        :param unlink: unlink action required -- bool
        :param restore: restore action required -- bool
        :param new_name: new name for the snapshot -- str
        :param _async: if call should be async -- bool
        :param relink: relink action required -- bool
        :returns: modified storage group snapshot details -- dict
        """
        payload = dict()
        if link:
            payload = ({'action': 'Link', 'link': {
                'storage_group_name': tgt_storage_grp_id,
                'copy': False}})
        elif unlink:
            payload = ({'action': 'Unlink', 'unlink': {
                'storage_group_name': tgt_storage_grp_id}})
        elif restore:
            payload = {'action': 'Restore'}
        elif new_name:
            payload = ({'rename': {'new_snapshot_name': new_name},
                        'action': 'Rename'})
        elif relink:
            payload = ({'action': 'Relink', 'relink': {
                'storage_group_name': tgt_storage_grp_id}})
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=src_storage_grp_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=SNAP_ID, object_type_id=snap_id,
            payload=payload)

    def restore_snapshot(self, sg_id, snap_name, gen_num=0):
        """Restore a storage group to its snapshot.

        This is for arrays with microcode less than 5978.669.669.
        Please use restore_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            sg_id, None, snap_name, restore=True, gen_num=gen_num)

    def restore_snapshot_by_snap_id(self, sg_id, snap_name, snap_id):
        """Restore a storage group to its snapshot using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, None, snap_name, snap_id, restore=True)

    def rename_snapshot(self, sg_id, snap_name, new_name, gen_num=0):
        """Rename an existing storage group snapshot.

        This is for arrays with microcode less than 5978.669.669.
        Please use rename_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param new_name: new snapshot name -- str
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            sg_id, None, snap_name,
            new_name=new_name, gen_num=gen_num)

    def rename_snapshot_by_snap_id(self, sg_id, snap_name, new_name, snap_id):
        """Rename an existing storage group snapshot using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param new_name: new snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, None, snap_name, snap_id, new_name=new_name)

    def link_gen_snapshot(self, sg_id, snap_name, link_sg_name,
                          _async=False, gen_num=0):
        """Link a snapshot to another storage group.

        This is for arrays with microcode less than 5978.669.669.
        Please use link_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        Target storage group will be created if it does not exist.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param link_sg_name: target storage group name -- str
        :param _async: if call should be async -- bool
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot(
            sg_id, link_sg_name, snap_name,
            link=True, gen_num=gen_num, _async=_async)

    def link_snapshot_by_snap_id(
            self, sg_id, link_sg_name, snap_name, snap_id, _async=False):
        """Link a snapshot to another storage group using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        Target storage group will be created if it does not exist.

        :param sg_id: storage group id -- str
        :param link_sg_name: target storage group name -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :param _async: if call should be async -- bool
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, link_sg_name, snap_name, snap_id, link=True, _async=_async)

    def unlink_gen_snapshot(self, sg_id, snap_name, unlink_sg_name,
                            _async=False, gen_num=0):
        """Unlink a snapshot from another storage group.

        This is for arrays with microcode less than 5978.669.669.
        Please use unlink_snapshot_by_snap_id for microcode greater
        than 5978.669.669.

        :param sg_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param unlink_sg_name: target storage group name -- str
        :param _async: if call should be async -- bool
        :param gen_num: snapshot generation number -- int
        :returns: snapshot details -- dict
        """
        return self.modify_storagegroup_snap(
            sg_id, unlink_sg_name, snap_name,
            unlink=True, gen_num=gen_num, _async=_async)

    def unlink_snapshot_by_snap_id(
            self, sg_id, unlink_sg_name, snap_name, snap_id, _async=False):
        """Unlink a snapshot from another storage group using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param sg_id: storage group id -- str
        :param unlink_sg_name: target storage group name -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        :param _async: if call should be async -- bool
        :returns: snapshot details -- dict
        """
        return self.modify_storage_group_snapshot_by_snap_id(
            sg_id, unlink_sg_name, snap_name, snap_id,
            unlink=True, _async=_async)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'delete_storage_group_snapshot', 9.1, 10.0)
    def delete_storagegroup_snapshot(self, storagegroup, snap_name, gen_num=0):
        """Delete the snapshot of a storage group.

        DEPRECATION NOTICE: ReplicationFunctions.delete_storagegroup_snapshot()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.delete_storage_group_snapshot(). For further
        information please consult PyU4V 9.1 release notes.

        :param storagegroup: storage group id -- str
        :param snap_name: snapshot name -- str
        :param gen_num: snapshot generation number -- int
        """

        self.delete_storage_group_snapshot(storagegroup, snap_name, gen_num)

    def delete_storage_group_snapshot(self, storage_group_id, snap_name,
                                      gen=0):
        """Delete the snapshot of a storage group.

        This is for arrays with microcode less than 5978.669.669.
        Please use delete_storage_group_snapshot_by_snap_id for microcode
        greater than 5978.669.669.

        :param storage_group_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param gen: snapshot generation number -- int
        """
        self.delete_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=GENERATION, object_type_id=str(gen))

    def delete_storage_group_snapshot_by_snap_id(
            self, storage_group_id, snap_name, snap_id):
        """Delete the snapshot of a storage group using it's snap id.

        Snap ids are only available on microcode 5978.669.669
        and greater.

        :param storage_group_id: storage group id -- str
        :param snap_name: snapshot name -- str
        :param snap_id: snapshot snap id -- int
        """
        self.delete_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=SNAPSHOT, resource_id=snap_name,
            object_type=SNAP_ID, object_type_id=snap_id)

    @decorators.deprecation_notice('ReplicationFunctions', 9.1, 10.0)
    def choose_snapshot_from_list_in_console(self, storagegroup_id):
        """Allow a user to select a snapshot from a list.

        DEPRECATION NOTICE:
        ReplicationFunctions.choose_snapshot_from_list_in_console() will be
        deprecated in PyU4V version 10.0. For further information please
        consult PyU4V 9.1 release notes.

        :param storagegroup_id: storage group id -- str
        :returns: chosen snapshot details -- dict
        """
        snap_list = self.get_storagegroup_snapshot_list(storagegroup_id)
        return console.choose_from_list('snapshot', snap_list)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'is_volume_in_replication_session', 9.1, 10.0)
    def is_vol_in_rep_session(self, device_id):
        """Check if a volume is in a replication session.

        DEPRECATION NOTICE: ReplicationFunctions.is_vol_in_rep_session() will
        be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.is_volume_in_replication_session(). For further
        information please consult PyU4V 9.1 release notes.

        :param device_id: device id -- str
        :returns: snap vx target, snap vx source, rdf group -- bool, bool, list
        """
        return self.is_volume_in_replication_session(device_id)

    def is_volume_in_replication_session(self, device_id):
        """Check if a volume is in a replication session.

        :param device_id: device id -- str
        :returns: snap vx target, snap vx source, rdf group -- bool, bool, list
        """
        snapvx_src, snapvx_tgt, rdf_grp = False, False, None
        volume_details = self.provisioning.get_volume(device_id)
        if volume_details:
            LOG.debug('Vol details: {vol}'.format(vol=volume_details))
            if volume_details.get('snapvx_target'):
                snapvx_tgt = volume_details['snapvx_target']
            if volume_details.get('snapvx_source'):
                snapvx_src = volume_details['snapvx_source']
            if volume_details.get('rdfGroupId'):
                rdf_grp = volume_details['rdfGroupId']
        return snapvx_tgt, snapvx_src, rdf_grp

    def get_rdf_group(self, rdf_number, array_id=None):
        """Get specific rdf group details.

        :param rdf_number: rdf group number -- int
        :param array_id: array serial number -- str
        :returns: rdf group details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=RDFG, resource_type_id=rdf_number)

    def get_rdf_group_list(self, array_id=None):
        """Get rdf group list from array.

        :param array_id: array serial number -- str
        :returns: rdf group list -- list
        """
        array_id = self.array_id if not array_id else array_id
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=RDFG)
        return response.get('rdfGroupID', list()) if response else list()

    def get_rdf_group_volume(self, rdf_number, device_id):
        """Get specific volume details, from an RDF group.

        :param rdf_number: rdf group number -- int
        :param device_id: device id -- str
        :returns: rdf group volume details -- dict
        """
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=RDFG, resource_type_id=rdf_number,
            resource=VOLUME, resource_id=device_id)

    def get_rdf_group_volume_list(self, rdf_number):
        """Get specific volume details, from an RDF group.

        :param rdf_number: rdf group number -- int
        :returns: device ids -- list
        """
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=RDFG, resource_type_id=rdf_number,
            resource=VOLUME)
        return response.get('name', list()) if response else list()

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'are_volumes_rdf_paired', 9.1, 10.0)
    def are_vols_rdf_paired(self, remote_array, device_id,
                            target_device, rdf_group):
        """Check if a pair of volumes are RDF paired.

        DEPRECATION NOTICE: ReplicationFunctions.are_vols_rdf_paired() will
        be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.are_volumes_rdf_paired(). For further information
        please consult PyU4V 9.1 release notes.

        :param remote_array: remote array serial number -- str
        :param device_id: device id -- str
        :param target_device: target device id -- str
        :param rdf_group: rdf group number -- int
        :returns: paired, state -- bool, string
        """
        return self.are_volumes_rdf_paired(remote_array, device_id,
                                           target_device, rdf_group)

    def are_volumes_rdf_paired(self, remote_array, device_id,
                               target_device, rdf_group):
        """Check if a pair of volumes are RDF paired.

        :param remote_array: remote array serial number -- str
        :param device_id: device id -- str
        :param target_device: target device id -- str
        :param rdf_group: rdf group number -- int
        :returns: paired, state -- bool, string
        """
        paired, local_vol_state, rdf_pair_state = False, '', ''
        volume = self.get_rdf_group_volume(rdf_group, device_id)
        if volume:
            remote_volume = volume['remoteVolumeName']
            remote_symm = volume['remoteSymmetrixId']
            if (remote_volume == target_device and (
                    remote_array == remote_symm)):
                paired = True
                local_vol_state = volume['localVolumeState']
                rdf_pair_state = volume['rdfpairState']
        else:
            LOG.warning('Cannot find source RDF volume {vol}.'.format(
                vol=device_id))
        return paired, local_vol_state, rdf_pair_state

    def get_rdf_group_number(self, rdf_group_label):
        """Given a group label, return the associated group number.

        :param rdf_group_label: rdf group label -- str
        :returns: rdf group number -- int
        """
        number = None
        rdf_list = self.get_rdf_group_list()
        if rdf_list:
            number = ([rdf['rdfgNumber'] for rdf in rdf_list
                       if rdf['label'] == rdf_group_label][0])
        if number:
            rdf_group = self.get_rdf_group(number)
            if not rdf_group:
                number = None
        return number

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'get_storage_group_srdf_group_list', 9.1, 10.0)
    def get_storagegroup_srdfg_list(self, storagegroup_id):
        """Get the rdf group numbers for a storage group.

        DEPRECATION NOTICE: ReplicationFunctions.get_storagegroup_srdfg_list()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.get_storagegroup_srdfg_list(). For further
        information please consult PyU4V 9.1 release notes.

        :param storagegroup_id: replicated storage group id -- str
        :returns: rdf group numbers -- list
        """
        return self.get_storage_group_srdf_group_list(storagegroup_id)

    def get_storage_group_srdf_group_list(self, storage_group_id,
                                          array_id=None):
        """Get the rdf group numbers for a storage group.

        :param storage_group_id: replicated storage group id -- str
        :param array_id: array serial number -- str
        :returns: rdf group numbers -- list
        """
        array_id = self.array_id if not array_id else array_id
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=RDFG)
        return response.get('rdfgs', list()) if response else list()

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'get_storage_group_rdf_details', 9.1, 10.0)
    def get_storagegroup_srdf_details(self, storagegroup_id, rdfg_num):
        """Get the details for an rdf group on a particular storage group.

        DEPRECATION NOTICE:
        ReplicationFunctions.get_storagegroup_srdf_details() will be refactored
        in PyU4V version 10.0 in favour of
        ReplicationFunctions.get_storage_group_rdf_details(). For further
        information please consult PyU4V 9.1 release notes.

        :param storagegroup_id: replicated storage group id -- str
        :param rdfg_num: rdf group number -- int
        :returns: storage group rdf details -- dict
        """
        return self.get_storage_group_srdf_details(storagegroup_id, rdfg_num)

    def get_storage_group_srdf_details(self, storage_group_id, rdfg_num):
        """Get the details for an rdf group on a particular storage group.

        :param storage_group_id: replicated storage group id -- str
        :param rdfg_num: rdf group number -- int
        :returns: storage group rdf details -- dict
        """
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=RDFG, resource_id=rdfg_num)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'create_storage_group_srdf_pairings',
        9.1, 10.0)
    def create_storagegroup_srdf_pairings(
            self, storagegroup_id, remote_sid, srdfmode, establish=None,
            _async=False, rdfg_number=None, forceNewRdfGroup=False):
        """RDF protect a storage group.

        DEPRECATION NOTICE:
        ReplicationFunctions.create_storagegroup_srdf_pairings() will be
        refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.create_storage_group_srdf_pairings(). For further
        information please consult PyU4V 9.1 release notes.

        Valid modes are 'Active', 'AdaptiveCopyDisk', 'Synchronous', and
        'Asynchronous'.

        :param storagegroup_id: storage group id -- str
        :param remote_sid: remote array id -- str
        :param srdfmode: replication mode -- str
        :param establish: establish srdf -- bool
        :param _async: if call should be async -- bool
        :param rdfg_number: rdf group number -- int
        :param forceNewRdfGroup: if operation should use force -- bool
        :returns: storage group rdf details -- dict
        """
        return self.create_storage_group_srdf_pairings(
            storagegroup_id, remote_sid, srdfmode, establish, _async,
            rdfg_number, forceNewRdfGroup)

    def create_storage_group_srdf_pairings(
            self, storage_group_id, remote_sid, srdf_mode, establish=None,
            _async=False, rdfg_number=None, force_new_rdf_group=False):
        """SRDF protect a storage group.

        Valid modes are 'Active', 'AdaptiveCopyDisk', 'Synchronous', and
        'Asynchronous'.

        :param storage_group_id: storage group id -- str
        :param remote_sid: remote array id -- str
        :param srdf_mode: replication mode -- str
        :param establish: establish srdf -- bool
        :param _async: if call should be async -- bool
        :param rdfg_number: rdf group number -- int
        :param force_new_rdf_group: if force command should be applied -- bool
        :returns: storage group rdf details -- dict
        """
        establish_sg = 'True' if establish else 'False'
        rdf_payload = {'replicationMode': srdf_mode,
                       'remoteSymmId': remote_sid,
                       'remoteStorageGroupName': storage_group_id,
                       'establish': establish_sg}
        if rdfg_number is not None:
            rdf_payload['rdfgNumber'] = rdfg_number
        if force_new_rdf_group:
            rdf_payload.update({'forceNewRdfGroup': True})
        if _async:
            rdf_payload.update(ASYNC_UPDATE)
        return self.create_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            resource=RDFG, payload=rdf_payload)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'modify_storage_group_srdf', 9.1, 10.0)
    def modify_storagegroup_srdf(
            self, storagegroup_id, action, rdfg, options=None, _async=False):
        """Modify the state of a rdf group.

        DEPRECATION NOTICE: ReplicationFunctions.modify_storagegroup_srdf()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.modify_storage_group_srdf(). For further
        information please consult PyU4V 9.1 release notes.

        This may be a long running task depending on the size of the SRDF
        group, can switch to async call if required. Available actions are
        'Establish', 'Split', 'Suspend', 'Restore', 'Resume', 'Failover',
        'Failback', 'Swap', 'SetBias', and 'SetMode'.

        :param storagegroup_id: storage group id -- str
        :param action: the rdf action --str
        :param rdfg: rdf group number -- int
        :param options: srdf options e.g.
                        {setMode': {'mode': 'Asynchronous'}} -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storagegroup_id, action, rdfg, options, _async)

    def modify_storage_group_srdf(
            self, storage_group_id, action, srdf_group_number, options=None,
            _async=False):
        """Modify the state of a rdf group.

        This may be a long running task depending on the size of the SRDF
        group, can switch to async call if required. Available actions are
        'Establish', 'EnableConsistency', 'DisableConsistency', 'Split',
        'Suspend', 'Restore', 'Resume', 'Failover', 'Failback', 'Swap',
        'SetBias', and 'SetMode'.
        :param storage_group_id: storage group id -- str
        :param action: the rdf action, note enable/disable consistency
                       feature requires Unisphere 9.2.1.6 or higher -- str
        :param srdf_group_number: srdf group number -- int
        :param options: srdf options e.g.
                        {setMode': {'mode': 'Asynchronous'}} -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        srdf_actions = {
            'ESTABLISH': ESTABLISH, 'SPLIT': SPLIT, 'SUSPEND': SUSPEND,
            'RESTORE': RESTORE, 'RESUME': RESUME, 'FAILOVER': FAILOVER,
            'FAILBACK': FAILBACK, 'SWAP': SWAP, 'SETBIAS': SETBIAS,
            'SETMODE': SETMODE, 'DISABLECONSISTENCY': DISABLECONSISTENCY,
            'ENABLECONSISTENCY': ENABLECONSISTENCY}
        srdf_action = srdf_actions.get(action.upper())

        if srdf_action:
            payload = {'action': srdf_action}
        else:
            msg = ('SRDF Action must be one of [Establish, Split, Suspend, '
                   'Restore, Resume, Failover, Failback, Swap, SetBias, '
                   'SetMode]')
            LOG.exception(msg)
            raise exception.VolumeBackendAPIException(data=msg)
        if _async:
            payload.update(ASYNC_UPDATE)
        if options and action:
            payload.update(options)

        return self.modify_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=self.array_id, resource_type=STORAGEGROUP,
            resource_type_id=storage_group_id, resource=RDFG,
            resource_id=srdf_group_number, payload=payload)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'suspend_storage_group_srdf', 9.1, 10.0)
    def suspend_storagegroup_srdf(self, storagegroup_id, rdfg_no,
                                  suspend_options=None, _async=False):
        """Suspend IO on the links for the given storage group.

        DEPRECATION NOTICE: ReplicationFunctions.suspend_storagegroup_srdf()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.suspend_storage_group_srdf(). For further
        information please consult PyU4V 9.1 release notes.

        Optional boolean parameters to set are "bypass", "metroBias", "star",
        "immediate", "hop2", "consExempt", "force", "symForce".

        :param storagegroup_id: storage group id -- str
        :param rdfg_no: rdf group number -- int
        :param suspend_options: suspend parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.suspend_storage_group_srdf(
            storagegroup_id, rdfg_no, suspend_options, _async)

    def suspend_storage_group_srdf(self, storage_group_id, srdf_group_number,
                                   suspend_options=None, _async=False):
        """Suspend IO on the links for the given storage group.

        Optional boolean parameters to set are "bypass", "metroBias", "star",
        "immediate", "hop2", "consExempt", "force", "symForce".

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param suspend_options: suspend parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'suspend', srdf_group_number,
            options=suspend_options, _async=_async)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'establish_storage_group_srdf', 9.1, 10.0)
    def establish_storagegroup_srdf(
            self, storagegroup_id, rdfg_no,
            establish_options=None, _async=False):
        """Establish io on the links for the given storage group.

        DEPRECATION NOTICE: ReplicationFunctions.establish_storagegroup_srdf()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.establish_storage_group_srdf(). For further
        information please consult PyU4V 9.1 release notes.

        Optional boolean parameters to set are 'bypass', 'metroBias', 'star',
        'hop2', 'force', 'symForce', 'full'.

        :param storagegroup_id: storage group id -- str
        :param rdfg_no: rdf group number -- int
        :param establish_options: establish parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.establish_storage_group_srdf(
            storagegroup_id, rdfg_no, establish_options, _async)

    def establish_storage_group_srdf(
            self, storage_group_id, srdf_group_number,
            establish_options=None, _async=False):
        """Establish io on the links for the given storage group.

        Optional boolean parameters to set are 'bypass', 'metroBias', 'star',
        'hop2', 'force', 'symForce', 'full'.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param establish_options: establish parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'establish', srdf_group_number,
            options=establish_options, _async=_async)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'failover_storage_group_srdf', 9.1, 10.0)
    def failover_storagegroup_srdf(
            self, storagegroup_id, rdfg_no,
            failover_options=None, _async=False):
        """Failover a given storage group.

        DEPRECATION NOTICE: ReplicationFunctions.failover_storagegroup_srdf()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.failover_storage_group_srdf(). For further
        information please consult PyU4V 9.1 release notes.

        Optional boolean parameters to set are 'bypass', 'star', 'restore',
        'immediate', 'hop2', 'force', 'symForce', 'remote', 'establish'.

        :param storagegroup_id: storage group id -- str
        :param rdfg_no: rdf group number -- int
        :param failover_options: failover parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.failover_storage_group_srdf(
            storagegroup_id, rdfg_no, failover_options, _async)

    def failover_storage_group_srdf(
            self, storage_group_id, srdf_group_number,
            failover_options=None, _async=False):
        """Failover a given storage group.

        Optional boolean parameters to set are 'bypass', 'star', 'restore',
        'immediate', 'hop2', 'force', 'symForce', 'remote', 'establish'.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param failover_options: failover parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'failover', srdf_group_number,
            options=failover_options, _async=_async)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'failback_storage_group_srdf', 9.1, 10.0)
    def failback_storagegroup_srdf(
            self, storagegroup_id, rdfg_no, failback_options=None,
            _async=False):
        """Failback a given storage group.

        DEPRECATION NOTICE: ReplicationFunctions.failback_storagegroup_srdf()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.failback_storage_group_srdf(). For further
        information please consult PyU4V 9.1 release notes.

        Optional boolean parameters to set are 'bypass', 'recoverPoint',
        'star', 'hop2', 'force', 'symForce', 'remote'.

        :param storagegroup_id: storage group id -- str
        :param rdfg_no: rdf group number -- int
        :param failback_options: failback parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.failback_storage_group_srdf(
            storagegroup_id, rdfg_no, failback_options, _async)

    def failback_storage_group_srdf(
            self, storage_group_id, srdf_group_number, failback_options=None,
            _async=False):
        """Failback a given storage group.

        Optional boolean parameters to set are 'bypass', 'recoverPoint',
        'star', 'hop2', 'force', 'symForce', 'remote'.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param failback_options: failback parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'failback', srdf_group_number,
            options=failback_options, _async=_async)

    @decorators.refactoring_notice(
        'ReplicationFunctions', 'delete_storage_group_srdf', 9.1, 10.0)
    def delete_storagegroup_srdf(
            self, storagegroup_id, rdfg_num=None):
        """Delete srdf pairings for a given storage group.

        DEPRECATION NOTICE: ReplicationFunctions.delete_storagegroup_srdf()
        will be refactored in PyU4V version 10.0 in favour of
        ReplicationFunctions.delete_storage_group_srdf(). For further
        information please consult PyU4V 9.1 release notes.

        :param storagegroup_id: storage group id -- str
        :param rdfg_num: rdf group number -- int
        :returns: storage group rdf details -- dict
        """
        self.delete_storage_group_srdf(storagegroup_id, rdfg_num)

    def delete_storage_group_srdf(
            self, storage_group_id, srdf_group_number, filters=None):
        """Delete srdf pairings for a given storage group.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param filters: optional boolean filters, half_delete,hop2, force,
                        symforce, star, bypass, keepR1, keepR2,
                        usage example filters={'keepR1': 'true'} -- dict
        :returns: storage group rdf details -- dict
        """
        self.delete_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=self.array_id, resource_type=STORAGEGROUP,
            resource_type_id=storage_group_id, resource=RDFG,
            resource_id=srdf_group_number, params=filters)

    def get_rdf_director_list(self, array_id=None, filters=None):
        """Finds out directors configured for SRDF on the specified array.

        :param array_id: 12 digit serial number for PowerMax array -- str
        :param filters: optional filters - dict
        :returns: list of directors -- list
        """
        if not array_id:
            array_id = self.array_id
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=RDF_DIRECTOR, params=filters)
        director_list = (
            response.get('directorId', list()) if response else list())
        return director_list

    def get_rdf_director_detail(self, director_id, array_id=None):
        """Retrieves details for specified RDF_director.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param array_id: 12 digit serial number for PowerMax array -- str
        :returns: director details --dict
        """
        if not array_id:
            array_id = self.array_id
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=RDF_DIRECTOR, resource_type_id=director_id)

    def get_rdf_director_port_list(self, director_id, array_id=None,
                                   filters=None):
        """Retrieves list of ports available on RDF_director.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param array_id: 12 digit serial number for PowerMax array -- str
        :param filters: optional filters -- dict
        :returns: list of RDF ports -- list
        """
        if not array_id:
            array_id = self.array_id
        response = self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=RDF_DIRECTOR, resource_type_id=director_id,
            resource=PORT, params=filters)
        port_list = (
            response.get('portNumber', list()) if response else list())
        return port_list

    def get_rdf_director_port_details(self, director_id, port_id,
                                      array_id=None):
        """Retrieves details of specified RDF ports.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param port_id: port number -- int
        :param array_id: 12 digit serial number for  PowerMax array -- str
        :returns: port details -- dict
        """
        if not array_id:
            array_id = self.array_id
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=RDF_DIRECTOR, resource_type_id=director_id,
            resource=PORT, resource_id=port_id)

    def get_rdf_port_remote_connections(self, director_id, port_id,
                                        array_id=None):
        """Performs a scan of the RDF environment via specified port.

        This function should be run on initial SRDF configuration once zoning
        or IP routing is configured, prior to first RDF group being configured.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param port_id: port number -- int
        :param array_id: 12 digit serial number for Source  -- str
        :returns: remote port details -- dict
        """

        if not array_id:
            array_id = self.array_id
        return self.get_resource(
            category=REPLICATION,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=RDF_DIRECTOR, resource_type_id=director_id,
            resource=PORT, resource_id=port_id, object_type=REMOTE_PORT)

    def create_rdf_group(self, local_director_port_list, remote_array_id,
                         label, local_rdfg_number, remote_rdfg_number,
                         remote_director_port_list, array_id=None):
        """Create a new RDF group between directors and ports on two PowerMax.

        If this is the first connection between 2 arrays please ensure that you
        run get_rdf_remote_port_details and create the initial connection
        group using only the first source port you can extract details for one
        or more remote ports for the desired target array and feed into this
        function. Additional Ports can be added with modify_rdf_group function.

        :param local_director_port_list: list of local directors and ports for
                                         group e.g [RF-1E:1, RF-2E:1] -- list
        :param remote_array_id: 12 digit serial number of remote array  -- str
        :param label: label for group up to 10 characters -- str
        :param local_rdfg_number: rdfg for the local array -- int
        :param remote_rdfg_number: rdfg for the remote array -- int
        :param remote_director_port_list: list of remote directors and ports
                                          to group e.g [RF-1E:1, RF-2E:1]
                                          -- list
        :param array_id: 12 digit serial number of Source (R1) array,
                         if no array is specified the array in config file or
                         api connection will be default -- str
        """
        if not array_id:
            array_id = self.array_id
        local_ports = list()
        remote_ports = list()
        for port in local_director_port_list:
            dir_id = port.split(':')[0]
            port_no = port.split(':')[1]
            local_ports.append({'symmetrixID': array_id,
                                'directorId': dir_id,
                                'portNumber': port_no})
        for port in remote_director_port_list:
            dir_id = port.split(':')[0]
            port_no = port.split(':')[1]
            remote_ports.append({'symmetrixID': remote_array_id,
                                 'directorId': dir_id, 'portNumber': port_no})

        payload = {
            'local_ports': local_ports,
            'remote_rdfg_number': remote_rdfg_number,
            'remote_ports': remote_ports,
            'label': label,
            'local_rdfg_number': local_rdfg_number}

        self.create_resource(category=REPLICATION,
                             resource_level=SYMMETRIX,
                             resource_level_id=array_id,
                             resource_type=RDF_GROUP, payload=payload)

    def modify_rdf_group(self, action, srdf_group_number, array_id=None,
                         port_list=None, label=None, dev_list=None,
                         target_rdf_group=None, consistency_exempt=None):
        """Function to Modify Ports, devices or change label of RDF group.

        Function can be used to Add ports, move volumes between rdf groups,
        remove ports or rename RDF group.

        :param action: add_ports, remove_ports, move -- str
        :param srdf_group_number: srdf group number
                                  for action on local array: int
        :param array_id: 12 digit serial of array -- str
        :param port_list: list of ports to be added or removed e.g.
                          [RF-1E:10, RF-2E:10] --list
        :param label: label for group up to 10 characters -- str
        :param dev_list: list of volumes to be moved between RDF groups -- list
        :param target_rdf_group: rdfg group to move volumes to -- int
        :param consistency_exempt: ignore device for consistency checks -- bool
        """

        rdfg_action = constants.RDFG_ACTIONS.get(action.upper())
        payload = dict()

        if not rdfg_action:
            msg = ('RDFG Action must be one [add_ports, remove_ports, move, '
                   'set_label]')
            LOG.exception(msg)
            raise exception.VolumeBackendAPIException(data=msg)
        if not array_id:
            array_id = self.array_id
        if rdfg_action == 'Move':
            if not consistency_exempt:
                consistency_exempt = False
            payload = {
                'move': {
                    'targetRdfGroup': target_rdf_group,
                    'volumesToMove': dev_list,
                    'exempt': consistency_exempt},
                'action': 'Move'}

        elif rdfg_action == 'set_label':
            payload = {
                "set_label": {
                    "label": label},
                "action": "set_label"}

        elif rdfg_action in ['add_ports', 'remove_ports']:
            if not port_list:
                msg = ('list of ports must be supplied when adding or '
                       'removing ports from RDFG e.g. [RF-1E:10, RF-2E:10]')
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg)
            port_payload = list()
            for port in port_list:
                dir_id, port_no = port.split(':')
                port_payload.append(
                    {'symmetrixID': array_id,
                     'directorId': dir_id,
                     'portNumber': port_no})
                payload = {'action': rdfg_action,
                           rdfg_action: {
                               'ports': port_payload}}

        self.modify_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=RDF_GROUP,
            resource_type_id=srdf_group_number, payload=payload)

    def delete_rdf_group(self, srdf_group_number, array_id=None):
        """Function to Delete SRDF groups between VMAX or PowerMax arrays.

        :param srdf_group_number: number of RDF group to be deleted -- int
        :param array_id: 12 digit serial of array -- str
        """

        if not array_id:
            array_id = self.array_id

        self.delete_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=RDF_GROUP,
            resource_type_id=srdf_group_number)

    def create_storage_group_from_rdfg(
            self, storage_group_name, srdf_group_number, array_id=None,
            rdf_type=None, remote_storage_group_name=None):
        """Creates management storage group from all devices in SRDF group.

        Note SRDF management storage group will be created without a service
        level, it is assumed that this group is created solely for the purpose
        of managing SRDF device and replication state, devices in an SRDF
        group may span multiple applications and storage groups.

        :param storage_group_name: Name of storage group -- str
        :param srdf_group_number: number of RDF group volumes are in -- int
        :param array_id: number of RDF group volumes are in -- int
        :param rdf_type: The SRDF type of the volumes in the SRDF group to be
                         added to the Storage Group. Only needs to be populated
                         if the SRDF group contains both RDF1 and RDF2 volumes
                         valid values RDF1 or RDF2 -- str
        :param remote_storage_group_name: Name of remote storage group -- str
        """
        if not array_id:
            array_id = self.array_id

        create_sg_payload = {
            'rdf_group_number': srdf_group_number}
        payload = {
            'create_sg_from_rdfg': create_sg_payload,
            'storage_group_name': storage_group_name,
            'action': 'CreateSgFromRdfg'}
        if rdf_type:
            create_sg_payload.update({'rdf_type': rdf_type})
        if remote_storage_group_name:
            create_sg_payload.update(
                {'remote_storage_group_name': remote_storage_group_name})

        self.create_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=STORAGEGROUP,
            payload=payload)
