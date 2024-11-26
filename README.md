# beam-analysis

Web application-based tool for analyzing beam data using Streamlit, a Python-based web application framework. This tool allows users to input beam specifications, perform structural analysis, and visualize results interactively. 

The implementation is based on the [engineering beam theory](https://en.wikipedia.org/wiki/Euler–Bernoulli_beam_theory) and [thin plate buckling theory](https://en.wikipedia.org/wiki/Buckling#Plate_buckling).

## Installation

To setup the respository and install relevant packages (pip):

```sh
git clone https://github.com/supremegg/beam-analysis.git
cd beam-analysis
pip install -r requirements.txt
```

If you use conda or poetry or any other package managers, simply install `Numpy, Matplotlib, Streamlit`.

## Usage

To launch the webapp:

```sh
streamlit run main.py
```

## Features

The application has a wide variety of features including:

1. Customize your design: speicfy beam length, loading characteristic, and cross-sectional properties
2. Build and save your cross section and glue joints as a JSON for future use
3. Analyze the beam: calculate shear force, bending moment, flexural stress, shear stress
4. Calculate geometric properties such as first and second moment of area and analyse local buckling
5. Display FOS (Factor of Safety) for the beam due to different failure modes
6. Visualize the SF (Shear Force) and BM (Bending Moment) diagrams
7. Visualize the SF (Shear Force) and BM (Bending Moment) envelopes for a live load
8. Generate the failure capacitiy for different failure modes based on SFD and BMD

## Repository Structure

The program is written in standard OOP (Object-Oriented Programming) style. The `core` module contains the main classes and functions for beam analysis, equivalent to backend services. The `app` module contains the Streamlit application components for input handling and output display, equivalent to frontend services.

```plaintext
beam-analysis/
├── main.py                # Main application file for Streamlit
├── requirements.txt       # List of dependencies
├── README.md              # Project documentation
├── assets/                # Design assets (saved JSON files)
├── app/                   # Functions to handle inputs and outputs
│   ├── __init__.py        # Initialization file for the app module
│   ├── common.py          # Common shared helper functions
│   ├── inputs.py          # Input handling components for the app
│   ├── studio.py          # Studio components for designing cross sections
├── core/                  # Beam analysis module
│   ├── __init__.py        # Initialization file for the core module
│   ├── beam.py            # Beam class and major calculations
│   ├── geometry.py        # Cross Section class and utilities
│   └── load.py            # Train load class and utilities
```

## Credits

The program was developed by Jet Chiang (@supreme-gg-gg) for CIV102 course project at the University of Toronto, Engineering Science. Contribution requests should be directed to [my email](mailto:jetjiang.ez@gmail.com). The code is presented "as is", i.e. I am not responsible to deliver future maintenances. 
