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
# pylint: disable=line-too-long
import collections
import csv
import io
import warnings
from typing import cast

import pytest
import pytest_cases
from .conftest import new_header_gaggle_format, new_field_names_remove_reserved  # pylint: disable=relative-beyond-top-level

from gaggle import gaggle
from gaggle import exceptions

TSV_FILE_ENCODING = gaggle._ANKI_EXPORT_ENCODING
TSV_FILE_DIALECT = gaggle._ANKI_EXPORT_CONTENT_DIALECT
EXCLUSIVE_OPEN_PARAMS = gaggle.EXCLUSIVE_OPEN_PARAMS
READ_PARAMS = gaggle.READ_PARAMS
WRITE_PARAMS: gaggle.OpenOptions = {
    'mode': 'w',
    'encoding': TSV_FILE_ENCODING,
    'newline': ''
}


@pytest_cases.fixture
def number_of_fields():
  return 10


@pytest_cases.fixture
def generic_fields(number_of_fields):
  return [f'value{field_idx}' for field_idx in range(number_of_fields)]


@pytest_cases.fixture
def anki_card_reserved_names():
  return ['Tags', 'Deck', 'Note Type', 'GUID']


@pytest_cases.fixture
def generic_indexes_reserved_names_mapping(
    generic_tags_idx,
    generic_deck_idx,
    generic_note_type_idx,
    generic_guid_idx,
    anki_card_reserved_names,
):
  indexes = [
      generic_tags_idx, generic_deck_idx, generic_note_type_idx,
      generic_guid_idx
  ]
  return dict(zip(indexes, anki_card_reserved_names))


@pytest_cases.fixture
def generic_field_names(number_of_fields):
  field_names = [f'Field{field_idx}' for field_idx in range(number_of_fields)]
  return field_names


@pytest_cases.fixture
def generic_field_names_remove_reserved(generic_field_names,
                                        generic_indexes_reserved_names_mapping):
  field_names = generic_field_names
  for index in generic_indexes_reserved_names_mapping.keys():
    field_names[index] = ''
  return field_names


@pytest_cases.fixture
def generic_field_names_add_reserved(generic_field_names,
                                     generic_indexes_reserved_names_mapping):
  field_names = generic_field_names
  for index, reserved_name in generic_indexes_reserved_names_mapping.items():
    field_names[index] = reserved_name
  return field_names


@pytest_cases.fixture
def has_html_true():
  return 'true'


@pytest_cases.fixture
def has_html_false():
  return 'false'


@pytest_cases.fixture
def generic_tags_idx(number_of_fields):
  return number_of_fields - 1


@pytest_cases.fixture
def generic_note_type_idx():
  return 1


@pytest_cases.fixture
def generic_deck_idx():
  return 2


@pytest_cases.fixture
def generic_guid_idx():
  return 0


@pytest_cases.parametrize('fields', [generic_fields])
@pytest_cases.parametrize('field_names',
                          [None, generic_field_names_remove_reserved])
@pytest_cases.parametrize('has_html', [has_html_false, has_html_true])
@pytest_cases.parametrize('tags_idx', [None, generic_tags_idx])
@pytest_cases.parametrize('note_type_idx', [None, generic_note_type_idx])
@pytest_cases.parametrize('deck_idx', [None, generic_deck_idx])
@pytest_cases.parametrize('guid_idx', [None, generic_guid_idx])
def test_anki_card_init_generic_arguments(
    fields,
    field_names,
    has_html,
    tags_idx,
    note_type_idx,
    deck_idx,
    guid_idx,
):
  card = gaggle.AnkiCard(fields, field_names, has_html, tags_idx, note_type_idx,
                         deck_idx, guid_idx)
  assert card


@pytest_cases.fixture
def anki_card_generic_fully_formed(
    generic_fields,
    generic_field_names_remove_reserved,
    has_html_false,
    generic_tags_idx,
    generic_note_type_idx,
    generic_deck_idx,
    generic_guid_idx,
):
  return gaggle.AnkiCard(generic_fields, generic_field_names_remove_reserved,
                         has_html_false, generic_tags_idx,
                         generic_note_type_idx, generic_deck_idx,
                         generic_guid_idx)


@pytest_cases.fixture
@pytest_cases.parametrize('reserved_name',
                          ['Tags', 'Deck', 'Note Type', 'GUID'])
