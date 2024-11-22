import streamlit as st
from app.studio import get_geometry
from core import TrainLoad, Beam

def get_beam_length():
    """Get the length of the beam from the user."""
    length = st.sidebar.number_input("Beam length (mm):", min_value=1.0, value=1200.0, step=10.0)
    return length

def get_supports():
    """Get the locations of supports from the user."""
    supports = st.sidebar.text_input("Supports (comma separated, e.g., A, B):", value="A,B").split(",")
    return supports

def get_loads():
    """Get the applied loads from the user."""
    if 'loads' not in st.session_state:
        st.session_state.loads = []

    # Input for new load
    load_position = st.sidebar.number_input("Position of load (mm):", min_value=0.0, value=0.0, step=0.1)
    load_magnitude = st.sidebar.number_input("Magnitude of load (N):", min_value=0.0, value=400.0, step=1.0)
    
    # Button to add the load to the list
    if st.sidebar.button("Add Load"):
        st.session_state.loads.append((load_position, load_magnitude))

    # Display current loads
    st.sidebar.write("Current loads:")
    for idx, (position, magnitude) in enumerate(st.session_state.loads):
        st.sidebar.write(f"Load {idx + 1}: {magnitude} N at {position} m")
        if st.sidebar.button(f"Remove Load {idx + 1}", key=f"remove_{idx}"):
            st.session_state.loads.pop(idx)

    return st.session_state.loads

def get_train_weight():
    """Get the total weight of the train from the user."""
    total_weight = st.sidebar.number_input("Total weight of the train (in N):", min_value=0.0, step=100.0, value=400.0)
    return total_weight

def get_train_position():
    """Get the current position of the train on the bridge (in meters)."""
    train_position = st.sidebar.number_input("Train position (in mm from the left end of the bridge):", min_value=-100.0, step=1.0, value=0.0)
    return train_position

def get_train_loads():
    """Calculate and return the positions and loads of the train wheels based on user input."""
    total_weight = get_train_weight()
    train_position = get_train_position()

    # Hardcoded wheel positions (in mm from the leftmost end)
    base_positions = [52, 176, 164, 176, 164, 176]

    # Weight per wheel (assuming the total weight is distributed evenly across the 6 wheels)
    weight_per_wheel = round(total_weight / 6, 2)

    return TrainLoad(total_weight=total_weight, weight_per_wheel=weight_per_wheel, base_positions=base_positions, train_position=train_position)

def get_glue_locations():
    st.subheader("Select Glue Location")
    
    cross_section = get_geometry()  # Use the existing function to get the geometry
    
    # Ensure the list of rectangles is populated before displaying the glue options
    if not cross_section.rectangles:
        st.warning("No rectangles available. Please add some rectangles first.")
        return

    rect1_id = st.selectbox("Rectangle 1 ID", options=range(1, len(cross_section.rectangles) + 1))
    rect2_id = st.selectbox("Rectangle 2 ID", options=range(1, len(cross_section.rectangles) + 1))
    direction = st.radio("Glue Direction", options=["horizontal", "vertical"])
    thickness = st.number_input("Glue Thickness (mm):", min_value=0.1, value=1.0, step=0.1)

    if st.button("Add Glue"):
        # Adjust to zero-based index for backend
        rect1_id -= 1
        rect2_id -= 1
        
        # Add the glue connection
        cross_section.add_glue_connection(rect1_id, rect2_id, direction, thickness)
        st.success(f"Glue added between R{rect1_id + 1} and R{rect2_id + 1} in {direction} direction with thickness {thickness}.")

    # Display existing glue connections
    st.write("Existing Glue Connections:")
    for connection in cross_section.glue_connections:
        # Convert IDs to 1-based for display
        rect1_id = connection['rect1'] + 1
        rect2_id = connection['rect2'] + 1
        st.write(f"R{rect1_id} ↔ R{rect2_id} ({connection['direction']})")

def get_user_inputs():
    
    st.sidebar.subheader("Beam and Load Information")

    length = get_beam_length()
    supports = get_supports()
    train_load = get_train_loads()

    beam = Beam(length, supports, train_load)
    
    return length, supports, beam