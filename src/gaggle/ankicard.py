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
"""Base class for Anki card"""
import collections
from typing import Protocol, Any, TypeVar, List, OrderedDict
from collections.abc import Iterable
from _csv import Dialect

_ANKI_HEADER_TRUE = 'true'
_ANKI_HEADER_FALSE = 'false'

T = TypeVar('T')
S = TypeVar('S')
class SupportsWriteRow(Protocol[T]):
  @property
  def dialect(self) -> Dialect: ...
  def writerow(self, row: Iterable[T]) -> Any: ...


def _generate_field_names(field_names, n_fields):
  """

  Args:
    field_names: The names which should be set for each delimited field in the
    parsed file. Used for reference, does not modify read contents. Use '' to
    apply a default field name. The length of field_names does not have to match
    the length of the delimited fields. Missing names will be generated with a
    default and extra names will be discarded.
    n_fields: The number of fields contained in the AnkiCard.

  Returns:

  """
  if field_names is None:
    field_names = []
  if len(field_names) == n_fields:
    return field_names
  else:
    range_start = len(field_names)
    range_stop = n_fields
    for idx in range(range_start, range_stop):
      field_names.append(f'Field{idx}')
    return field_names


def _generate_field_dict(field_names: Iterable[T],
                         fields: Iterable[S],
                         ) -> OrderedDict[T, S]:
  """Create a dictionary mapping given names to a value in AnkiCard.

  Args:
    field_names: Names used for referencing values stored in the field dict.
    Special properties exist for fields named by the header.
    Must match the length of fields.
    fields: The values to be stored in an AnkiCard.

  Returns:
    Named values whose iteration order is the same as read from file.
  """
  name_field_tuples = zip(field_names, fields, strict=True)
  return collections.OrderedDict(name_field_tuples)


def _parse_bool(bool_as_str):
  if bool_as_str == _ANKI_HEADER_TRUE:
    return True
  elif bool_as_str == _ANKI_HEADER_FALSE:
    return False
  else:
    return TypeError


class AnkiCard:
  """
  Anki Card fields as denoted by Anki documentation
  Up to date reference:
  https://docs.ankiweb.net/importing.html#file-headers
  Permanent Reference [09 May 2023]:
  https://github.com/ankitects/anki-manual/blob/0aa372146d10e299631e361769f41533a6d4a417/src/importing.md?plain=1#L196-L220
  """
  def __init__(self, fields, has_html=False, tags_idx=None, field_names=None,
               note_type_idx=None, deck_idx=None, guid_idx=None):
    self.has_html = _parse_bool(has_html)
    self.tags_field_idx = tags_idx
    self.note_type_field_idx = note_type_idx
    self.deck_field_idx = deck_idx
    self.guid_field_idx = guid_idx
    self.field_names = _generate_field_names(field_names, len(fields))
    anki_header_names = {'Tags':tags_idx, 'Deck':deck_idx,
                         'Note Type':note_type_idx, 'GUID':guid_idx}
    self._overlay_anki_header_names(anki_header_names)
    self.fields = _generate_field_dict(self.field_names, fields)

  def __repr__(self):
    return str(self.fields)

  def _overlay_anki_header_names(self, anki_header_names):
    for name, field_idx in anki_header_names.items():
      if field_idx is not None:
        self.field_names[field_idx] = name

  def get_field(self, field_name):
    return self.fields[field_name]

  def get_tags(self):
    return self.get_field('Tags')

  def get_note_type(self):
    return self.get_field('Note Type')

  def get_deck_name(self):
    return self.get_field('Deck')

  def get_guid(self):
    return self.get_field('GUID')

  def as_str_list(self) -> List[str]:
    """Return data fields of AnkiCard. Preserves read in order.

    Returns:
      List of strings. Each string is an individual data value stored in
      AnkiCard. The order of the strings is the same order as the AnkiCard was
      read from file.

      Assume a file with three values was read. For example:

      [column0, column1, column2]

    """
    str_list = []
    for name in self.field_names:
      field_value = self.get_field(name)
      str_list.append(field_value)
    return str_list

  def write_as_tsv(self, w: SupportsWriteRow[str]) -> None:
    """Output data fields of AnkiCard in TSV format.

    Requires only a stream to improve reusability as a public API. See
    AnkiDeck.write_as_tsv() for a simpler setup.

    Args:
      w: The stream to write to. Must have internal formatting data.
        See AnkiDeck.write_as_tsv() for an example using csv.writer.
    """
    content = self.as_str_list()
    w.writerow(content)
