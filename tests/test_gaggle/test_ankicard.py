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
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# Bug when using open() with **kwargs. Fixed in 2.17.5
# pylint: disable=unspecified-encoding
import collections
import csv
import io

import pytest
import pytest_cases as pyc

from gaggle import gaggle

TSV_FILE_ENCODING = gaggle._ANKI_EXPORT_ENCODING
TSV_FILE_DIALECT = gaggle._ANKI_EXPORT_CONTENT_DIALECT
EXCLUSIVE_OPEN_PARAMS = gaggle.EXCLUSIVE_OPEN_PARAMS
READ_PARAMS = gaggle.READ_PARAMS
WRITE_PARAMS: gaggle.OpenOptions = {
    'mode': 'w',
    'encoding': TSV_FILE_ENCODING,
    'newline': ''
}


@pytest.fixture
def number_of_fields():
  return 10


@pytest.fixture
def generic_fields(number_of_fields):
  return [f'value{field_idx}' for field_idx in range(number_of_fields)]


@pytest.fixture
def generic_field_names(number_of_fields):
  return [f'field{field_idx}' for field_idx in range(number_of_fields)]


@pytest.fixture
def has_html_true():
  return 'true'


@pyc.fixture
def has_html_false():
  return 'false'


@pyc.fixture
def generic_tags_idx(number_of_fields):
  return number_of_fields - 1


@pyc.fixture
def generic_note_type_idx():
  return 1


@pyc.fixture
def generic_deck_idx():
  return 2


@pyc.fixture
def generic_guid_idx():
  return 0


@pyc.parametrize('fields', [generic_fields])
@pyc.parametrize('field_names', [None, generic_field_names])
@pyc.parametrize('has_html', [has_html_false, has_html_true])
@pyc.parametrize('tags_idx', [None, generic_tags_idx])
@pyc.parametrize('note_type_idx', [None, generic_note_type_idx])
@pyc.parametrize('deck_idx', [None, generic_deck_idx])
@pyc.parametrize('guid_idx', [None, generic_guid_idx])
def test_anki_card_init_generic_arguments(fields, field_names, has_html,
                                          tags_idx, note_type_idx, deck_idx,
                                          guid_idx):
  card = gaggle.AnkiCard(fields, field_names, has_html, tags_idx, note_type_idx,
                         deck_idx, guid_idx)
  assert card


@pyc.fixture
def anki_card_generic_fully_formed(generic_fields, generic_field_names,
                                   has_html_false, generic_tags_idx,
                                   generic_note_type_idx, generic_deck_idx,
                                   generic_guid_idx):
  return gaggle.AnkiCard(generic_fields, generic_field_names, has_html_false,
                         generic_tags_idx, generic_note_type_idx,
                         generic_deck_idx, generic_guid_idx)


@pyc.fixture
@pyc.parametrize('reserved_name', ['Tags', 'Deck', 'Note Type', 'GUID'])
def anki_card_reserved_names_field_names(reserved_name):
  """These names are guaranteed by the public API. They cannot be assigned
  manually (passed as field_names), cannot be duplicated (used in field_names
  and specified by argument), and each is accessible as a property."""
  return reserved_name


@pyc.fixture
@pyc.parametrize('reserved_name', ['tags', 'deck_name', 'note_type', 'guid'])
def anki_card_reserved_names_property_names(reserved_name):
  """These names are guaranteed by the public API. They cannot be assigned
  manually (passed as field_names), cannot be duplicated (used in field_names
  and specified by argument), and each is accessible as a property."""
  return reserved_name


@pyc.parametrize('reserved_name', [anki_card_reserved_names_property_names])
def test_reserved_names_specified_returns_value(anki_card_generic_fully_formed,
                                                reserved_name):
  assert hasattr(anki_card_generic_fully_formed, reserved_name)


@pyc.fixture
def anki_card_generic_fields(generic_fields):
  return gaggle.AnkiCard(generic_fields)


@pyc.parametrize('reserved_name', [anki_card_reserved_names_property_names])
def test_reserved_names_not_specified_raises_key_error(anki_card_generic_fields,
                                                       reserved_name):
  with pytest.raises(KeyError):
    hasattr(anki_card_generic_fields, reserved_name)


@pyc.fixture
def generic_field_name_string_base():
  return 'Field'


def test_get_field_existing_field(anki_card_generic_fields,
                                  generic_field_name_string_base,
                                  generic_guid_idx, generic_fields):
  assert (anki_card_generic_fields.get_field(
      f'{generic_field_name_string_base}{generic_guid_idx}') ==
          generic_fields[generic_guid_idx])


def test_get_field_non_existing_field(anki_card_generic_fields):
  with pytest.raises(KeyError):
    anki_card_generic_fields.get_field(None)


def test_as_str_list_content_matches(anki_card_generic_fields, generic_fields):
  test_set = collections.Counter(anki_card_generic_fields.as_str_list())
  expected_set = collections.Counter(generic_fields)
  assert test_set == expected_set


def test_as_str_list_order_matches(anki_card_generic_fields, generic_fields):
  assert anki_card_generic_fields.as_str_list() == generic_fields


def test_write_as_tsv_csv_writer_one_line(tmp_path, anki_card_generic_fields,
                                          generic_fields):
  file = tmp_path / 'test_write_as_tsv_csv_writer_one_line.txt'
  with open(file, **WRITE_PARAMS) as f:
    w = csv.writer(f, dialect=TSV_FILE_DIALECT)
    anki_card_generic_fields.write_as_tsv(w)
  with open(file, **READ_PARAMS) as f:
    r = csv.reader(f, dialect=TSV_FILE_DIALECT)
    test_card = next(r)
    assert test_card == generic_fields


def test_write_as_tsv_csv_writer_multiple_lines(tmp_path,
                                                anki_card_generic_fields,
                                                generic_fields):
  file = tmp_path / 'test_write_as_tsv_csv_writer_multiple_lines.txt'
  with open(file, **WRITE_PARAMS) as f:
    w = csv.writer(f, dialect=TSV_FILE_DIALECT)
    anki_card_generic_fields.write_as_tsv(w)
    anki_card_generic_fields.write_as_tsv(w)
  expected_card = generic_fields
  with open(file, **READ_PARAMS) as f:
    r = csv.reader(f, dialect=TSV_FILE_DIALECT)
    for test_card in r:
      assert test_card == expected_card


def test_write_as_tsv_no_write_permission_raises_unsupported_operation(
    tmp_path, anki_card_generic_fields):
  file = tmp_path / ('test_write_as_tsv_no_write_permission_raises_unsupported_'
                     'operation.txt')
  try:
    open(file, **EXCLUSIVE_OPEN_PARAMS)  #pylint: disable='consider-using-with'
  except:  # pylint: disable='bare-except'
    pytest.fail('Test file could not be created. Required to simulate improper '
                'file permissions.')
  with open(file, **READ_PARAMS) as f:
    w = csv.writer(f, dialect=TSV_FILE_DIALECT)
    with pytest.raises(io.UnsupportedOperation):
      anki_card_generic_fields.write_as_tsv(w)


@pyc.parametrize('has_html, expected', [(has_html_false, False),
                                        (has_html_true, True)])
def test_parse_anki_header_bool_valid_input(has_html, expected):
  assert gaggle._parse_anki_header_bool(has_html) == expected


def test_parse_anki_header_bool_invalid_value_raises_value_error():
  with pytest.raises(ValueError):
    gaggle._parse_anki_header_bool('')
