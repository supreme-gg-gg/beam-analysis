import sys
import os
# Add the root directory of the project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from inputs import get_user_inputs
from cross_section import display_geometry_input

def main():
    # Title of the application
    st.title("Beam Analysis")

    display_geometry_input()

    _, _, beam = get_user_inputs()

    st.subheader("Train Load Information")
    train_load = beam.Load
    st.write(f"Total train weight: {train_load.total_weight} N")
    st.write(f"Weight per wheel: {train_load.weight_per_wheel} N")
    st.write(f"Wheel positions: {train_load.wheel_positions}")
    st.write(f"Applied loads (position, load): {train_load.get_loads()}")

    st.subheader("Beam Analysis Results")
    st.write("Reaction forces:")
    st.write(beam.reaction_forces)
    beam.plot_sfd_bmd()
    st.write("Maximum shear force: ", beam.max_shear_force)
    st.write("Maximum bending moment: ", beam.max_bending_moment)

    st.subheader("Cross-Section Information")

if __name__ == "__main__":
    main()