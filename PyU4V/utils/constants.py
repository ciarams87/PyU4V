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
"""constants.py."""

# Configuration constants
SETUP = 'setup'
ARRAY = 'array'
R_ARRAY = 'remote_array'
R_ARRAY_2 = 'remote_array_2'
USERNAME = 'username'
PASSWORD = 'password'
SERVER_IP = 'server_ip'
PORT = 'port'
VERIFY = 'verify'

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'
CONTENT_TYPE = 'content-type'
ACCEPT = 'accept'
ACCEPT_ENC = 'Accept-Encoding'
USER_AGENT = 'user-agent'
APP_TYPE = 'application-type'
APP_JSON = 'application/json'
APP_OCT = 'application/octet-stream'
APP_MPART = 'multipart/form-data'

# Unisphere REST URI constants
PYU4V_VERSION = '9.2.1.4'
UNISPHERE_VERSION = '92'
VERSION = 'version'
ITERATOR = 'Iterator'
PAGE = 'page'
JOB = 'job'
SYMMETRIX = 'symmetrix'
SLOPROVISIONING = 'sloprovisioning'
PROVISIONING = 'provisioning'
STORAGEGROUP = 'storagegroup'
REPLICATION = 'replication'
METRO_DR = 'metrodr'
WLP = 'wlp'
MIGRATION = 'migration'
DSA = 'dsa'
SYSTEM = 'system'
LOCAL_USER = 'local_user'
VOLUME = 'volume'
VVOL = 'vvol'
COMMON = 'common'
HEADROOM = 'headroom'
ENVIRONMENT = 'environment'
CAPABILITIES = 'capabilities'
DIRECTOR = 'director'
PORTGROUP = 'portgroup'
HOST = 'host'
HOSTGROUP = 'hostgroup'
INITIATOR = 'initiator'
MASKINGVIEW = 'maskingview'
CONNECTIONS = 'connections'
SLO = 'slo'
WORKLOADTYPE = 'workloadtype'
SRP = 'srp'
COMPRESSIBILITY_REPORT = 'compressibility_report'
SG_DEMAND_REPORT = 'storage_group_demand_report'
SNAPSHOT = 'snapshot'
GENERATION = 'generation'
SNAP_ID = 'snapid'
RDFG = 'rdf_group'
RDF_GROUP = 'rdf_group'
GB_HEADROOM = 'gbHeadroom'
RDF_DIRECTOR = 'rdf_director'
REMOTE_PORT = 'remote_port'
ALERT = 'alert'
ALERT_SUMMARY = 'alert_summary'
COMPLIANCE = 'compliance'

# Status Codes
STATUS_200 = 200
STATUS_201 = 201
STATUS_202 = 202
STATUS_204 = 204
STATUS_401 = 401
STATUS_404 = 404

# Job constants
INCOMPLETE_LIST = ['created', 'scheduled', 'running',
                   'validating', 'validated']
CREATED = 'created'
SUCCEEDED = 'succeeded'
ASYNCHRONOUS = 'ASYNCHRONOUS'
ASYNC_UPDATE = {'executionOption': ASYNCHRONOUS}
CREATE_VOL_STRING = 'Creating new Volumes'

# Replication Modes
ASYNCHRONOUS_CC = 'Asynchronous'
ADAPTIVE_COPY = 'AdaptiveCopyDisk'
DISABLECONSISTENCY = 'DisableConsistency'
ENABLECONSISTENCY = 'EnableConsistency'
ESTABLISH = 'Establish'
FAILBACK = 'Failback'
FAILOVER = 'Failover'
RECOVER = 'Recover'
RESTORE = 'Restore'
RESUME = 'Resume'
SETBIAS = 'SetBias'
SETMODE = 'SetMode'
SPLIT = 'Split'
SUSPEND = 'Suspend'
SWAP = 'Swap'
UPDATE_R1 = 'UpdateR1'
# RDFG Constants

RDFG_ACTIONS = {
    'MOVE': 'Move', 'ADD_PORTS': 'add_ports',
    'REMOVE_PORTS': 'remove_ports', 'SET_LABEL': 'set_label'}
