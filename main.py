import streamlit as st
from app.inputs import get_user_inputs
from app.studio import display_geometry_input

def main():
    # Title of the application
    st.title("Beam Analysis")

    st.sidebar.title("Input Parameters")
    crossSection = display_geometry_input()
    _ , _, beam = get_user_inputs()
    beam.cross_section = crossSection

    if st.sidebar.button("Perform Analysis"):

        st.subheader("Beam Analysis Results")
        st.write("Reaction forces:")
        st.write(beam.reaction_forces)
        beam.plot_sfd_bmd()
        st.write("Maximum shear force: ", beam.max_shear_force_frame)
        st.write("Maximum bending moment: ", beam.max_bending_moment_frame)

        st.subheader("Stress and Shear Analysis")
        tensile, compressive, FOS_bottom, FOS_top = beam.calculate_max_stress()

        st.write(f"Maximum Tensile Stress: {round(tensile, 1)} N/mm^2")
        st.write(f"Maximum Compressive Stress: {round(compressive, 1)} N/mm^2")

        st.subheader("Local Buckling Analysis")

        st.subheader("FOS Analysis")
        st.write(f"Factor of Safety (Bottom): {round(FOS_bottom, 1)}")
        st.write(f"Factor of Safety (Top): {round(FOS_top, 1)}")

    st.sidebar.subheader("SFE and BME") # this computationally expensive, don't do automatically!
    direction = st.sidebar.radio("Select the direction of the train:", ("Left to Right", "Right to Left"))
    if st.sidebar.button("Generate"):
        st.subheader("Shear Force and Bending Moment Envelope")
        st.write("Generating the envelope...")
        if direction == "Left to Right":
            beam.generate_sfe_bme(left=True)
        else:
            beam.generate_sfe_bme(left=False)
        st.write("Envelope generated successfully.")
        beam.plot_sfe_bme()

if __name__ == "__main__":
    main()