def anki_card_reserved_names_field_names(reserved_name):
  """These names are guaranteed by the public API. They cannot be assigned
  manually (passed as field_names), cannot be duplicated (used in field_names
  and specified by argument), and each is accessible as a property."""
  return reserved_name


@pytest_cases.fixture
@pytest_cases.parametrize('reserved_name',
                          ['tags', 'deck_name', 'note_type', 'guid'])
def anki_card_reserved_names_property_names(reserved_name):
  """These names are guaranteed by the public API. They cannot be assigned
  manually (passed as field_names), cannot be duplicated (used in field_names
  and specified by argument), and each is accessible as a property."""
  return reserved_name


@pytest_cases.parametrize('reserved_name',
                          [anki_card_reserved_names_property_names])
def test_reserved_names_specified_returns_value(
    anki_card_generic_fully_formed,
    reserved_name,
):
  assert hasattr(anki_card_generic_fully_formed, reserved_name)


@pytest_cases.fixture
def anki_card_generic_fields(generic_fields):
  return gaggle.AnkiCard(generic_fields)


@pytest_cases.parametrize('reserved_name',
                          [anki_card_reserved_names_property_names])
def test_reserved_names_not_specified_raises_key_error(
    anki_card_generic_fields,
    reserved_name,
):
  with pytest.raises(KeyError):
    hasattr(anki_card_generic_fields, reserved_name)


@pytest_cases.fixture
def generic_field_name_string_base():
  return 'Field'


def test_get_field_existing_field(
    anki_card_generic_fields,
    generic_field_name_string_base,
    generic_guid_idx,
    generic_fields,
):
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


def test_write_as_tsv_csv_writer_one_line(
    tmp_path,
    anki_card_generic_fields,
    generic_fields,
):
  file = tmp_path / 'test_write_as_tsv_csv_writer_one_line.txt'
  with open(file, **WRITE_PARAMS) as f:
    w = csv.writer(f, dialect=TSV_FILE_DIALECT)
    anki_card_generic_fields.write_as_tsv(w)
  with open(file, **READ_PARAMS) as f:
    r = csv.reader(f, dialect=TSV_FILE_DIALECT)
    test_card = next(r)
    assert test_card == generic_fields


def test_write_as_tsv_csv_writer_multiple_lines(
    tmp_path,
    anki_card_generic_fields,
    generic_fields,
):
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


@pytest_cases.parametrize('has_html, expected', [(has_html_false, False),
                                                 (has_html_true, True)])
def test_parse_anki_header_bool_valid_input(has_html, expected):
  assert gaggle._parse_anki_header_bool(has_html) == expected


def test_parse_anki_header_bool_invalid_value_raises_value_error():
  with pytest.raises(ValueError):
    gaggle._parse_anki_header_bool('')


@pytest_cases.fixture
def generic_field_dict(generic_field_names, generic_fields):
  test = gaggle._generate_field_dict(generic_field_names, generic_fields)
  return test


def test_generate_field_dict_returns_ordered_dict(generic_field_dict):
  assert isinstance(generic_field_dict, collections.OrderedDict)


def test_generate_field_dict_preserves_order_field_values(
    generic_field_dict, generic_fields):
  for test_value, expected_value in zip(generic_field_dict.values(),
                                        generic_fields):
    assert test_value == expected_value


def test_generate_field_dict_preserves_order_field_names(
    generic_field_dict, generic_field_names):
  for test_value, expected_value in zip(generic_field_dict.keys(),
                                        generic_field_names):
    assert test_value == expected_value


def test_generate_field_dict_mismatched_length_raises_value_error(
    generic_field_names_remove_reserved, generic_fields):
  generic_fields.append('Extend Values By One')
  with pytest.raises(ValueError):
    gaggle._generate_field_dict(generic_field_names_remove_reserved,
                                generic_fields)


@pytest_cases.fixture
def generic_seen_names_set(anki_card_reserved_names):
  return set(anki_card_reserved_names)


def test_anki_card_reserved_names_matches_fixture(
    anki_card_generic_fields,
    anki_card_reserved_names,
):
  assert anki_card_generic_fields._reserved_names == anki_card_reserved_names


