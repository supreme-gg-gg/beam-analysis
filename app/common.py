import streamlit as st
import json
from core import Rectangle, CrossSection

def get_geometry():
    if "geometry" not in st.session_state:
        st.session_state.geometry = CrossSection()
    return st.session_state.geometry

def reset_geometry():
    st.session_state.geometry = CrossSection()

def upload_geometry_file():
    uploaded_file = st.sidebar.file_uploader("Upload JSON file", type=["json"])
    if uploaded_file is not None:
        geometry = get_geometry()
        if not geometry.rectangles:
            try:
                data = json.load(uploaded_file)
                
                # Load Rectangles
                if "rectangles" in data and data["rectangles"]:
                    for rect_data in data["rectangles"]:
                        geometry.add_rectangle(Rectangle(
                            width=rect_data["width"],
                            height=rect_data["height"],
                            position=rect_data["position"]
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
                    moment_of_inertia = geometry.calculate_moment_of_inertia()

                    st.subheader("Cross-Section Geometry")
                    st.write(f"Total Area: {total_area} mm²")
                    st.write(f"Centroid Position (Y): {centroid_y} mm")
                    st.write(f"Total Moment of Inertia: {moment_of_inertia} mm⁴")
                else:
                    st.sidebar.warning("No rectangles found in the uploaded file.")
            except Exception as e:
                st.sidebar.error(f"Error loading file: {e}")

def save_geometry_to_file():
    geometry = get_geometry()
    if geometry.rectangles or geometry.glue_connections:
        rect_data = [
            {"width": rect.width, "height": rect.height, "position": rect.position}
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
