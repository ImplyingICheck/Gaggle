"""Base class for Anki card"""
from typing import Protocol, Any, TypeVar
from collections.abc import Iterable


_ANKI_HEADER_TRUE = 'true'
_ANKI_HEADER_FALSE = 'false'

T = TypeVar('T')
class SupportsWriteRow(Protocol[T]):
  def writerow(self, row: Iterable[T]) -> Any: ...


def _generate_field_names(field_names, n_fields):
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


def _generate_field_dict(field_names, fields):
  field_dict = {}
  for idx in range(len(field_names)):
    field_dict[field_names[idx]] = fields[idx]
  return field_dict


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

  def contains_html(self):
    return self.has_html

  def get_tags(self):
    return self.get_field('Tags')

  def get_field_names(self):
    return self.field_names

  def get_note_type(self):
    return self.get_field('Note Type')

  def get_deck_name(self):
    return self.get_field('Deck')

  def get_guid(self):
    return self.get_field('GUID')

  def as_str_list(self):
    str_list = []
    for name in self.get_field_names():
      field_value = self.get_field(name)
      str_list.append(field_value)
    return str_list

  def write_as_tsv(self, w: SupportsWriteRow[str]) -> None:
    content = self.as_str_list()
    w.writerow(content)
