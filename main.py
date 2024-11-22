import streamlit as st
from app.inputs import get_user_inputs, get_glue_locations
from app.studio import display_geometry_input, get_geometry
from app.common import get_geometry, upload_geometry_file, reset_geometry

def main():
    # Title of the application
    st.title("Beam Analysis")

    st.sidebar.subheader("Build Cross Section")
    option = st.sidebar.selectbox("Choose input method:", ("Manual Input", "Upload File"))

    if "mode" not in st.session_state:
        st.session_state.mode = "Manual Input"
    
    if option != st.session_state.mode:
        st.session_state.mode = option
        reset_geometry()

    if option == "Manual Input":
        display_geometry_input()
        # draw_shape()
    else:
        upload_geometry_file()
    
    if st.sidebar.subheader("Cofigure Glue Locations"):
        get_glue_locations()

    _ , _, beam = get_user_inputs()
    beam.cross_section = get_geometry()

    if st.sidebar.button("Perform Analysis"):

        st.subheader("Beam Analysis Results")
        st.write("Reaction forces:")
        st.write(beam.reaction_forces)
        beam.plot_sfd_bmd()
        st.write("Maximum shear force: ", beam.max_shear_force_frame)
        st.write("Maximum bending moment: ", beam.max_bending_moment_frame)

        st.subheader("Stress and Shear Analysis")
        tensile, compressive, FOS_bottom, FOS_top = beam.calculate_max_stress()
        st.write(f"Maximum Tensile Stress: {round(tensile, 2)} N/mm^2")
        st.write(f"Maximum Compressive Stress: {round(compressive, 2)} N/mm^2")
        max_shear, FOS_shear = beam.calculate_shear_stress()
        st.write(f"Maximum Shear Stress: {round(max_shear, 2)} N/mm^2")
        beam.calculate_glue_shear()
        for key, value in beam.shear_stress.items():
            if "glue" in key:
                st.write(f"Glue Location {key}: Shear Stress = {round(value, 2)} N/mm^2")

        st.subheader("Local Buckling Analysis")

        st.subheader("FOS Analysis")
        st.write(f"Factor of Safety (Bottom): {round(FOS_bottom, 2)}")
        st.write(f"Factor of Safety (Top): {round(FOS_top, 2)}")
        st.write(f"Factor of Safety (Shear): {round(FOS_shear, 2)}")
        FOS_glue = beam.calculate_glue_fos()
        st.write(f"Factor of Safety (Glue): {round(FOS_glue, 2)}")
        

    st.sidebar.subheader("SFE and BME") # this computationally expensive, don't do automatically!
    direction = st.sidebar.radio("Select the direction of the train:", ("Left to Right", "Right to Left"))
    if st.sidebar.button("Generate"):
        st.subheader("Shear Force and Bending Moment Envelope")
        st.write("Generating the envelope...")
        if direction == "Left to Right":
            max_positive_shear, max_negative_shear, max_positive_moment, max_negative_monent = beam.generate_sfe_bme(left=True)
            
        else:
            max_positive_shear, max_negative_shear, max_positive_moment, max_negative_monent = beam.generate_sfe_bme(left=False)
        st.table({
                "Parameter": ["Maximum Positive Shear", "Maximum Negative Shear", 
                              "Maximum Positive Moment", "Maximum Negative Moment"],
                "Index": [max_positive_shear[0], max_negative_shear[0], 
                          max_positive_moment[0], max_negative_monent[0]],
                "Value": [max_positive_shear[1], max_negative_shear[1], 
                          max_positive_moment[1], max_negative_monent[1]]
            })
        st.write("Envelope generated successfully.")
        beam.plot_sfe_bme()

        if st.sidebar.button("Stress Shear Analysis"):
            tensile, compressive, FOS_bottom, FOS_top = beam.calculate_max_stress()
            st.write(f"Maximum Tensile Stress: {round(tensile, 1)} N/mm^2")
            st.write(f"Maximum Compressive Stress: {round(compressive, 1)} N/mm^2")
            st.write(f"Factor of Safety (Bottom): {round(FOS_bottom, 1)}")
            st.write(f"Factor of Safety (Top): {round(FOS_top, 1)}")

if __name__ == "__main__":
    main()