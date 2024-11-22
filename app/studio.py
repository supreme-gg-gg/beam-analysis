import streamlit as st
from streamlit_drawable_canvas import st_canvas
from core import Rectangle, CrossSection
import json

def get_geometry():
    if "geometry" not in st.session_state:
        st.session_state.geometry = CrossSection()
    return st.session_state.geometry

def reset_geometry():
    """Clear the existing geometry in session state."""
    st.session_state.geometry = CrossSection()

def display_geometry_input():
    st.sidebar.subheader("Build the Cross-Section")

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
        moment_of_inertia = geometry.calculate_moment_of_inertia()

        st.write(f"Total Area: {total_area} mm²")
        st.write(f"Centroid Position (Y): {centroid_y} mm")
        st.write(f"Total Moment of Inertia: {moment_of_inertia} mm⁴")
    elif render_build:
        st.warning("Add rectangles before rendering.")

def upload_geometry_file():
    uploaded_file = st.sidebar.file_uploader("Upload JSON file", type=["json"])
    if uploaded_file is not None:
        reset_geometry()
        try:
            data = json.load(uploaded_file)
            geometry = get_geometry()
            for rect_data in data:
                geometry.add_rectangle(Rectangle(
                    width=rect_data["width"],
                    height=rect_data["height"],
                    position=rect_data["position"]
                ))
            st.sidebar.success("Geometry loaded.")
            total_area = geometry.calculate_total_area()
            centroid_y = geometry.calculate_centroid()
            moment_of_inertia = geometry.calculate_moment_of_inertia()

            st.write(f"Total Area: {total_area} mm²")
            st.write(f"Centroid Position (Y): {centroid_y} mm")
            st.write(f"Total Moment of Inertia: {moment_of_inertia} mm⁴") 
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")

def save_geometry_to_file():
    geometry = get_geometry()
    if geometry.rectangles:
        rect_data = [
            {"width": rect.width, "height": rect.height, "position": rect.position}
            for rect in geometry.rectangles
        ]
        json_data = json.dumps(rect_data, indent=4)
        st.sidebar.download_button(
            label="Download Geometry as JSON",
            data=json_data,
            file_name="geometry.json",
            mime="application/json"
        )
    else:
        st.sidebar.warning("No rectangles to save.")

def draw_shape():
    st.sidebar.header("Draw and Modify Geometry")

    cross_section = get_geometry()
    
    # Canvas for drawing
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",  # Transparent fill
        stroke_width=2,
        stroke_color="#000",
        background_color="#FFF",
        update_streamlit=True,
        height=400,
        width=400,
        drawing_mode="rect",
        key="canvas",
    )

    # Add rectangles from canvas to the cross-section object
    if canvas_result.json_data is not None:
        for obj in canvas_result.json_data["objects"]:
            if obj["type"] == "rect":
                width = obj["width"]
                height = obj["height"]
                x = obj["left"]
                y = obj["top"]

                # Convert to bottom-left position (standard)
                position = 400 - y - height  # Invert y for canvas to geometry conversion

                # Avoid duplicates by checking existing rectangles
                exists = any(
                    rect.width == width and rect.height == height and rect.position == position
                    for rect in cross_section.rectangles
                )
                if not exists:
                    cross_section.add_rectangle(Rectangle(width, height, position))

    # Show current rectangles and allow manual modification
    st.sidebar.subheader("Edit Rectangles")
    for idx, rect in enumerate(cross_section.rectangles):
        st.sidebar.write(f"Rectangle {idx + 1}")
        width = st.sidebar.number_input(f"Width {idx + 1} (mm)", value=rect.width, key=f"width_{idx}")
        height = st.sidebar.number_input(f"Height {idx + 1} (mm)", value=rect.height, key=f"height_{idx}")
        x = st.sidebar.number_input(f"X Position {idx + 1} (mm)", value=rect.position, key=f"x_{idx}")
        y = st.sidebar.number_input(f"Y Position {idx + 1} (mm)", value=rect.centroid - rect.height / 2, key=f"y_{idx}")

        if st.sidebar.button(f"Update Rectangle {idx + 1}"):
            rect.width = width
            rect.height = height
            rect.position = y  # Update position (bottom-left corner)

    # Update the canvas visualization
    if st.sidebar.button("Redraw Geometry"):
        st.rerun()

    # Display the geometry
    st.subheader("Cross-Section Geometry")
    st.write(cross_section)