METRO_DR_ACTIONS = {
    'ESTABLISH': ESTABLISH, 'SPLIT': SPLIT, 'SUSPEND': SUSPEND,
    'RECOVER': RECOVER, 'RESTORE': RESTORE, 'FAILOVER': FAILOVER,
    'FAILBACK': FAILBACK, 'SETMODE': SETMODE, 'UPDATER1': UPDATE_R1
}
METRO_DR_ACTION_PARAMS = {
    'ESTABLISH': 'establish', 'SPLIT': 'split', 'SUSPEND': 'suspend',
    'RESTORE': 'restore', 'FAILOVER': 'failover',
    'FAILBACK': 'failback', 'SETMODE': 'set_mode', 'UPDATER1': 'update_r1'
}

METRO_DR_REPLICATION_MODE = {'ADAPTIVECOPYDISK': 'AdaptiveCopyDisk',
                             'ASYNCHRONOUS': 'Asynchronous'}

# Director constants
DIRECTOR_ID = 'directorId'
PORT_ID = 'portId'
SYMMETRIX_PORT_KEY = 'symmetrixPortKey'
NUM_OF_PORTS = 'num_of_ports'
NUM_OF_CORES = 'num_of_cores'
IP_INTERFACE = 'ipinterface'
IP_INTERFACE_ID = 'ipInterfaceId'

# Host constants
HOST_ID = 'hostId'
ENABLED_FLAGS = 'enabled_flags'
CONSISTENT_LUN = 'consistent_lun'
NUM_OF_INITIATORS = 'num_of_initiators'
HOST_LUN_ADDRESS = 'host_lun_address'
OVERRIDE = 'override'
ENABLED = 'enabled'
TRUE = 'true'
FALSE = 'false'
SPC2_PROTOCOL_VERSION = 'spc2_protocol_version'
SPC2_PROTOCOL_VERSION_FLAG = 'SPC2_Protocol_Version(SPC2)'
SCSI_3 = 'scsi_3'
SCSI_3_FLAG = 'SCSI_3(SC3)'
OPENVMS = 'openvms'
OPENVMS_FLAG = 'OpenVMS(OVMS)'
AVOID_RESET_BROADCAST = 'avoid_reset_broadcast'
AVOID_RESET_BROADCAST_FLAG = 'Avoid_Reset_Broadcast(ARB)'
VOLUME_SET_ADDRESSING = 'volume_set_addressing'
HOST_FLAGS = {
    'disable_q_reset_on_ua': {
        OVERRIDE: FALSE, ENABLED: FALSE},
    'environ_set': {
        OVERRIDE: FALSE, ENABLED: FALSE},
    VOLUME_SET_ADDRESSING: {
        OVERRIDE: FALSE, ENABLED: FALSE},
    'spc2_protocol_version': {
        OVERRIDE: FALSE, ENABLED: FALSE},
    'scsi_support1': {
        OVERRIDE: FALSE, ENABLED: FALSE},
    OPENVMS: {
        OVERRIDE: FALSE, ENABLED: FALSE},
    AVOID_RESET_BROADCAST: {
        OVERRIDE: FALSE, ENABLED: FALSE},
    SCSI_3: {
        OVERRIDE: TRUE, ENABLED: TRUE},
    CONSISTENT_LUN: FALSE}

# Host Group constants
NUM_OF_HOSTS = 'num_of_hosts'
HOST_GROUP = 'host_group'
HOST_GROUP_ID = 'hostGroupId'

# SRP constants
SRP_CAPACITY = 'srp_capacity'
SRP_EFFICIENCY = 'srp_efficiency'
STORAGE_GROUP_DEMAND = 'storage_group_demand'
SRP_ID = 'srpId'
NUM_OF_DISK_GROUPS = 'num_of_disk_groups'
RESERVED_CAP_PERCENT = 'reserved_cap_percent'
TOTAL_SRDF_DSE_ALLOCATED_CAP_GB = 'total_srdf_dse_allocated_cap_gb'
RDFA_DSE = 'rdfa_dse'
DISK_GROUP_ID = 'diskGroupId'

# Storage Group constants
STORAGE_GROUP_ID_CAMEL = 'storageGroupId'
STORAGE_GROUP_ID = 'storage_group_id'
NUM_OF_CHILD_SGS = 'num_of_child_sgs'
SERVICE_LEVEL = 'service_level'
BASE_SLO_NAME = 'base_slo_name'
SLO_COMPLIANCE = 'slo_compliance'
NUM_OF_VOLS = 'num_of_vols'
NUM_OF_PARENT_SGS = 'num_of_parent_sgs'
NUM_OF_MASKING_VIEWS = 'num_of_masking_views'
NUM_OF_SNAPSHOTS = 'num_of_snapshots'
DEVICE_EMULATION = 'device_emulation'
UNPROTECTED = 'unprotected'
COMPRESSION = 'compression'

