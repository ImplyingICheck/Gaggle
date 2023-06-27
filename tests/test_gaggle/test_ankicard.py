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
import pytest

from gaggle import gaggle

TSV_FILE_ENCODING = gaggle._ANKI_EXPORT_ENCODING


@pytest.fixture
def anki_card(make_anki_export_file_no_header_well_formed_content):
  file_path = make_anki_export_file_no_header_well_formed_content()
  with open(file_path, 'r', encoding=TSV_FILE_ENCODING) as f:
    source = f.readline()
    return source, gaggle.create_cards_from_tsv(source)


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


@pytest.fixture
def has_html_false():
  return 'false'


def test_anki_card_init_fields(generic_fields):
  card = gaggle.AnkiCard(generic_fields)
  assert card


def test_anki_card_init_fields_field_names(generic_fields, generic_field_names):
  card = gaggle.AnkiCard(generic_fields, generic_field_names)
  assert card


def test_anki_card_init_fields_field_names_has_html_true(
    generic_fields, generic_field_names, has_html_true):
  card = gaggle.AnkiCard(generic_fields, generic_field_names, has_html_true)
  assert card


def test_anki_card_init_fields_field_names_has_html_false(
    generic_fields, generic_field_names, has_html_false):
  card = gaggle.AnkiCard(generic_fields, generic_field_names, has_html_false)
  assert card
