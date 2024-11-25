import streamlit as st
from app.studio import get_geometry, save_geometry_to_file
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
    """
    Get the applied loads from the user via Streamlit sidebar inputs.
    This function manages the state of applied loads using Streamlit's session state.
    Users can input the position and magnitude of loads, add them to a list, and remove
    them if needed. The current list of loads is displayed in the sidebar.
    Returns:
        list: A list of tuples where each tuple contains the position (float) and magnitude (float) of a load.
    """
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

def get_train_loads_1():
    """
    Calculate and return the positions and loads of the train wheels for Load Case 1

    Returns:
        TrainLoad: An object containing the following attributes:
            - total_weight (float): The total weight of the train.
            - weight_per_wheel (list of float): The weight distributed to each of the 6 wheels.
            - base_positions (list of int): The hardcoded positions of the wheels in millimeters from the leftmost end.
            - train_position (float): The current position of the train.
    """
    total_weight = get_train_weight()
    train_position = get_train_position()

    # Hardcoded wheel positions (in mm from the leftmost end)
    base_positions = [52, 176, 164, 176, 164, 176]

    # Weight per wheel (assuming the total weight is distributed evenly across the 6 wheels)
    weight_per_wheel = [total_weight / 6] * 6

    return TrainLoad(total_weight=total_weight, weight_per_wheel=weight_per_wheel, base_positions=base_positions, train_position=train_position)

def get_train_loads_2(first_pass=False):
    """
    This function calculates the weight per wheel for a train with a locomotive and two freight cars for Load Case 2.
    The weight of the locomotive is 1.35 times the weight of the freight car with the most load.
    The weight of the freight car at the end is 10% more than the weight of the freight car with the least load.
    Setting first_pass to True will set the two freight cars to have the same load.
    Args:
        first_pass (bool): If True, sets the two freight cars to have the same load. Defaults to False.
    Returns:
        TrainLoad: An object containing the total weight of the train, the weight per wheel, 
                   the base positions of the wheels, and the train position.
    """
    train_position = get_train_position()
    total_weight = get_train_weight()

    base_positions = [52, 176, 164, 176, 164, 176]

    if first_pass:
        freight_mid = total_weight / 3.35
        freight_end = freight_mid
    else:
        freight_mid = total_weight / 3.45 # this is the freight car with the least load
        freight_end = freight_mid * 1.1
        
    locomotive = freight_end * 1.35

    weight_per_wheel = [freight_end/2, freight_end/2, freight_mid/2, freight_mid/2, locomotive/2, locomotive/2]

    return TrainLoad(total_weight=total_weight, weight_per_wheel=weight_per_wheel, base_positions=base_positions, train_position=train_position)

def get_glue_locations():
    """
    Display and manage glue connections between rectangles in a cross-section.
    This function uses Streamlit to create a sidebar interface for selecting two rectangles,
    specifying the glue direction and thickness, and adding the glue connection. It also
    displays existing glue connections in a table format.
    Steps:
    1. Retrieve the cross-section geometry using the `get_geometry` function.
    2. Ensure that the list of rectangles is populated; if not, display a warning.
    3. Provide options to select two rectangles by their IDs, specify the glue direction
       (horizontal or vertical), and input the glue thickness.
    4. Add the glue connection when the "Add Glue" button is pressed.
    5. Display existing glue connections in a table format.
    6. Save the updated geometry to a file.
    Note:
    - Rectangle IDs are displayed as 1-based indices for user convenience but are converted
      to 0-based indices for backend processing.
    - The function assumes the existence of `get_geometry`, `add_glue_connection`, and
      `save_geometry_to_file` functions.
    Returns:
        None
    """
    cross_section = get_geometry()  # Use the existing function to get the geometry
    
    # Ensure the list of rectangles is populated before displaying the glue options
    if not cross_section.rectangles:
        st.sidebar.warning("No rectangles available. Please add some rectangles first.")
        return

    rect1_id = st.sidebar.selectbox("Rectangle 1 ID", options=range(1, len(cross_section.rectangles) + 1))
    rect2_id = st.sidebar.selectbox("Rectangle 2 ID", options=range(1, len(cross_section.rectangles) + 1))
    direction = st.sidebar.radio("Glue Direction", options=["horizontal", "vertical"])
    thickness = st.sidebar.number_input("Glue Thickness (mm):", min_value=0.1, value=1.0, step=0.1)

    st.subheader("Glue Connections")
    if st.sidebar.button("Add Glue"):
        # Adjust to zero-based index for backend
        rect1_id -= 1
        rect2_id -= 1
        
        # Add the glue connection
        cross_section.add_glue_connection(rect1_id, rect2_id, direction, thickness)
        st.success(f"Glue added between R{rect1_id + 1} and R{rect2_id + 1} in {direction} direction with thickness {thickness}.")

    # Display existing glue connections in a table view
    st.write("Existing Glue Connections:")
    if cross_section.glue_connections:
        glue_data = {
            "Rectangle 1 ID": [],
            "Rectangle 2 ID": [],
            "Direction": [],
            "Thickness (mm)": []
        }
        for connection in cross_section.glue_connections:
            # Convert IDs to 1-based for display
            rect1_id = connection['rect1'] + 1
            rect2_id = connection['rect2'] + 1
            glue_data["Rectangle 1 ID"].append(rect1_id)
            glue_data["Rectangle 2 ID"].append(rect2_id)
            glue_data["Direction"].append(connection['direction'])
            glue_data["Thickness (mm)"].append(connection['thickness'])
        
        st.table(glue_data)
    else:
        st.write("No glue connections available.")
    
    save_geometry_to_file()

def get_user_inputs():
    """
    Prompts the user to input beam and train load information via a Streamlit sidebar.
    The function collects the following inputs:
    - Beam length
    - Beam supports
    - Load case (either evenly distributed or increasing load)
    - Train load based on the selected load case and pass type
    Returns:
        tuple: A tuple containing:
            - length (float): The length of the beam.
            - supports (list): A list of supports for the beam.
            - beam (Beam): An instance of the Beam class initialized with the provided inputs.
    """
    
    st.sidebar.subheader("Beam Information")

    length = get_beam_length()
    supports = get_supports()

    st.sidebar.subheader("Train Load Information")

    load_case = st.sidebar.selectbox("Select Load Case", options=["Case 1: evenly distributed", "Case 2: increasing load"])

    if load_case == "Case 1: evenly distributed":
        train_load = get_train_loads_1()
    else:
        first_pass = st.sidebar.radio("Select Pass Type", options=["First Pass", "Subsequent Pass"], index=0)
        if first_pass == "First Pass":
            train_load = get_train_loads_2(first_pass=True)
        else:
            train_load = get_train_loads_2()

    beam = Beam(length, supports, train_load)
    
    return length, supports, beam