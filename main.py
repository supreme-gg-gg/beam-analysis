import streamlit as st
from app.inputs import get_user_inputs, get_glue_locations
from app.studio import display_geometry_input
from app.common import get_geometry, upload_geometry_file, reset_geometry

def main():
    """
    Main function to run the Beam Analysis application using Streamlit.
    The application allows users to:
    - Build a cross section by either uploading a file, manually inputting geometry, 
      or configuring glue.
    - Perform beam analysis to calculate reaction forces, maximum shear force, 
      maximum bending moment, maximum tensile stress, maximum compressive stress, 
      maximum shear stress, and maximum glue shear stress.
    - Display the results of the analysis including stress and shear analysis, 
      local buckling analysis, and factor of safety (FOS) analysis.
    - Generate Shear Force and Bending Moment Envelope (SFE and BME) based on 
      the direction of the train.
    The function handles user inputs, updates session state, and displays results 
    using Streamlit components. Main functionalities are implemented in the 
    imported functions from the `inputs`, `studio`, and `core` modules.
    """
    # Title of the application
    st.title("Beam Analysis")

    st.sidebar.subheader("Build Cross Section")
    option = st.sidebar.selectbox( # this is a dropdown menu
        "Choose input method:", ("Upload File", "Manual Input Geometry", "Configure Glue"))

    if "mode" not in st.session_state: # store the mode in the session state
        st.session_state.mode = "Manual Input Geometry"
    
    if option != st.session_state.mode:
        st.session_state.mode = option
        reset_geometry()

    if option == "Manual Input Geometry":
        display_geometry_input()
        # draw_shape()
    elif option == "Upload File":
        upload_geometry_file()
    else:
        get_glue_locations()

    _ , _, beam = get_user_inputs() # get the beam object
    beam.cross_section = get_geometry()

    if st.sidebar.button("Perform Analysis"): # main analysis to get FOS

        st.subheader("Beam Analysis Results")
        st.write("Reaction forces:")
        st.write(beam.reaction_forces)
        beam.plot_sfd_bmd()
        st.write("Maximum shear force: ", beam.max_shear_force_frame)
        st.write("Maximum bending moment: ", beam.max_bending_moment_frame)

        st.subheader("Stress and Shear Analysis")
        tensile, compressive, FOS_bottom, FOS_top = beam.calculate_max_stress()
        stress_data = { # dictionary to store the stress data
            "Type": ["Maximum Tensile Stress", "Maximum Compressive Stress", "Maximum Shear Stress"],
            "Value (N/mm²)": [round(tensile, 2), round(compressive, 2), None]  # None for shear initially
        }
        max_shear, FOS_shear = beam.calculate_shear_stress()
        stress_data["Value (N/mm²)"][2] = round(max_shear, 2)
        if beam.cross_section.glue_connections:
            beam.calculate_glue_shear()
            max_glue_shear = max(value for key, value in beam.shear_stress.items() if "glue" in key)
            stress_data["Type"].append("Maximum Glue Shear Stress")
            stress_data["Value (N/mm²)"].append(round(max_glue_shear, 2))
            FOS_glue = beam.calculate_glue_fos()
        else:
            FOS_glue = -1
        st.table(stress_data)

        st.subheader("Local Buckling Analysis")

        st.subheader("FOS Analysis") # show FOS in a table
        fos_data = {
            "Component": ["Bottom", "Top", "Shear", "Glue"],
            "Factor of Safety": [
            round(FOS_bottom, 2),
            round(FOS_top, 2),
            round(FOS_shear, 2),
            round(FOS_glue or None, 2)
            ]
        }
        st.table(fos_data)
        

    st.sidebar.subheader("SFE and BME") # this computationally expensive, don't do automatically!
    direction = st.sidebar.radio("Select the direction of the train:", ("Left to Right", "Right to Left"))
    if st.sidebar.button("Generate"):
        st.subheader("Shear Force and Bending Moment Envelope")
        st.write("Generating the envelope...")

        # if direction == "Left to Right":
        #     max_positive_shear, max_negative_shear, max_positive_moment, max_negative_monent = beam.generate_loading_characteristic(left=True)
            
        # else:
        #     max_positive_shear, max_negative_shear, max_positive_moment, max_negative_monent = beam.generate_loading_characteristic(left=False)
        
        # st.table({
        #         "Parameter": ["Maximum Positive Shear", "Maximum Negative Shear", 
        #                       "Maximum Positive Moment", "Maximum Negative Moment"],
        #         "Index": [max_positive_shear[0], max_negative_shear[0], 
        #                   max_positive_moment[0], max_negative_monent[0]],
        #         "Value": [max_positive_shear[1], max_negative_shear[1], 
        #                   max_positive_moment[1], max_negative_monent[1]]
        #     })
        # st.write("Envelope generated successfully.")
        # beam.plot_loading_characteristic()

        if direction == "Left to Right":
            max_shear, min_shear, max_moment, min_moment = beam.generate_sfe_bme(left=True)
        else:
            max_shear, min_shear, max_moment, min_moment = beam.generate_sfe_bme(left=False)
        
        st.table({ # show the results in a table
            "Parameter": ["Maximum Positive Shear", "Maximum Negative Shear", 
                            "Maximum Positive Moment", "Maximum Negative Moment"],
            "Index": [max_shear[0], min_shear[0], 
                        max_moment[0], min_moment[0]],
            "Value": [max_shear[1], min_shear[1], 
                        max_moment[1], min_moment[1]]
        })

if __name__ == "__main__":
    main()