# Dataset Publishing Language

## Introduction
**DSPL** stands for **Dataset Publishing Language**. It is a representation
format for both the metadata (information about the dataset, such as its name
and provider, as well as the concepts it contains and displays) and actual data
(the numbers) of datasets. Datasets described in this format can be imported
into the [Google Public Data Explorer](https://www.google.com/publicdata), a
tool that allows for rich, visual exploration of the data.

This site hosts miscellaneous, open source content (i.e., schemas, example
files, and utilities) associated with the DSPL standard. See our [documentation
site](https://developers.google.com/public-data) for more details on what DSPL
is and how to use it.  The utilities in this repository are documented at [this
site](https://developers.google.com/public-data/docs/dspltools).

## Build and install
To build the tools, install `lxml`, then use the `setup.py` script in
`tools/dspltools/`.  You can use pip to install these:
```
pip install -r tools/dspltools/requirements.txt
pip install tools/dspltools
```

# DSPL 2
The draft of the DSPL 2 specification, which replaces the existing XML metadata
format with schema.org markup, can be found at the [DSPL GitHub
page](https://google.github.io/dspl).  The source for the specification is at
[`docs/dspl2-spec.md`](https://github.com/google/dspl/blob/master/docs/dspl2-spec.md).
