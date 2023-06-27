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
"""Constructs test files used by test_ankicard.py, test_ankideck.py, and
test_gaggle.py"""
import os.path

import xxhash


def generate_file_xxh128(file, blocksize=2**20):
  x = xxhash.xxh128()
  with open(file, 'rb') as f:
    while chunk := f.read(blocksize):
      x.update(chunk)
  return x.digest()


def set_file_first(file_or_path1, file_or_path2):
  if not os.path.isfile(file_or_path1) and os.path.isfile(file_or_path2):
    return file_or_path2, file_or_path1
  else:
    return file_or_path1, file_or_path2


def hashes_are_equal(file1, file2, /, hash_function=None, **kwargs):
  """Avoid usage of filecmp and miscellaneous functions from os.path.
  Implementations are not guaranteed across all Linux distributions."""
  file1, file2 = set_file_first(file1, file2)
  file1_is_file = os.path.isfile(file1)
  file2_is_file = os.path.isfile(file2)
  if file1_is_file:
    if hash_function is None:
      hash_function = generate_file_xxh128
    if file2_is_file:
      file1_hash = hash_function(file1, **kwargs)
      file2_hash = hash_function(file2, **kwargs)
    else:
      file1_hash = hash_function(file1, **kwargs)
      file2_hash = file2
  else:
    file1_hash = file1
    file2_hash = file2
  return file1_hash == file2_hash