@pytest_cases.fixture
def generic_unique_field_names_constructor(
    generic_field_names_remove_reserved,
    generic_fields,
    generic_indexes_reserved_names_mapping,
    generic_seen_names_set,
):

  def generate_unique_field_names(
      *,
      field_names=generic_field_names_remove_reserved,
      fields=generic_fields,
      indexes_reserved_names_mapping=generic_indexes_reserved_names_mapping,
      seen_names_set=generic_seen_names_set,
  ):
    return list(
        gaggle._generate_unique_field_names(field_names, fields,
                                            indexes_reserved_names_mapping,
                                            seen_names_set))

  return generate_unique_field_names


def test_generate_unique_field_names_replaces_field_names(
    generic_unique_field_names_constructor,
    generic_field_names_add_reserved,
):
  expected_field_names = generic_field_names_add_reserved
  assert generic_unique_field_names_constructor() == expected_field_names


def test_generate_unique_field_names_well_formed_no_warnings(
    generic_unique_field_names_constructor,):
  with warnings.catch_warnings():
    warnings.simplefilter('error')
    generic_unique_field_names_constructor()


def test_generate_unique_field_names_longer_field_names_raises_leftover_argument_warning(
    generic_unique_field_names_constructor,
    generic_field_names_remove_reserved,
):
  extended_field_names = generic_field_names_remove_reserved
  extended_field_names.append('This extends field_names by one.')
  with pytest.warns(exceptions.LeftoverArgumentWarning):
    generic_unique_field_names_constructor(field_names=extended_field_names)


def test_generate_unique_field_names_longer_field_names_multiple_extra_raises_one_warning(
    generic_unique_field_names_constructor,
    generic_field_names_remove_reserved,
):
  extended_field_names = generic_field_names_remove_reserved
  extra_field_names = [
      'This extends field_names by one.', 'This extends field_names by two.'
  ]
  extended_field_names.append(extra_field_names[0])
  extended_field_names.append(extra_field_names[1])
  with pytest.warns(exceptions.LeftoverArgumentWarning) as record:
    generic_unique_field_names_constructor(field_names=extended_field_names)
  assert len(record) == 1


def test_generate_unique_field_names_longer_field_names_multiple_extra_returns_all_extra(
    generic_unique_field_names_constructor,
    generic_field_names_remove_reserved,
):
  extended_field_names = generic_field_names_remove_reserved
  extra_field_names = [
      'This extends field_names by one.', 'This extends field_names by two.'
  ]
  extended_field_names.append(extra_field_names[0])
  extended_field_names.append(extra_field_names[1])
  with pytest.warns(exceptions.LeftoverArgumentWarning) as record:
    generic_unique_field_names_constructor(field_names=extended_field_names)
  warning = record[0].message
  warning = cast(exceptions.LeftoverArgumentWarning, warning)
  actual_extra_field_names = warning.leftovers
  expected_extra_field_names = ' '.join(extra_field_names)
  assert actual_extra_field_names == expected_extra_field_names


def test_generate_unique_field_names_mismatched_reserved_name_raises_header_field_name_mismatch_warning(
    generic_field_names_remove_reserved,
    generic_unique_field_names_constructor,
):
  mimatched_reserved_name = generic_field_names_remove_reserved
  mimatched_reserved_name[0] = 'This is not a field name assigned by the header'
  with pytest.warns(exceptions.HeaderFieldNameMismatchWarning):
    generic_unique_field_names_constructor(field_names=mimatched_reserved_name)


def test_generate_unique_field_names_multiple_mismatched_reserved_name_raises_multiple_header_field_name_mismatch_warning(
    generic_field_names_remove_reserved,
    generic_unique_field_names_constructor,
):
  mimatched_reserved_name = generic_field_names_remove_reserved
  mimatched_reserved_name[0] = 'This is not a field name assigned by the header'
  mimatched_reserved_name[1] = 'Also not a field name assigned by the header'
  with pytest.warns(exceptions.HeaderFieldNameMismatchWarning) as record:
    generic_unique_field_names_constructor(field_names=mimatched_reserved_name)
  assert len(record) == 2


def test_generate_unique_field_names_duplicate_reserved_name_raises_duplicate_warning(
    generic_deck_idx,
    generic_unique_field_names_constructor,
    generic_field_names_add_reserved,
):
  duplicate_reserved_name = generic_field_names_add_reserved
  first_index_with_default_field_name = generic_deck_idx + 1
  duplicate_reserved_name[
      first_index_with_default_field_name] = duplicate_reserved_name[0]
  with pytest.warns(exceptions.DuplicateWarning):
    generic_unique_field_names_constructor(field_names=duplicate_reserved_name)