# Port Group constants
PORT_GROUP = 'port_group'
PORT_GROUP_ID = 'portGroupId'

# Masking View constants
MASKING_VIEW_ID = 'maskingViewId'

# Volume constants
VOLUME_ID_CAMEL = 'volumeId'
VOLUME_ID = 'volume_id'
DEVICE_ID = 'device_id'
CAP_GB = 'cap_gb'
ALLOCATED_PERCENT = 'allocated_percent'
VOLUME_IDENTIFIER = 'volume_identifier'
VOLUME_NAME = 'volume_name'
WWN = 'wwn'
EFFECTIVE_WWN = 'effective_wwn'
HAS_EFFECTIVE_WWN = 'has_effective_wwn'
EMULATION = 'emulation'
TYPE = 'type'
SSID = 'ssid'
CAP_MB = 'cap_mb'
CAP_CYL = 'cap_cyl'
STATUS = 'status'
RESERVED = 'reserved'
PINNED = 'pinned'
ENCAPSULATED = 'encapsulated'
NUM_OF_FRONT_END_PATHS = 'num_of_front_end_paths'
SNAPVX_SOURCE = 'snapvx_source'
SNAPVX_TARGET = 'snapvx_target'
MOBILITY_ID_ENABLED = 'mobility_id_enabled'

# SLO constants
SLO_ID = 'sloId'
NUM_OF_STORAGE_GROUPS = 'num_of_storage_groups'

# Initiator constants
INITIATOR_ID = 'initiatorId'
LOGGED_IN = 'logged_in'
ALIAS = 'alias'
ON_FABRIC = 'on_fabric'
FCID = 'fcid'

# Regex search pattern constants
DIRECTOR_SEARCH_PATTERN = '\\w{2}-\\w{2}'
PORT_SEARCH_PATTERN = '\\d{1,3}'
WWN_SEARCH_PATTERN_16 = '[0-9a-fA-F]{16}'
WWN_SEARCH_PATTERN_32 = '[0-9a-fA-F]{32}'
ISCSI_IQN_SEARCH_PATTERN = (
    '^iqn.\\d{1,4}-\\d{2}.(?:com|org).\\w{1,}:(?:\\d{2}:)*'
    '[0-9a-fA-F]{1,32}$||.[0-9A-Fa-f]{16}')
non_iscsi_initiator_pattern = '{d}:{p}:{w}'.format(
    d=DIRECTOR_SEARCH_PATTERN, p=PORT_SEARCH_PATTERN,
    w=WWN_SEARCH_PATTERN_16)
iscsi_initiator_pattern = '{d}:{p}:{pa}'.format(
    d=DIRECTOR_SEARCH_PATTERN, p=PORT_SEARCH_PATTERN,
    pa=ISCSI_IQN_SEARCH_PATTERN)
INITIATOR_SEARCH_PATTERN = '{ni}|{i}'.format(
    ni=non_iscsi_initiator_pattern, i=iscsi_initiator_pattern)

# QOS constants
HOST_IO_LIMIT = 'hostIOLimit'
MAX_MBPS = 'maxMBPS'
DISTRIBUTION_TYPE = 'DistributionType'
HOST_IO_LIMIT_IO_SEC = 'host_io_limit_io_sec'
HOST_IO_LIMIT_MB_SEC = 'host_io_limit_mb_sec'
DYNAMIC_DISTRIBUTION = 'dynamicDistribution'

# System Health / Disk Checks
HEALTH = 'health'
HEALTH_CHECK = 'health_check'
FAILED = 'failed'
DISK = 'disk'
TAG = 'tag'
DESCRIPTION = 'description'
ARRAY_ID = 'array_id'
TAG_NAME = 'tag_name'
SG_ID = 'storage_group_id'
SG_NUM = 'num_of_storage_groups'
ARRAY_NUM = 'num_of_arrays'
HEALTH_SCORE = 'health_score_metric'
HEALTH_CHECK_ID = 'health_check_id'
TEST_RES = 'testResult'
JOB_ID = 'jobId'
RES_LINK = 'resourceLink'
NAME = 'name'
DISK_IDS = 'disk_ids'
SPINDLE_ID = 'spindle_id'
VENDOR = 'vendor'
CAPACITY = 'capacity'
ALERT_SUMMARY_KEYS = ['alert_count', 'all_unacknowledged_count',
                      'fatal_unacknowledged_count',
                      'critical_unacknowledged_count',
                      'warning_unacknowledged_count',
                      'info_unacknowledged_count',
                      'minor_unacknowledged_count',
                      'normal_unacknowledged_count',
                      'all_acknowledged_count', 'fatal_acknowledged_count',
                      'critical_acknowledged_count',
                      'warning_acknowledged_count',
                      'info_acknowledged_count', 'minor_acknowledged_count',
                      'normal_acknowledged_count']
