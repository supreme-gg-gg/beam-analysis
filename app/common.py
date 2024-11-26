import streamlit as st
import json
from core import Rectangle, CrossSection

def get_geometry():
    """
    Retrieve or initialize the geometry object in the session state.

    This function checks if the "geometry" key exists in the Streamlit session state.
    If it does not exist, it initializes it with a new CrossSection object.
    It then returns the geometry object from the session state.

    Returns:
        CrossSection: The geometry object stored in the session state.
    """
    if "geometry" not in st.session_state:
        st.session_state.geometry = CrossSection()
    return st.session_state.geometry

def reset_geometry():
    """
    Resets the geometry in the Streamlit session state to a new instance of CrossSection.

    This function sets the 'geometry' attribute of the Streamlit session state to a new 
    instance of the CrossSection class, effectively resetting any previous geometry data.
    """
    st.session_state.geometry = CrossSection()

def upload_geometry_file():
    """
    Handles the upload and processing of a JSON file containing geometric data.
    This function allows the user to upload a JSON file via a Streamlit sidebar file uploader.
    It processes the file to extract rectangle and glue connection data, which are then used
    to update the geometry object. The function also calculates and displays the total area,
    centroid position, and moment of inertia of the cross-section geometry.
    The JSON file should have the following structure:
    {
        "rectangles": [
            {
                "width": <float>,
                "height": <float>,
                "position": <tuple>
            },
            ...
        ],
        "glue_connections": [
            {
                "rect1": <int>,
                "rect2": <int>,
                "direction": <str>,
                "thickness": <float>
            },
            ...
        ]
    }
    Raises:
        Exception: If there is an error loading or processing the JSON file.
    Displays:
        - Success message if the geometry and glue connections are loaded successfully.
        - Warning message if no rectangles are found in the uploaded file.
        - Error message if there is an issue with loading the file.
        - Cross-section geometry details including total area, centroid position, and moment of inertia.
    """
    uploaded_file = st.sidebar.file_uploader("Upload JSON file", type=["json"])
    if uploaded_file is not None:
        geometry = get_geometry()
        if not geometry.rectangles:
            try:
                data = json.load(uploaded_file)
                
                # Load Rectangles
                if "rectangles" in data and data["rectangles"]:
                    for rect_data in data["rectangles"]:
                        position_x = rect_data.get("position_x", None)
                        geometry.add_rectangle(Rectangle(
                            width=rect_data["width"],
                            height=rect_data["height"],
                            position=rect_data["position"],
                            position_x=position_x
                        ))
                    
                    # Load Glue Connections if they exist
                    if "glue_connections" in data:
                        for glue_data in data["glue_connections"]:
                            geometry.add_glue_connection(
                                rect1_id=glue_data["rect1"],
                                rect2_id=glue_data["rect2"],
                                direction=glue_data["direction"],
                                thickness=glue_data["thickness"]
                            )
                    
                    st.sidebar.success("Geometry and glue connections loaded.")
                    total_area = geometry.calculate_total_area()
                    centroid_y = geometry.calculate_centroid()
                    centroid_x = geometry.calculate_centroid_x()
                    moment_of_inertia = geometry.calculate_moment_of_inertia()

                    st.subheader("Cross-Section Geometry")
                    st.write(f"Total Area: {total_area} mm²")
                    st.write(f"Centroid Position (Y): {centroid_y} mm")
                    st.write(f"Centroid Position (X): {centroid_x} mm")
                    st.write(f"Total Moment of Inertia: {moment_of_inertia} mm⁴")
                else:
                    st.sidebar.warning("No rectangles found in the uploaded file.")
            except Exception as e:
                st.sidebar.error(f"Error loading file: {e}")

def save_geometry_to_file():
    """
    Saves the current geometry to a JSON file and provides a download button in the Streamlit sidebar.
    The function retrieves the current geometry, which includes rectangles and glue connections.
    If there are any rectangles or glue connections, it converts them into a JSON format and 
    provides a download button in the Streamlit sidebar for the user to download the JSON file.
    If there are no rectangles or glue connections, it displays a warning message in the sidebar.
    The JSON file contains:
    - rectangles: A list of dictionaries, each containing the width, height, and position of a rectangle.
    - glue_connections: A list of dictionaries, each containing the details of a glue connection 
      (rect1, rect2, direction, and thickness).
    Raises:
        None
    Returns:
        None
    """
    geometry = get_geometry()
    if geometry.rectangles or geometry.glue_connections:
        rect_data = [
            {
                "width": rect.width,
                "height": rect.height,
                "position": rect.position,
                "position_x": rect.position_x if hasattr(rect, 'position_x') else None
            }
            for rect in geometry.rectangles
        ]
        glue_data = [
            {"rect1": connection["rect1"], "rect2": connection["rect2"],
             "direction": connection["direction"], "thickness": connection["thickness"]}
            for connection in geometry.glue_connections
        ]
        json_data = json.dumps({
            "rectangles": rect_data,
            "glue_connections": glue_data
        }, indent=4)
        
        st.sidebar.download_button(
            label="Download Geometry as JSON",
            data=json_data,
            file_name="cross_section.json",
            mime="application/json"
        )
    else:
        st.sidebar.warning("No rectangles or glue connections to save.")
