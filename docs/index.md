---
title: Data Set Publishing Language, Version 2.0
author: Natarajan Krishnaswami
---
# DSPL 2.0
This is the project website for the DSPL 2.0 specification, samples, and related tools.

## Spec

The draft specification is here: [dspl2-spec.html](dspl2-spec.html).

## Related tools

Initial tool and a python library are in the DSPL 2.0 GitHub repository under [`tools/dspl2`](https://github.com/google/dspl/tree/master/tools/dspl2).

* [`dspl2-expand.py`](https://github.com/google/dspl/blob/master/tools/dspl2/scripts/dspl2-expand.py): tool to convert a DSPL 2.0 dataset with CSV references to one with only JSON-LD.
* [`dspl2-validate.py`](https://github.com/google/dspl/blob/master/tools/dspl2/scripts/dspl2-validate.py): tool to do basic validation of a DSPL 2.0 dataset into an HTML file.
* [`dspl2-pretty-print.py`](https://github.com/google/dspl/blob/master/tools/dspl2/scripts/dspl2-pretty-print.py): tool to pretty print a DSPL 2.0 dataset as HTML tables.
* [`dspl2-pretty-print-server.py`](https://github.com/google/dspl/blob/master/tools/dspl2/scripts/dspl2-pretty-print-server.py): local web app of the above.
* [`dspl2`](https://github.com/google/dspl/tree/master/tools/dspl2/dspl2): python library to load, normalize, and expand CSV files in DSPL 2.0 datasets.

## Samples

Examples are in the DSPL 2.0 GitHub repository under [`samples`](https://github.com/google/dspl/tree/master/samples). Currently Eurostat unemployment and Eurostat population density samples include DSPL 2.0 metadata.

## Contributing

To contribute, see the [CONTRIBUTING](CONTRIBUTING.html) file and after submitting a CLA, submit pull requests to the [DSPL GitHub repository](https://github.com/google/dspl)
