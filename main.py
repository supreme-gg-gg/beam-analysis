import streamlit as st
from app.inputs import get_user_inputs
from app.studio import display_geometry_input

def main():
    # Title of the application
    st.title("Beam Analysis")

    crossSection = display_geometry_input()

    _, _, beam = get_user_inputs()

    beam.cross_section = crossSection

    if st.button("Perform Analysis"):
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
        tensile, compressive, FOS_bottom, FOS_top = beam.calculate_max_stress()

        st.write(f"Maximum Tensile Stress: {round(tensile, 1)} N/mm^2")
        st.write(f"Maximum Compressive Stress: {round(compressive, 1)} N/mm^2")
        st.write(f"Factor of Safety (Bottom): {round(FOS_bottom, 1)}")
        st.write(f"Factor of Safety (Top): {round(FOS_top, 1)}")

if __name__ == "__main__":
    main()