def test_generate_unique_field_names_multiple_duplicate_reserved_name_raises_multiple_duplicate_warning(
    generic_deck_idx,
    generic_unique_field_names_constructor,
    generic_field_names_add_reserved,
):
  duplicate_reserved_name = generic_field_names_add_reserved
  first_index_with_default_field_name = generic_deck_idx + 1
  duplicate_reserved_name[
      first_index_with_default_field_name] = duplicate_reserved_name[0]
  duplicate_reserved_name[first_index_with_default_field_name +
                          1] = duplicate_reserved_name[0]
  with pytest.warns(exceptions.DuplicateWarning) as record:
    generic_unique_field_names_constructor(field_names=duplicate_reserved_name)
  assert len(record) == 2


def test_generate_unique_field_names_duplicate_default_name_after_assignment_raises_duplicate_warning(
    generic_deck_idx,
    generic_unique_field_names_constructor,
    generic_field_names_remove_reserved,
):
  duplicate_default_name = generic_field_names_remove_reserved
  first_index_with_default_field_name = generic_deck_idx + 1
  duplicated_field_name = duplicate_default_name[
      first_index_with_default_field_name]
  duplicate_default_name[first_index_with_default_field_name +
                         1] = duplicated_field_name
  with pytest.warns(exceptions.DuplicateWarning):
    generic_unique_field_names_constructor(field_names=duplicate_default_name)


def test_generate_unique_field_names_multiple_duplicate_default_name_after_assignment_raises_multiple_duplicate_warning(
    generic_deck_idx,
    generic_unique_field_names_constructor,
    generic_field_names_remove_reserved,
):
  duplicate_default_name = generic_field_names_remove_reserved
  first_index_with_default_field_name = generic_deck_idx + 1
  duplicated_field_name = duplicate_default_name[
      first_index_with_default_field_name]
  duplicate_default_name[first_index_with_default_field_name +
                         1] = duplicated_field_name
  duplicate_default_name[first_index_with_default_field_name +
                         2] = duplicated_field_name
  with pytest.warns(exceptions.DuplicateWarning) as record:
    generic_unique_field_names_constructor(field_names=duplicate_default_name)
  assert len(record) == 2


def test_generate_unique_field_names_duplicate_default_name_before_assignment_raises_value_error(
    generic_deck_idx,
    generic_unique_field_names_constructor,
    generic_field_names_remove_reserved,
):
  duplicate_default_name = generic_field_names_remove_reserved
  first_index_with_default_field_name = generic_deck_idx + 1
  duplicated_field_name = duplicate_default_name[
      first_index_with_default_field_name + 1]
  duplicate_default_name[
      first_index_with_default_field_name] = duplicated_field_name
  with pytest.raises(ValueError):
    generic_unique_field_names_constructor(field_names=duplicate_default_name)


def test_generate_unique_field_names_multiple_duplicate_default_name_before_assignment_raises_single_value_error(
    generic_deck_idx,
    generic_unique_field_names_constructor,
    generic_field_names_remove_reserved,
):
  duplicate_default_name = generic_field_names_remove_reserved
  first_index_with_default_field_name = generic_deck_idx + 1
  duplicated_field_name = duplicate_default_name[
      first_index_with_default_field_name + 2]
  duplicate_default_name[
      first_index_with_default_field_name] = duplicated_field_name
  duplicate_default_name[first_index_with_default_field_name +
                         1] = duplicated_field_name
  with pytest.raises(ValueError):
    generic_unique_field_names_constructor(field_names=duplicate_default_name)


@pytest_cases.parametrize('field_names',
                          [None, new_field_names_remove_reserved])
@pytest_cases.parametrize('header', [None, new_header_gaggle_format])
def test_create_cards_from_tsv_well_formed_arguments(
    case_anki_export_file_no_header_well_formed_content, field_names, header):
  # TODO: This is a minimal test suite for create_cards_from_tsv
  #   See: https://github.com/ImplyingICheck/Gaggle/issues/32
  test_file_path = case_anki_export_file_no_header_well_formed_content
  with open(test_file_path, **READ_PARAMS) as f:
    deck = gaggle.create_cards_from_tsv(
        f, field_names=field_names, header=header)
  assert deck
