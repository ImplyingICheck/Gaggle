# Copyright 2023 The Gaggle Authors. All Rights Reserved.
#
# This file is part of Gaggle.
#
# Gaggle is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Gaggle is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaggle. If not, see <https://www.gnu.org/licenses/>.
# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
"""Constructs test files used by test_ankicard.py, test_ankideck.py, and
test_gaggle.py"""
import csv
import os.path
import stat
import pathlib

import pytest_cases
import xxhash
from gaggle import gaggle

TEST_FILE_DIRECTORY = pathlib.Path(os.path.join(__file__)).parents[2]
TEST_FILE_DIRECTORY = os.path.join(TEST_FILE_DIRECTORY, 'test_files')
TSV_FILE_EXTENSION = gaggle._ANKI_NOTESINPLAINTEXT_EXT
TSV_FILE_ENCODING = gaggle._ANKI_EXPORT_ENCODING
TSV_FILE_DIALECT = gaggle._ANKI_EXPORT_CONTENT_DIALECT

NUM_FIELDS = 7


def generate_file_hash(file, hash_function=None, blocksize=2**20):
  """Collision resistance of xxh128 is sufficient for our verification needs.
  For more granular collision testing, use haslib.SHA512 as the hash_function"""
  if hash_function is None:
    hash_function = xxhash.xxh128
  x = hash_function()
  with open(file, 'rb') as f:
    while chunk := f.read(blocksize):
      x.update(chunk)
  return x.digest()


def set_file_first(file_or_path1, file_or_path2):
  if not os.path.isfile(file_or_path1) and os.path.isfile(file_or_path2):
    return file_or_path2, file_or_path1
  else:
    return file_or_path1, file_or_path2


def hashes_are_equal(file1, file2, /, helper_function=None, **kwargs):
  """Avoid usage of filecmp and miscellaneous functions from os.path.
  Implementations are not guaranteed across all Linux distributions."""
  file1, file2 = set_file_first(file1, file2)
  file1_is_file = os.path.isfile(file1)
  file2_is_file = os.path.isfile(file2)
  if file1_is_file:
    if helper_function is None:
      helper_function = generate_file_hash
    if file2_is_file:
      file1_hash = helper_function(file1, **kwargs)
      file2_hash = helper_function(file2, **kwargs)
    else:
      file1_hash = helper_function(file1, **kwargs)
      file2_hash = file2
  else:
    file1_hash = file1
    file2_hash = file2
  return file1_hash == file2_hash


def make_read_only_test_file(header=None,
                             content=None,
                             filename='',
                             hash_value=None,
                             **kwargs):
  filename = f'{filename}{TSV_FILE_EXTENSION}'
  path = os.path.join(TEST_FILE_DIRECTORY, filename)
  if hash_value:
    if hashes_are_equal(path, hash_value, **kwargs):
      return path
    else:
      try:
        os.remove(path)
      except FileNotFoundError:
        pass
  with open(path, mode='x', encoding=TSV_FILE_ENCODING, newline='') as f:
    if header:
      f.writelines(header)
    if content:
      w = csv.writer(f, dialect=TSV_FILE_DIALECT)
      w.writerows(content)
  os.chmod(path, stat.S_IREAD)
  return os.path.abspath(path)


def generate_well_formed_header():
  # TODO: Implement using AnkiHeader class once implemented
  # IOBase.writelines() does not provide line terminators
  header_content = [
      '#separator:tab\n', '#html:true\n', '#guid column:1\n',
      '#notetype column:2\n', '#deck column:3\n', '#tags column:7\n'
  ]
  return header_content


def generate_well_formed_ankicard_data(num_cards=20):
  # TODO: Improve logical coupling with generate_well_formed_header. This should
  #    be done using the AnkiHeader as formatting information is stored there.
  rows = [[
      f'card{card_idx}_field{field_idx}' for field_idx in range(NUM_FIELDS)
  ] for card_idx in range(num_cards)]
  return rows


@pytest_cases.fixture
def new_header_gaggle_format():
  contents = [('guid_idx', 0), ('note_type_idx', 1), ('deck_idx', 2),
              ('tags_idx', 6)]
  return dict(contents)


@pytest_cases.fixture
def new_field_names_remove_reserved(new_header_gaggle_format):
  field_names = [f'Field{field_idx}' for field_idx in range(NUM_FIELDS)]
  for index in new_header_gaggle_format.values():
    field_names[index] = ''
  return field_names


@pytest_cases.fixture
def case_anki_export_file_well_formed_header_well_formed_content():
  header = generate_well_formed_header()
  content = generate_well_formed_ankicard_data()
  filename = (
      f'{case_anki_export_file_well_formed_header_well_formed_content.__name__}'
  )
  hash_value = b'\xff\xabU"\x8f\x05sI\xf7\x1ad\xff\x89c\xeb\xfb'
  return make_read_only_test_file(
      header, content, filename=filename, hash_value=hash_value)


@pytest_cases.fixture
def case_anki_export_file_no_header_well_formed_content():
  header = None
  content = generate_well_formed_ankicard_data()
  filename = f'{case_anki_export_file_no_header_well_formed_content.__name__}'
  hash_value = b'B\xb6\xaf\x08\x04\x8fb9\xae\xf1\xd4\xb5\x9b\t,*'
  return make_read_only_test_file(
      header, content, filename=filename, hash_value=hash_value)


@pytest_cases.fixture
def case_anki_export_file_well_formed_header_no_content():
  header = generate_well_formed_header()
  content = None
  filename = f'{case_anki_export_file_well_formed_header_no_content.__name__}'
  hash_value = b'\xf1\\\x966(\x80\x9c\x86>d\x0c\xb8\x94\xf3\x9c\xc4'
  return make_read_only_test_file(
      header, content, filename=filename, hash_value=hash_value)


@pytest_cases.fixture
@pytest_cases.parametrize(
    'value', [None, '', False, 0, ()],
    ids=['None', 'empty_string', 'False', '0', 'empty_tuple'])
def falsy_values_hashable(value):
  return value


@pytest_cases.fixture
@pytest_cases.parametrize(
    'value', [{}, [], set()], ids=['empty_dict', 'empty_list', 'empty_set'])
def falsy_values_unhashable(value):
  return value


@pytest_cases.fixture
@pytest_cases.parametrize('value',
                          [falsy_values_hashable, falsy_values_unhashable])
def falsy_values(value):
  return value
