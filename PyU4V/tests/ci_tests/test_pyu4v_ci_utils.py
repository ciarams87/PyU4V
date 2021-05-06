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
"""test_pyu4v_ci_utils.py."""
import configparser
import os
import re
import shutil
import tempfile
import testtools
import time

from pathlib import Path

from PyU4V.tests.ci_tests import base
from PyU4V import univmax_conn
from PyU4V.utils import constants
from PyU4V.utils import decorators
from PyU4V.utils import exception
from PyU4V.utils import file_handler
from PyU4V.utils import time_handler


class CITestUtils(base.TestBaseTestCase, testtools.TestCase):
    """Test Utils.

    PyU4V.conf must exist within the directory ~/.PyU4V in the current users
    home directory for a number of the tests to run without skipping.
    """

    def setUp(self):
        """setUp."""
        super(CITestUtils, self).setUp()
        # Set default denials for file writing functions
        os.umask(0o77)
        # Set the global path to PyU4V.conf
        global_path = os.path.normpath('{home_path}/.PyU4V/PyU4V.conf'.format(
            home_path=os.path.expanduser('~')))
        # If PyU4V.conf exists in the current user's home directory, set config
        # defaults for paths and parse configuration
        if os.path.isfile(global_path):
            self.conf_file = global_path
            self.conf_dir = os.path.dirname(os.path.realpath(self.conf_file))
            self.cfg = configparser.ConfigParser()
            self.cfg.read(self.conf_file)
            self.skip_config_ci = False
        # Else PyU4V.conf is not in user's home directory, skip CI tests for
        # PyU4V.conf placement in multiple locations
        else:
            self.skip_config_ci = True

    # utils.config_handler

    def test_conf_in_current_directory(self):
        """Test config handler with PyU4V in current directory."""
        # Skip test condition
        if self.skip_config_ci:
            self.skipTest(reason='PyU4V.conf not in ~/.PyU4V/')
        # Set the config file temporary name and initialise temp config file
        hidden_conf = os.path.normpath(
            '{dir}/__PyU4V.conf'.format(dir=self.conf_dir))
        temp_file = str()
        try:
            # Make copy of PyU4V.conf to current directory
            temp_file = shutil.copy(self.conf_file, os.getcwd())
            # Rename PyU4V for this test to ensure it isn't loaded by default
            os.rename(self.conf_file, hidden_conf)
            # Create U4VConn using temporary PyU4V.conf in current dir
            temp_u4v_conn = univmax_conn.U4VConn()
            # Perform basic request for Unisphere version, assert successful
            test_request = temp_u4v_conn.common.get_uni_version()
            self.assertTrue(test_request)
            # Cleanup
            self.addCleanup(self.cleanup_files,
                            pyu4v_orig=(self.conf_file, hidden_conf),
                            temp_file=temp_file)
        # If there are any exceptions raised ensure cleanup is carried out on
        # changes to PyU4V.conf
        except Exception as e:
            self.addCleanup(self.cleanup_files,
                            pyu4v_orig=(self.conf_file, hidden_conf),
                            temp_file=temp_file)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_conf_in_user_directory(self):
        """Test config handler with PyU4V in user specified directory."""
        # Skip test condition
        if self.skip_config_ci:
            self.skipTest(reason='PyU4V.conf not in ~/.PyU4V/')
        # Set the config file temporary name and initialise temp config file
        # and temp directory
        hidden_conf = os.path.normpath(
            '{dir}/__PyU4V.conf'.format(dir=self.conf_dir))
        # Initialise path strings for temporary file and directory
        temp_file, temp_dir = str(), str()
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            # Copy source PyU4V.conf to new temporary directory
            temp_file = shutil.copy(self.conf_file, temp_dir)
            # Rename source PyU4V.conf so it cannot be loaded by default
            os.rename(self.conf_file, hidden_conf)
            # Set the filepath to PyU4V.conf in the temporary directory
            univmax_conn.file_path = temp_file
            # Initialise U4VConn and
            temp_u4v_conn = univmax_conn.U4VConn()
            # Perform basic request for Unisphere version, assert successful
            test_request = temp_u4v_conn.common.get_uni_version()
            self.assertTrue(test_request)
            # Cleanup
            # Reset path to PyU4V.conf to None
            univmax_conn.file_path = None
            self.addCleanup(self.cleanup_files,
                            pyu4v_orig=(self.conf_file, hidden_conf),
                            temp_file=temp_file, temp_dir=temp_dir)
        # If there are any exceptions raised ensure cleanup is carried out on
        # changes to PyU4V.conf
        except Exception as e:
            self.addCleanup(self.cleanup_files,
                            pyu4v_orig=(self.conf_file, hidden_conf),
                            temp_file=temp_file, temp_dir=temp_dir)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_logger_configured(self):
        """Test config_handler working logger functionality"""
        # Skip condition - Previous test must have run to ensure that
        # PyU4V.log exists, and DEBUG must be enabled so there are logs output
        # to PyU4V.log before this test runs
        if self.skip_config_ci:
            self.skipTest(reason='PyU4V.conf could not be loaded, not '
                                 'possible to guarantee PyU4V.log existence')
        if 'DEBUG' not in self.cfg.get('logger_PyU4V', 'level'):
            self.skipTest(reason='DEBUG level logging is required for '
                                 'utils.config_handler CI tests')

        # Get the location of PyU4V.log as specified in PyU4V.conf
        log_args = self.cfg.get('handler_fileHandler', 'args').split(',')
        log_path = log_args[0][2:].strip("'")
        # Assert PyU4V.log exists in the location specified in PyU4V.conf
        assert os.path.isfile(os.path.normpath(log_path)) is True
        # Compile regex search pattern for matching the current time (to the
        # minute)
        time_re_search = re.compile(
            r"\A" + time.strftime("%Y-%m-%d")
            + r"\s" + time.strftime("%H:%M") + r":\d{2},\d{3}")
        # Open PyU4V.log file and read the lines withing
        with open(log_path, newline='') as log_file:
            log_lines = log_file.readlines()
            # Search the last line in PyU4V.log
            assert bool(time_re_search.match(log_lines[-1])) is True

    # utils.file_handler

    def test_create_list_from_file(self):
        """Test file_handler.create_list_from_file."""
        # Initialise path strings for temporary file and directory
        temp_dir, file_path = str(), str()
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Create path for temporary file
            file_path = os.path.join(temp_dir, 'temp_list.txt')
            # Initialise empty string and set length of file contents (line
            # count)
            data, list_length = str(), 5
            # Create file contents
            for i in range(0, list_length):
                data += 'value-{i}\n'.format(i=i)
            # Write file contents to the temporary file path
            with open(file_path, 'w') as my_file:
                my_file.writelines(data)
            # Using the file just written to, read contents and return list
            my_list = file_handler.create_list_from_file(file_path)
            # Assert return is a list and of the correct length
            self.assertIsInstance(my_list, list)
            self.assertEqual(list_length, len(my_list))
            # Cleanup temporary files
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
        # If there are any exceptions raised ensure cleanup is carried out on
        # temporary files
        except Exception as e:
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_read_csv_values(self):
        """Test read_csv_values."""
        # Initialise path strings for temporary file and directory
        temp_dir, file_path = str(), str()
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Create path for temporary CSV file
            pyu4v_path = os.path.join(temp_dir, 'temp_spread.csv')
            # Initialise empty string
            data = str()
            # Create file contents
            for i in range(0, 9):
                val = 'key' if i <= 2 else 'value'
                data += '{prefix}-{num}'.format(prefix=val, num=i)
                data += '\n' if (i + 1) % 3 == 0 else ','
            # Write file contents to the temporary file path
            with open(pyu4v_path, 'w') as file:
                file.writelines(data)
            # Using the file just written to, read contents and return dict
            read_contents = file_handler.read_csv_values(pyu4v_path)
            # Assert return is a dict
            self.assertIsInstance(read_contents, dict)
            ref_contents = {'key-0': ['value-3', 'value-6'],
                            'key-1': ['value-4', 'value-7'],
                            'key-2': ['value-5', 'value-8']}
            # Assert CSV reader returned expected populated dict
            self.assertEqual(ref_contents, read_contents)
            # Cleanup temporary files
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=pyu4v_path, temp_dir=temp_dir)
        # If there are any exceptions raised ensure cleanup is carried out on
        # temporary files
        except Exception as e:
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_write_binary_data_to_file(self):
        """Test write_binary_data_to_file provide directory path."""
        response, temp_dir_path = str(), str()
        try:
            temp_u4v_conn = univmax_conn.U4VConn()
            dummy_data = temp_u4v_conn.common.download_file(
                category=constants.SYSTEM, resource_level=constants.SYMMETRIX,
                resource_level_id=temp_u4v_conn.array_id,
                resource_type=constants.AUDIT_LOG_RECORD,
                resource=constants.EXPORT_FILE,
                payload={constants.AUDIT_LOG_FILENAME: 'ci_test'})
            self.assertTrue(dummy_data)

            temp_dir_path = Path(self.create_temp_directory())
            temp_filename = Path('ci_test_dummy_data')
            temp_suffix = constants.PDF_SUFFIX
            temp_pdf_filename = temp_filename.with_suffix(temp_suffix)
            temp_full_path = Path.joinpath(temp_dir_path, temp_pdf_filename)

            response = file_handler.write_binary_data_to_file(
                data=dummy_data, file_extension=temp_suffix,
                file_name=str(temp_filename), dir_path=str(temp_dir_path))
            self.assertTrue(dummy_data)
            self.assertEqual(str(temp_full_path), str(response))
            self.addCleanup(self.cleanup_files, temp_file=str(response),
                            temp_dir=temp_dir_path)

        # If there are any exceptions raised ensure cleanup is carried out on
        # changes to PyU4V.conf
        except Exception as e:
            self.addCleanup(self.cleanup_files, temp_file=str(response),
                            temp_dir=temp_dir_path)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_write_binary_data_to_file_no_dir(self):
        """Test write_binary_data_to_file no directory path."""
        response, temp_dir_path = str(), str()
        try:
            temp_u4v_conn = univmax_conn.U4VConn()
            dummy_data = temp_u4v_conn.common.download_file(
                category=constants.SYSTEM, resource_level=constants.SYMMETRIX,
                resource_level_id=temp_u4v_conn.array_id,
                resource_type=constants.AUDIT_LOG_RECORD,
                resource=constants.EXPORT_FILE,
                payload={constants.AUDIT_LOG_FILENAME: 'ci_test'})
            self.assertTrue(dummy_data)

            temp_dir_path = Path.cwd()
            temp_filename = Path('ci_test_dummy_data')
            temp_suffix = constants.PDF_SUFFIX
            temp_pdf_filename = temp_filename.with_suffix(temp_suffix)
            temp_full_path = Path.joinpath(temp_dir_path, temp_pdf_filename)

            response = file_handler.write_binary_data_to_file(
                data=dummy_data, file_extension=temp_suffix,
                file_name=str(temp_filename))
            self.assertTrue(dummy_data)
            self.assertEqual(str(temp_full_path), str(response))
            self.addCleanup(self.cleanup_files, temp_file=str(response))

        # If there are any exceptions raised ensure cleanup is carried out on
        # changes to PyU4V.conf
        except Exception as e:
            self.addCleanup(self.cleanup_files, temp_file=str(response))
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_write_binary_data_to_file_dir_exception(self):
        """Test invalid directory exception."""
        self.assertRaises(
            exception.InvalidInputException,
            file_handler.write_binary_data_to_file,
            data=None, file_extension=None, file_name=None, dir_path='fake')

    def test_write_to_csv_file(self):
        """Test write_to_csv_file."""
        # Initialise path strings for temporary file and directory
        temp_dir, file_path = str(), str()
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Create path for temporary CSV file
            pyu4v_path = os.path.join(temp_dir, 'temp_spread.csv')
            # Initialise empty string
            data = list()
            # Create file contents
            for i in range(0, 9, 3):
                line = list()
                for x in range(i, i + 3):
                    val = 'key' if i <= 2 else 'value'
                    line.append('{prefix}-{num}'.format(prefix=val, num=x))
                data.append(line)
            # Write file contents to the temporary file path
            file_handler.write_to_csv_file(pyu4v_path, data)
            # Assert the file was created at the path specified
            assert os.path.isfile(pyu4v_path) is True
            # Read the contents of the file just written to
            read_contents = file_handler.read_csv_values(pyu4v_path)
            # Assert file contents are what we expect them to be
            ref_contents = {'key-0': ['value-3', 'value-6'],
                            'key-1': ['value-4', 'value-7'],
                            'key-2': ['value-5', 'value-8']}
            self.assertEqual(ref_contents, read_contents)
            # Cleanup
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=pyu4v_path, temp_dir=temp_dir)
        # If there are any exceptions raised ensure cleanup is carried out on
        # temporary files
        except Exception as e:
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    def test_write_dict_to_csv_file(self):
        """Test write_dict_to_csv_file."""
        data_dict = {'col_1': [1, 2, 3, 4, 5], 'col_2': [6, 7, 8, 9, 10]}
        # Initialise path strings for temporary file and directory
        temp_dir, file_path = str(), str()
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            # Create path for temporary CSV file
            pyu4v_path = os.path.join(temp_dir, 'temp_spread.csv')
            # Write to CSV file, assert file exists
            file_handler.write_dict_to_csv_file(
                pyu4v_path, data_dict, delimiter='#', quotechar='"')
            self.assertTrue(os.path.isfile(pyu4v_path))
            # Read the CSV file and assert contents are equal to data written
            # in previous step
            read_data = file_handler.read_csv_values(
                pyu4v_path, convert=True, delimiter='#', quotechar='"')
            self.assertEqual(data_dict, read_data)
            # Cleanup
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=pyu4v_path, temp_dir=temp_dir)
        # If there are any exceptions raised ensure cleanup is carried out on
        # temporary files
        except Exception as e:
            self.addCleanup(self.cleanup_files, pyu4v_orig=None,
                            temp_file=file_path, temp_dir=temp_dir)
            raise Exception('Test failed with exception: {msg}'.format(msg=e))

    # utils.decorators
    def test_deprecation_notice(self):
        """Test deprecation_notice."""
        # Skip test condition
        if self.skip_config_ci:
            self.skipTest(reason='PyU4V.conf not in ~/.PyU4V/, cannot '
                                 'determine log file location.')
        # Set variables for this test
        c_name, f_name = 'test_class', '_my_test_func'
        start_ver, end_ver = 10, 13

        # Dummy function to test decorator
        @decorators.deprecation_notice(c_name, start_ver, end_ver)
        def _my_test_func():
            pass

        # Get the current date and time (to the current minute)
        c_date = time.strftime('%Y-%m-%d')
        c_time = time.strftime('%H:%M')
        # Create regex search patterns
        reg_time = r'\A' + c_date + r'\s' + c_time + r':\d{2},\d{3}\s-\s'
        reg_lvl = r'PyU4V\.action\_required\s-\sWARNING\s-\s'
        reg_msg = (c_name + r'\.' + f_name + r'[\w\s]{31}' + str(end_ver)
                   + r'\.[\w\s]{46}' + str(start_ver) + r'[\w\s]{14}\.$')
        # Compile regex search query
        time_re_search = re.compile((reg_time + reg_lvl + reg_msg))
        # Run the dummy function to output notice to log file
        _my_test_func()
        # Get the location of PyU4V.log as specified in PyU4V.conf
        log_args = self.cfg.get('handler_fileHandler', 'args').split(',')
        log_path = log_args[0][2:].strip("'")
        # Open PyU4V.log file and read the lines within
        with open(log_path, newline='') as log_file:
            log_lines = log_file.read().splitlines()
            # Slice list to take only 10 most recent log lines
            last_lines = log_lines[-10:]
            # Match last line in PyU4V.log with the regex search pattern
            match = False
            for line in last_lines:
                if bool(time_re_search.match(line)):
                    match = True
            # Assert the regex pattern matched the expected log file contents
            self.assertTrue(match)

    def test_refactoring_notice(self):
        """Test refactoring_notice."""
        # Skip test condition
        if self.skip_config_ci:
            self.skipTest(reason='PyU4V.conf not in ~/.PyU4V/, cannot '
                                 'determine log file location.')
        # Set variables for this test
        c_name, f_name = 'test_class', '_my_test_func'
        f_path = 'PyU4V.path.to.function'
        start_ver, end_ver = 11, 14

        # Dummy function to test decorator
        @decorators.refactoring_notice(c_name, f_path, start_ver, end_ver)
        def _my_test_func():
            pass

        # Get the current date and time (to the current minute)
        c_date = time.strftime('%Y-%m-%d')
        c_time = time.strftime('%H:%M')
        # Create regex search patterns
        reg_time = r'\A' + c_date + r'\s' + c_time + r':\d{2},\d{3}\s-\s'
        reg_lvl = r'PyU4V\.action\_required\s-\sWARNING\s-\s'
        reg_msg = (c_name + r'\.' + f_name + r'[\w\s]{31}' + str(end_ver)
                   + r'[\w\s]{23}' + f_path + r'\.[\w\s]{46}'
                   + str(start_ver) + r'[\w\s]{14}\.$')
        # Compile regex search query
        time_re_search = re.compile((reg_time + reg_lvl + reg_msg))
        # Run the dummy function to output notice to log file
        _my_test_func()
        # Get the location of PyU4V.log as specified in PyU4V.conf
        log_args = self.cfg.get('handler_fileHandler', 'args').split(',')
        log_path = log_args[0][2:].strip("'")
        # Open PyU4V.log file and read the lines within
        with open(log_path, newline='') as log_file:
            log_lines = log_file.read().splitlines()
            # Slice list to take only 10 most recent log lines
            last_lines = log_lines[-10:]
            # Match last line in PyU4V.log with the regex search pattern
            match = False
            for line in last_lines:
                if bool(time_re_search.match(line)):
                    match = True
            # Assert the regex pattern matched the expected log file contents
            self.assertTrue(match)

    # utils.time_handler

    def test_format_time_input_return_seconds_from_seconds(self):
        """Test format_time_input input seconds return seconds."""
        time_now = time.time()
        return_time = time_handler.format_time_input(
            time_in=time_now, return_seconds=True)
        self.assertEqual(int(time_now), return_time)

    def test_format_time_input_return_milliseconds_from_seconds(self):
        """Test format_time_input input seconds return milliseconds."""
        time_now = time.time()
        return_time = time_handler.format_time_input(
            time_in=time_now, return_milliseconds=True)
        self.assertEqual(int(time_now) * 1000, return_time)

    def test_format_time_input_return_seconds_from_milliseconds(self):
        """Test format_time_input input milliseconds return seconds."""
        time_now = int(time.time()) * 1000
        return_time = time_handler.format_time_input(
            time_in=time_now, return_seconds=True)
        self.assertEqual(int(time_now) // 1000, return_time)

    def test_format_time_input_return_milliseconds_from_milliseconds(self):
        """Test format_time_input input milliseconds return milliseconds."""
        time_now = int(time.time()) * 1000
        return_time = time_handler.format_time_input(
            time_in=time_now, return_milliseconds=True)
        self.assertEqual(time_now, return_time)

    def test_format_time_input_type_exception(self):
        """Test format_time_input invalid time type exception."""
        self.assertRaises(
            exception.InvalidInputException,
            time_handler.format_time_input, 'time', True)

    def test_format_time_input_input_exception_all_false(self):
        """Test format_time_input invalid false input type exception."""
        self.assertRaises(
            exception.InvalidInputException,
            time_handler.format_time_input, 123, False, False)

    def test_format_time_input_input_exception_all_true(self):
        """Test format_time_input invalid true input type exception."""
        self.assertRaises(
            exception.InvalidInputException,
            time_handler.format_time_input, 123, True, True)

    def test_iscsi_regex(self):
        import re
        iqn = 'SE-1F:000:iqn.1994-05.com.redhat:338fa4db18b5'
        result = re.match(constants.iscsi_initiator_pattern, iqn)
        self.assertTrue(result)
