import streamlit as st
from core import Rectangle, CrossSection

def get_geometry():
    if "geometry" not in st.session_state:
        st.session_state.geometry = CrossSection()
    return st.session_state.geometry

def display_geometry_input():
    st.sidebar.title("Bridge Geometry")

    st.subheader("Build the Cross-Section")

    geometry = get_geometry()

    # Input fields to add a rectangle
    width = st.number_input("Width (mm)", min_value=1.0, value=100.0, key="width_input")
    height = st.number_input("Height (mm)", min_value=1.0, value=50.0, key="height_input")
    position = st.number_input("Position from bottom (mm)", value=0.0, key="position_input")

    # Add Rectangle button
    if st.button("Add Rectangle"):
        if width and height and position is not None:
            new_rect = Rectangle(width=width, height=height, position=position)
            geometry.add_rectangle(new_rect)
            st.success(f"Added rectangle: {new_rect}")
        else:
            st.warning("Please provide valid values for all inputs.")

    # Show current rectangles in the cross-section
    st.subheader("Current Rectangles")
    if geometry.rectangles:
        for idx, rect in enumerate(geometry.rectangles):
            st.write(f"Rectangle {idx+1}: {rect}")
    else:
        st.write("No rectangles added yet.")

    # Calculate and display total area and centroid
    st.subheader("Cross-Section Calculations")
    if geometry.rectangles:
        total_area = geometry.calculate_total_area()
        centroid_y = geometry.calculate_centroid()
        moment_of_inertia = geometry.calculate_moment_of_inertia()

        st.write(f"Total Area: {total_area} mm²")
        st.write(f"Centroid Position (Y): {centroid_y} mm")
        st.write(f"Total Moment of Inertia: {moment_of_inertia} mm⁴")
    else:
        st.write("Add some rectangles to calculate the area and centroid.")

    return geometry