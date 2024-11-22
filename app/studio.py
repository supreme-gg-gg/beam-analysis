import streamlit as st
from core import Rectangle
from app.common import get_geometry, save_geometry_to_file

def display_geometry_input():

    geometry = get_geometry()

    # Input fields
    width = st.sidebar.number_input("Width (mm)", min_value=1.0, value=100.0, key="width_input")
    height = st.sidebar.number_input("Height (mm)", min_value=1.0, value=50.0, key="height_input")
    position = st.sidebar.number_input("Position from bottom (mm)", value=0.0, key="position_input")

    # Add and Render Buttons
    add_rectangle = st.sidebar.button("Add Rectangle")
    render_build = st.sidebar.button("Render Build")

    if add_rectangle:
        if width and height and position is not None:
            geometry.add_rectangle(Rectangle(width=width, height=height, position=position))
            st.sidebar.success("Rectangle added.")
        else:
            st.sidebar.warning("Invalid input.")

    if render_build and geometry.rectangles:
        total_area = geometry.calculate_total_area()
        centroid_y = geometry.calculate_centroid()
        moment_of_inertia = geometry.calculate_moment_of_inertia()\

        st.subheader("Cross-Section Geometry")
        st.write(f"Total Area: {total_area} mm²")
        st.write(f"Centroid Position (Y): {centroid_y} mm")
        st.write(f"Total Moment of Inertia: {moment_of_inertia} mm⁴")
    elif render_build:
        st.warning("Add rectangles before rendering.")

    save_geometry_to_file()