SNAPSHOT_POLICY_INTERVALS = ['10 Minutes', '12 Minutes', '15 Minutes',
                             '20 Minutes', '30 Minutes', '1 Hour',
                             '2 Hours', '3 Hours', '4 Hours', '6 Hours',
                             '8 Hours', '12 Hours', '1 Day', '7 Days']
ASSOCIATE_TO_STORAGE_GROUPS = 'AssociateToStorageGroups'
DISASSOCIATE_FROM_STORAGE_GROUPS = 'DisassociateFromStorageGroups'
SNAPSHOT_POLICY = 'snapshot_policy'
SNAPSHOT_POLICY_NAME_FOR_TEST = 'DailyDefault'
MODIFY_POLICY = 'Modify'
SUSPEND_POLICY = 'Suspend'
RESUME_POLICY = 'Resume'
SNAPSHOT_POLICY_ACTIONS = [MODIFY_POLICY, SUSPEND_POLICY, RESUME_POLICY,
                           ASSOCIATE_TO_STORAGE_GROUPS,
                           DISASSOCIATE_FROM_STORAGE_GROUPS]

# Import/Export Settings
SETTINGS_FILENAME_TEMPLATE = 'PyU4V-SettingsExport'
SETTINGS = 'settings'
EXPORT_FILE = 'exportfile'
IMPORT_FILE = 'importfile'
SRC_ARRAY = 'source_array'
TGT_ARRAYS = 'target_arrays'
FILE_PASSWORD = 'file_password'
ZIP_FILE = 'zip_file'
ZIP_SUFFIX = '.zip'
PDF_SUFFIX = '.pdf'
FILE_READ_MODE = 'rb'
FILE_WRITE_MODE = 'wb'
ALL_SETTINGS = 'all'
EXCLUDE_UNI_SETTINGS = 'exclude_unisphere_setting_options'
EXCLUDE_SYS_SETTINGS = 'exclude_system_setting_options'
UNI_ALERT_SETTINGS = 'alert_notification_settings'
UNI_PERF_PREF_SETTINGS = 'performance_preference_settings'
UNI_PERF_USER_SETTINGS = 'performance_user_templates'
UNI_PERF_METRIC_SETTINGS = 'performance_metric_settings'
SYS_ALERT_SETTINGS = 'alert_policy_settings'
SYS_ALERT_NOTIFI_SETTINGS = 'alert_level_notification_settings'
SYS_THRESH_SETTINGS = 'system_threshold_settings'
SYS_PERF_THRESH_SETTINGS = 'performance_threshold_settings'

# Audit Log Constants
AUDIT_LOG_FILENAME_TEMPLATE = 'PyU4V-AuditLogRecord'
AUDIT_LOG_FILENAME = 'auditlogfilename'
AUDIT_RECORD_PATH = 'audit_record_path'
AUDIT_LOG_RECORD = 'audit_log_record'
AUDIT_RECORD_TIME = 'audit_record_time'
BINARY_DATA = 'binary_data'
RECORD_ID = 'record_id'
HOST_NAME = 'hostname'
CLIENT_HOST = 'client_host'
MESSAGE = 'message'
ACTIVITY_ID = 'activity_id'
APP_ID = 'application_id'
APP_VERSION = 'application_version'
TASK_ID = 'task_id'
PROCESS_ID = 'process_id'
VENDOR_ID = 'vendor_id'
OS_TYPE = 'os_type'
OS_REV = 'os_revision'
API_LIB = 'api_library'
API_VER = 'api_version'
AUDIT_CLASS = 'audit_class'
ACTION_CODE = 'action_code'
FUNC_CLASS = 'function_class'
SUCCESS = 'success'
COUNT = 'count'

# Date/Time
STR_TIME_FORMAT = '%Y%m%d%H%M%S'
