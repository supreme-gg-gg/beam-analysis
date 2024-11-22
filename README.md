# beam-analysis

A tool for analyzing beam data. We use Streamlit for Python based web application.

## Installation

```sh
git clone https://github.com/supremegg/beam-analysis.git
cd beam-analysis
pip install -r requirements.txt
```

## Usage

```sh
streamlit run main.py
```

## TODO:

- Think plate buckling analysis
- Visualization of the failing moment and shear

## Note on JSON

When you are building and uploading the bridge cross section by a JSON file, note:

1. We do not yet have horizontal coordinates implemented, so position refers to the height from bottom

2. You must manually calculate all the height, width, position for now

3. The glue refers to the glue between two labelled (ID) rectanlges

4. You need to add up the glue thickness (d) if they are on the same level

> Improvements might be made but it is unlikely to be done soon
