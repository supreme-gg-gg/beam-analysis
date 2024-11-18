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

- Add shear analysis using Jarowski equation + shear FOS
- Take into account the glue in shear analysis
- Compute and plot the shear force and bending moment envelope
- Think plate buckling analysis
- Visualization of the failing moment and shear

- Optional: GUI for cross-section selection
- Optional: show the stress profile of the beam (constant)
