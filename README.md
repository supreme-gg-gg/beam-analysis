# beam-analysis

Web application-based tool for analyzing beam data using Streamlit, a Python-based web application framework. This tool allows users to input beam specifications, perform structural analysis, and visualize results interactively.

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

## Features

1. Customize your design: speicfy beam length, loading characteristic, and cross-sectional properties
2. Build and save your cross section and glue joints as a JSON for future use
3. Analyze the beam: calculate shear force, bending moment, flexural stress, shear stress
4. Display FOS (Factor of Safety) for the beam and failure load
5. Visualize the SF (Shear Force) and BM (Bending Moment) diagrams
6. Visualize the SF (Shear Force) and BM (Bending Moment) envelopes for a live load

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
