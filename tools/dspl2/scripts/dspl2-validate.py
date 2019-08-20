#!/bin/env python3
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from absl import app

from dspl2.filegetter import LocalFileGetter
from dspl2.expander import ExpandStatisticalDataset


def main(args):
  if len(args) != 2:
    print(f'Usage: {args[0]} [DSPL file]', file=sys.stderr)
    exit(1)
  dspl = ExpandStatisticalDataset(LocalFileGetter(args[1]))
  ValidateDspl2(dspl)


if __name__ == '__main__':
  app.run(main)
