import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

from config import *

class Beam:
    """
    A class to represent a beam and perform structural analysis.
    """
    def __init__(self, length, supports, loads, cross_section=None):
        self.length = length      # Total length of the beam
        self.supports = supports  # List of support locations (e.g., ['A', 'B'])
        self.Load = loads     # TrainLoad object
        self.Load.bridge_length = length
        self.loads = loads.get_loads()   # List of loads with (location, magnitude)
        self.cross_section = cross_section  # CrossSection object

        # Calculate reaction forces based on applied loads and support locations
        self.reaction_forces = self.calculate_reactions()
        self.shear_forces, self.bending_moments = self.calculate_sfd_bmd()
        self.max_shear_force_frame = max(self.shear_forces)
        self.max_bending_moment_frame = max(self.bending_moments)
        self.shear_forces_max_envelope = []
        self.shear_forces_min_envelope = []
        self.bending_moments_envelope = []
        self.shear_forces_envelope = []
        self.shear_stress = {}
        self.max_shear_force = None
        self.max_bending_moment = None
        self.FOS = {}

    def calculate_reactions(self):
        """
        Calculate the reactions at supports A and B for a simply supported beam.

        This method calculates the reactions at the supports of a simply supported beam
        subjected to point loads. The beam is assumed to be horizontal and the loads
        are applied vertically.

        Returns:
            dict: A dictionary with the reactions at supports A and B.
                  The keys are 'A' and 'B', and the values are the reaction forces at
                  these supports.
        """
        # Total load (sum of all point loads)
        total_load = sum(load[1] for load in self.loads)

        # Calculate the moment about point A to get reaction at B (RB)
        sum_moments_A = sum(load[1] * load[0] for load in self.loads)  # Moment = Load * Distance from A
        RB = sum_moments_A / self.length  # Reaction at B (RB) is total moment divided by the beam length

        # Reaction at A (RA) is the remaining load balance after RB
        RA = total_load - RB

        return {'A': RA, 'B': RB}

    def calculate_sfd_bmd(self):
        """
        Calculate the Shear Force Diagram (SFD) and Bending Moment Diagram (BMD) for the beam.

        This method computes the shear forces and bending moments at discrete points along the length of the beam.
        It first calculates the reactions at the supports and then iterates over each point along the beam to determine
        the shear force and bending moment at that point.

        Returns:
            tuple: A tuple containing two lists:
                - shear_forces (list of float): The shear forces at each point along the beam.
                - bending_moments (list of float): The bending moments at each point along the beam.
        """
        # Initialize lists for shear force and bending moment
        shear_forces = []
        bending_moments = []

        # Calculate reactions first
        reactions = self.calculate_reactions()

        # Loop over each point along the length of the beam
        for x in range(0, int(self.length) + 1):  # From 0 to length of the beam (inclusive)
            # Start by calculating the shear force at the current position
            shear_force = reactions['A']  # Start with the reaction at A

            # Subtract loads that are to the left of the current position
            for load_pos, load_mag in self.loads:
                if load_pos <= x:  # If the load is to the left or at the current position
                    shear_force -= load_mag  # Subtract the load (since it acts downward)

            # Add the shear force to the list
            shear_forces.append(round(shear_force,1))

            # Now calculate the bending moment at the current position
            bending_moment = reactions['A'] * x  # Moment due to reaction at A

            # Subtract moments caused by loads to the left of the current position
            for load_pos, load_mag in self.loads:
                if load_pos <= x:  # Only consider loads to the left or at the current position
                    bending_moment -= load_mag * (x - load_pos)  # Moment = Load * Distance from load

            # Add the bending moment to the list
            bending_moments.append(round(bending_moment,1))

        return shear_forces, bending_moments
    
    def plot_sfd_bmd(self):
        """
        Plots the Shear Force Diagram (SFD) and Bending Moment Diagram (BMD) for the beam.

        This method creates a figure with two subplots:
        - The first subplot displays the Shear Force Diagram (SFD).
        - The second subplot displays the Bending Moment Diagram (BMD).

        The diagrams are plotted using the shear forces and bending moments calculated along the length of the beam.

        The plots are displayed using Streamlit.

        Parameters:
        None

        Returns:
        None
        """

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Plot Shear Force Diagram (SFD)
        ax1.plot(range(0, int(self.length) + 1), self.shear_forces, label='Shear Force')
        ax1.set_title('Shear Force Diagram')
        ax1.set_xlabel('Position along the beam (mm)')
        ax1.set_ylabel('Shear Force (N)')
        ax1.grid(True)
        ax1.legend()

        # Plot Bending Moment Diagram (BMD)
        ax2.plot(range(0, int(self.length) + 1), self.bending_moments, label='Bending Moment', color='r')
        ax2.set_title('Bending Moment Diagram')
        ax2.set_xlabel('Position along the beam (mm)')
        ax2.set_ylabel('Bending Moment (Nmm)')
        ax2.grid(True)
        ax2.legend()

        # Adjust layout with padding between plots
        plt.tight_layout(pad=3.0)

        # Display the plot using Streamlit
        st.pyplot(fig)

    def calculate_max_stress(self):
        """
        Calculate the maximum tensile and compressive stress in the beam and their respective factors of safety (FOS).
        This method calculates the maximum tensile and compressive stress in the beam based on the maximum bending moments
        and the properties of the beam's cross-section. It also calculates the factors of safety for both tensile and 
        compressive stresses.
        Returns:
            tuple: A tuple containing:
                - stress_t (float): Maximum tensile stress in the beam.
                - stress_c (float): Maximum compressive stress in the beam.
                - FOS_t (float): Factor of safety for tensile stress.
                - FOS_c (float): Factor of safety for compressive stress.
        """
        I = self.cross_section.I
        y_t, y_b = self.cross_section.get_max_y()

        stress_c = self.max_bending_moment_frame * y_t / I
        stress_t = self.max_bending_moment_frame * y_b / I

        FOS_c = COMPRESSIVE_STRENGTH / stress_c
        FOS_t = TENSILE_STRENGTH / stress_t

        self.FOS["tensile"] = FOS_t
        self.FOS["compressive"] = FOS_c

        return stress_t, stress_c, FOS_t, FOS_c
    
    @staticmethod
    def _find_extrema(data):
        """Helper function to find max positive and min negative values with indices."""
        max_pos = max(((idx - TRAIN_LENGTH, val) 
                       for idx, val in enumerate(data) if val > 0), default=(None, 0), key=lambda x: x[1])
        min_neg = min(((idx - TRAIN_LENGTH, val) 
                       for idx, val in enumerate(data) if val < 0), default=(None, 0), key=lambda x: x[1])
        
        return max_pos, min_neg
    
    def generate_sfe_bme(self, left=True):
        """
        Generates and plots Shear Force and Bending Moment Diagrams for selected train positions,
        along with envelopes for Shear Force and Bending Moment.

        Parameters:
        - left (bool): If True, move the train from left to right, otherwise from right to left.

        Returns:
        - tuple: Four tuples:
            - (location, max_shear_value)
            - (location, min_shear_value)
            - (location, max_bending_value)
            - (location, min_bending_value)
        """
        self.shear_forces_envelope = []
        self.bending_moments_envelope = []

        # Set the train's starting position
        if left:
            self.Load.set_train_left()
        else:
            self.Load.set_train_right()

        all_positions = range(int(self.length + 1))  # Full beam positions
        shear_force_plots = []
        bending_moment_plots = []

        # Store indices for only a few key plots
        key_plot_indices = []
        step_size = self.length // 3  # Divide into 3 parts: start, middle, end

        while (left and self.Load.wheel_positions[0] <= self.length) or (not left and self.Load.wheel_positions[-1] >= 0):
            # Update the loads for the current train position
            self.loads = self.Load.get_loads()

            # Calculate shear forces and bending moments
            shear_forces, bending_moments = self.calculate_sfd_bmd()

            # Update the envelopes
            if not self.shear_forces_min_envelope or not self.shear_forces_max_envelope:
                self.shear_forces_max_envelope = shear_forces
                self.shear_forces_min_envelope = shear_forces
                self.bending_moments_envelope = bending_moments
            else:
                self.shear_forces_max_envelope = [
                    max(env, sf) for env, sf in zip(self.shear_forces_max_envelope, shear_forces)
                ]
                self.shear_forces_min_envelope = [
                    min(env, sf) for env, sf in zip(self.shear_forces_min_envelope, shear_forces)
                ]
                self.bending_moments_envelope = [
                    max(env, bm) for env, bm in zip(self.bending_moments_envelope, bending_moments)
                ]

            # Add results for key positions
            current_index = self.Load.wheel_positions[0]
            if len(key_plot_indices) < 3 and abs(current_index - (len(key_plot_indices) * step_size)) < 1:
                shear_force_plots.append(shear_forces)
                bending_moment_plots.append(bending_moments)
                key_plot_indices.append(current_index)

            # Move the train incrementally
            if left:
                self.Load.update_load_positions(direction=1)
            else:
                self.Load.update_load_positions(direction=-1)

        # Find extrema with locations
        max_shear_value = max(self.shear_forces_max_envelope)
        min_shear_value = min(self.shear_forces_min_envelope)
        max_shear_location = self.shear_forces_max_envelope.index(max_shear_value)
        min_shear_location = self.shear_forces_min_envelope.index(min_shear_value)

        max_bending_value = max(self.bending_moments_envelope, key=abs)
        min_bending_value = min(self.bending_moments_envelope, key=abs)
        max_bending_location = self.bending_moments_envelope.index(max_bending_value)
        min_bending_location = self.bending_moments_envelope.index(min_bending_value)

        # Plotting
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))

        # Plot only selected SFD and BMD
        for i, (sf, bm) in enumerate(zip(shear_force_plots, bending_moment_plots)):
            ax[0].plot(all_positions, sf, label=f"Train Pos {key_plot_indices[i]}")
            ax[1].plot(all_positions, bm, label=f"Train Pos {key_plot_indices[i]}")

        # Plot the envelopes
        ax[0].plot(all_positions, self.shear_forces_max_envelope, 'r-', linewidth=2, label="SF Envelope (Max)")
        ax[0].plot(all_positions, self.shear_forces_min_envelope, 'r-', linewidth=2, label="SF Envelope (Min)")
        ax[1].plot(all_positions, self.bending_moments_envelope, 'b-', linewidth=2, label="BM Envelope")

        # Highlight extrema
        ax[0].scatter([max_shear_location, min_shear_location],
                    [max_shear_value, min_shear_value], color='red', zorder=5, label="SF Extrema")
        ax[1].scatter([max_bending_location, min_bending_location],
                    [max_bending_value, min_bending_value], color='blue', zorder=5, label="BM Extrema")

        ax[0].set_xlabel("Beam Length")
        ax[0].set_ylabel("Shear Force (SF)")
        ax[0].legend()
        ax[0].grid()

        ax[1].set_xlabel("Beam Length")
        ax[1].set_ylabel("Bending Moment (BM)")
        ax[1].legend()
        ax[1].grid()

        plt.tight_layout()
        st.pyplot(fig)

        return (
            (max_shear_location, max_shear_value),
            (min_shear_location, min_shear_value),
            (max_bending_location, max_bending_value),
            (min_bending_location, min_bending_value),
        )
    
    def generate_loading_characteristic(self, left=True):
        """
        Generates the loading characteristic of the beam by moving a train load across it.

        Args:
            left (bool): If True, the train starts from the left and moves to the right.
                         If False, the train starts from the right and moves to the left.

        Returns:
            tuple: A tuple containing:
                - max_positive_shear (float): The maximum positive shear force encountered.
                - max_negative_shear (float): The maximum negative shear force encountered.
                - max_positive_bending (float): The maximum positive bending moment encountered.
                - max_negative_bending (float): The maximum negative bending moment encountered.
        """

        # Move train to the extreme left
        if left:
            self.Load.set_train_left()
        else: 
            self.Load.set_train_right()

        # Iteratively move train across the bridge
        while (left and self.Load.wheel_positions[0] <= self.length) or (not left and self.Load.wheel_positions[-1] >= 0):
            # Update the beam's loads based on the train's current position
            self.loads = self.Load.get_loads()

            # Calculate shear forces at all positions
            shear_forces, bending_moments = self.calculate_sfd_bmd()

            # Update the shear force envelope with the maximum at each position
            self.shear_forces_envelope.append(max(shear_forces, key=abs))
            self.bending_moments_envelope.append(max(bending_moments, key=abs))

            if left:
                # Move train to the right incrementally
                self.Load.update_load_positions(direction=1)
            else:
                # Move train to the left incrementally
                self.Load.update_load_positions(direction=-1)

        # Calculate shear force and bending moment extrema
        max_positive_shear, max_negative_shear = self._find_extrema(self.shear_forces_envelope)
        max_positive_bending, max_negative_bending = self._find_extrema(self.bending_moments_envelope)

        self.max_shear_force = [max_positive_shear, max_negative_shear]
        self.max_bending_moment = [max_positive_bending, max_negative_bending]

        return max_positive_shear, max_negative_shear, max_positive_bending, max_negative_bending
    
    def plot_loading_characteristic(self):
        """
        Plots the loading characteristics of the beam, including the Shear Force Envelope (SFE) 
        and Bending Moment Envelope (BME).

        This method creates a figure with two subplots:
        - The first subplot displays the Shear Force Envelope (SFE) along the beam.
        - The second subplot displays the Bending Moment Envelope (BME) along the beam.

        The x-axis represents the position along the beam, extending from -TRAIN_LENGTH to the 
        length of the beam. The y-axis represents the shear force in Newtons (N) for the SFE 
        and the bending moment in Newton-millimeters (Nmm) for the BME.

        The method ensures that the envelope data matches the expected x-axis range. If the 
        lengths do not match, an error message is displayed.

        The plots include grid lines, zero-force/moment lines, and legends for clarity. The 
        layout is adjusted with padding between the plots for better visualization.

        The resulting figure is displayed using Streamlit.

        Raises:
            ValueError: If the length of the envelope data does not match the expected x-axis range.
        """
        # Calculate the x-axis range: train can extend from -train_length to bridge_length
        x_range = list(range(-int(TRAIN_LENGTH), int(self.length) + 1))

        # Ensure the envelope data matches the extended range
        if len(self.shear_forces_envelope) != len(x_range):
            st.error("Envelope data length does not match the expected x-axis range.")
            return

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot Shear Force Envelope (SFE)
        ax1.plot(x_range, self.shear_forces_envelope, label='Shear Force Envelope', color='b')
        ax1.set_title('Shear Force Envelope (SFE)')
        ax1.set_xlabel('Position along the beam (mm)')
        ax1.set_ylabel('Shear Force (N)')
        ax1.axhline(0, color='k', linestyle='--', linewidth=0.8)  # Add zero-force line
        ax1.grid(True)
        ax1.legend()

        # Plot Bending Moment Envelope (BME)
        ax2.plot(x_range, self.bending_moments_envelope, label='Bending Moment Envelope', color='r')
        ax2.set_title('Bending Moment Envelope (BME)')
        ax2.set_xlabel('Position along the beam (mm)')
        ax2.set_ylabel('Bending Moment (Nmm)')
        ax2.axhline(0, color='k', linestyle='--', linewidth=0.8)  # Add zero-moment line
        ax2.grid(True)
        ax2.legend()

        # Adjust layout with padding between plots
        plt.tight_layout(pad=3.0)

        # Display the plot using Streamlit
        st.pyplot(fig)
    
    def calculate_shear_stress(self):
        """
        This method computes the maximum shear stress at the centroid of the beam's cross-section
        using the shear force, moment of inertia, and the first moment of area. It also calculates
        the factor of safety (FOS) against shear failure.
        Returns:
            tuple: A tuple containing:
                - max_shear_stress (float): The maximum shear stress at the centroid.
                - FOS_shear (float): The factor of safety against shear failure.
        """
        if self.max_shear_force is None:
            V = self.max_shear_force_frame
        else: 
            V = max(abs(self.max_shear_force[0]), abs(self.max_shear_force[1]))

        I = self.cross_section.I
        Q = 0  # First moment of area
        b = 0  # Width at the centroidal axis

        for rectangle in self.cross_section.rectangles:
            # Bottom position and top position of the rectangle
            bottom = rectangle.position
            top = rectangle.position + rectangle.height

            # Rectangle intersects the centroid
            if bottom <= self.cross_section.centroid <= top: 
                b += rectangle.width  # Add the rectangle's width to b

                # Area of the portion above/below the centroid
                height_below = self.cross_section.centroid - bottom
                area_below = height_below * rectangle.width

                Q += area_below * abs(height_below/2 - self.cross_section.centroid)

            elif top < self.cross_section.centroid:
                # Rectangle is strictly below the centroid
                Q += rectangle.area * abs(rectangle.centroid - self.cross_section.centroid)

        # Ensure b is non-zero to avoid division errors
        if b == 0:
            st.error("Width at centroid (b) is zero. Check your geometry.")
            max_shear_stress = float('inf')
        else:
            # Shear stress calculation
            max_shear_stress = (V * Q) / (I * b)

        FOS_shear = SHEAR_STRENGTH / max_shear_stress

        self.shear_stress["centroid"] = max_shear_stress
        self.FOS["shear"] = FOS_shear

        return max_shear_stress, FOS_shear
    
    @DeprecationWarning
    def calculate_glue_shear_combined(self):
        """
        Calculate the combined glue shear for all glue connections in the cross-section.

        This method iterates over the glue connections in the cross-section, combines
        connections between the same pairs of rectangles in the same direction, and
        then calculates the glue shear for each unique pair of rectangles.

        The combined connections are stored in a dictionary with keys as tuples of
        ((rect1, rect2), direction) and values as the total thickness of the glue
        connections between those rectangles in that direction.

        After combining the connections, the method calls `calculate_glue_shear_pair`
        for each unique pair of rectangles to calculate the glue shear.

        Returns:
            None
        """
        # Initialize a dictionary to store combined glue connections by (rect1, rect2, direction)
        combined_connections = {}

        # Iterate over the glue connections
        for connection in self.cross_section.glue_connections:
            # Sort the rectangles to ensure uniqueness of the pair (rect1, rect2)
            rect_pair = tuple(sorted([connection["rect1"], connection["rect2"]]))
            key = (rect_pair, connection["direction"])

            # If the key exists, add the thickness to the existing value
            if key in combined_connections:
                combined_connections[key] += connection["thickness"]
            else:
                # If the key doesn't exist, initialize with the thickness
                combined_connections[key] = connection["thickness"]

        # After combining connections, process each unique pair
        for ((rect1, rect2), direction), total_thickness in combined_connections.items():
            # Call the method to calculate glue shear for the combined connections
            self.calculate_glue_shear_pair(rect1, rect2, direction, total_thickness)
    
    def calculate_glue_shear(self):
        """
        Calculate the shear stress in the glue connections of the beam's cross section.

        This method iterates over all glue connections in the cross section and calculates
        the shear stress for each pair of connected rectangles.

        Returns:
            None
        """
        for connection in self.cross_section.glue_connections:
            self.calculate_glue_shear_pair(connection["rect1"], connection["rect2"], connection["direction"], connection["thickness"])

    def calculate_glue_shear_pair(self, rect1_id, rect2_id, direction, thickness):
        """
        Calculate the shear stress in the glue line between two rectangles in a cross-section.
        Parameters:
        rect1_id (int): The ID of the first rectangle.
        rect2_id (int): The ID of the second rectangle.
        direction (str): The direction of the glue line ("horizontal" or "vertical").
        thickness (float): The thickness of the glue line.
        Returns:
        float: The calculated shear stress in the glue line.
        Raises:
        ValueError: If the rectangle IDs are invalid, the rectangles do not intersect in the specified direction,
                    the glue thickness is not greater than zero, or no common edge is found.
        NotImplementedError: If the vertical glue calculation is not implemented because it is not used in our design
        """
        
        if rect1_id < 0 or rect1_id >= len(self.cross_section.rectangles) or \
        rect2_id < 0 or rect2_id >= len(self.cross_section.rectangles):
            raise ValueError("Invalid rectangle IDs provided.")

        rect1 = self.cross_section.rectangles[rect1_id]
        rect2 = self.cross_section.rectangles[rect2_id]
        
        edge = None

        # Check if the rectangles intersect horizontally or vertically
        if direction == "horizontal":
            if rect1.position == rect2.position + rect2.height:
                edge = rect1.position
            elif rect2.position == rect1.position + rect1.height:
                edge = rect2.position
            else:
                raise ValueError("Rectangles do not intersect horizontally.")
        elif direction == "vertical":
            # if not (rect1.position == rect2.position + rect2.width and rect2.position <= rect1.position + rect1.width):
            #    raise ValueError("Rectangles do not intersect vertically.")
            raise NotImplementedError("Vertical Glue has Not been Implemented")

        if edge is None: 
            raise ValueError("No common edge")

        if thickness <= 0:
            raise ValueError("Glue thickness must be greater than zero.")

        # Calculate Q (first moment of area above/below the glue line)
        Q = 0
        for rectangle in self.cross_section.rectangles:
            if direction == "horizontal" and \
                ((self.cross_section.centroid < edge <= rectangle.position) or \
                 (rectangle.position <= edge < self.cross_section.centroid)):
                # Rectangle is above/below the glue line
                Q += rectangle.area * abs(rectangle.centroid - self.cross_section.centroid)
            elif direction == "vertical":
                raise NotImplementedError("Vertical Glue has Not been Implemented")

        if self.max_shear_force is None:
            V = self.max_shear_force_frame
        else: 
            V = max(abs(self.max_shear_force[0]), abs(self.max_shear_force[1]))

        # Shear stress calculation, adjusting for glue thickness (rthickness)
        I = self.cross_section.I  # Moment of inertia of the entire cross-section
        glue_shear_stress = (V * Q) / (I * thickness)

        # Store shear stress for this glue pair
        self.shear_stress[f"glue_{rect1_id}_{rect2_id}_{direction}"] = glue_shear_stress

        return glue_shear_stress
    
    def calculate_glue_fos(self):
        """
        Calculate the factor of safety (FOS) for glue joints based on shear stress.

        This method iterates through the shear stress values stored in the `shear_stress` dictionary
        of the object, identifies the entries related to glue joints, and calculates the factor of 
        safety for each glue joint by dividing the predefined shear strength of the glue 
        (SHEAR_STRENGTH_GLUE) by the corresponding shear stress value. It returns the minimum factor 
        of safety among all glue joints.

        Returns:
            float: The minimum factor of safety for the glue joints.
        """
        FOS_glue = []
        for key, value in self.shear_stress.items():
            if "glue" in key:
                FOS_glue.append(SHEAR_STRENGTH_GLUE / value)
        self.FOS["glue"] = min(FOS_glue)
        return self.FOS["glue"]

    def calculate_and_plot_failure_capacities(self, FOS):
        """
        Calculate and plot the failure capacities for bending moments and shear forces along the beam.
        Parameters:
        -----------
        FOS : dict
            A dictionary containing the factors of safety for different failure modes. The keys should include:
            - "tension": Factor of safety for tension failure in bending moments.
            - "compression": Factor of safety for compression failure in bending moments.
            - "buckling_comp": Factor of safety for buckling failure in compression bending moments.
            - "shear": Factor of safety for shear failure in shear forces.
            - "glue": Factor of safety for glue failure in shear forces.
            - "buckling_shear": Factor of safety for buckling failure in shear forces.
        Returns:
        --------
        None
            This method does not return any value. It generates and displays a plot of the failure capacities.
        """
        
        x_values = np.linspace(0, len(self.shear_forces), len(self.shear_forces))  # x-axis values (normalized positions)

        # Calculate failure capacities for bending moments
        M_fail_tens = FOS["tensile"] * np.array(self.bending_moments)
        M_fail_comp = FOS["compressive"] * np.array(self.bending_moments)
        M_fail_buck = FOS["buckling_comp"] * np.array(self.bending_moments)

        # Calculate failure capacities for shear forces
        V_fail_shear = FOS["shear"] * np.array(self.shear_forces)
        V_fail_glue = FOS["glue"] * np.array(self.shear_forces)
        V_fail_buck = FOS["buckling_shear"] * np.array(self.shear_forces)

        # Two subplots for moment-related and shear-related capacities
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

        # Plot moment-related capacities
        ax1.plot(x_values, M_fail_tens, label="M_fail_tens(x)", linestyle="--", color="blue")
        ax1.plot(x_values, M_fail_comp, label="M_fail_comp(x)", linestyle="--", color="orange")
        ax1.plot(x_values, M_fail_buck, label="M_fail_buck_1(x)", linestyle="--", color="green")
        ax1.set_title("Moment-Related Failure Capacities")
        ax1.set_xlabel("Position along the beam (x)")
        ax1.set_ylabel("Moment Capacity")
        ax1.legend()
        ax1.grid()

        # Plot shear-related capacities
        ax2.plot(x_values, V_fail_shear, label="V_fail_shear(x)", linestyle="-", color="red")
        ax2.plot(x_values, V_fail_glue, label="V_fail_glue(x)", linestyle="-", color="purple")
        ax2.plot(x_values, V_fail_buck, label="V_fail_buck(x)", linestyle="-", color="brown")
        ax2.set_title("Shear-Related Failure Capacities")
        ax2.set_xlabel("Position along the beam (x)")
        ax2.set_ylabel("Shear Capacity")
        ax2.legend()
        ax2.grid()

        # Adjust layout with padding between plots
        plt.tight_layout(pad=3.0)

        # Streamlit output
        st.pyplot(fig)