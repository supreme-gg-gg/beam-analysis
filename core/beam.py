import matplotlib.pyplot as plt
import streamlit as st

from config import *

class Beam:
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
        self.shear_forces_envelope = []
        self.bending_moments_envelope = []
        self.shear_stress = {}
        self.max_shear_force = None
        self.max_bending_moment = None

    def calculate_reactions(self):
        # Total load (sum of all point loads)
        total_load = sum(load[1] for load in self.loads)

        # Calculate the moment about point A to get reaction at B (RB)
        sum_moments_A = sum(load[1] * load[0] for load in self.loads)  # Moment = Load * Distance from A
        RB = sum_moments_A / self.length  # Reaction at B (RB) is total moment divided by the beam length

        # Reaction at A (RA) is the remaining load balance after RB
        RA = total_load - RB

        return {'A': RA, 'B': RB}

    def calculate_sfd_bmd(self):
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

        if not self.cross_section:
            st.warning("Please define a cross-section for the beam.")
            return

        I = self.cross_section.I
        y_t, y_b = self.cross_section.get_max_y()

        if self.max_bending_moment is not None:

            # positive max moment
            stress_c_1 = self.max_bending_moment[0][1] * y_t / I
            stress_t_1 = self.max_bending_moment[0][1] * y_b / I

            # we flip these values because the bending moment is negative
            # top is tensile and bottom is compressive
            stress_t_2 = self.max_bending_moment[1][1] * y_t / I
            stress_c_2 = self.max_bending_moment[1][1] * y_b / I

            # Calculate Factor of Safety (FOS)
            stress_t = max(abs(stress_t_1), abs(stress_t_2))
            stress_c = max(abs(stress_c_1), abs(stress_c_2))
        
        else:
            stress_c = self.max_bending_moment_frame * y_t / I
            stress_t = self.max_bending_moment_frame * y_b / I

        FOS_c = COMPRESSIVE_STRENGTH / stress_t
        FOS_t = TENSILE_STRENGTH / stress_c

        return stress_t, stress_c, FOS_t, FOS_c
    
    @staticmethod
    def _find_extrema(data):
        """Helper function to find max positive and min negative values with indices."""
        max_pos = max(((idx - TRAIN_LENGTH, val) for idx, val in enumerate(data) if val > 0), default=(None, 0), key=lambda x: x[1])
        min_neg = min(((idx - TRAIN_LENGTH, val) for idx, val in enumerate(data) if val < 0), default=(None, 0), key=lambda x: x[1])
        
        return max_pos, min_neg

    
    def generate_sfe_bme(self, left=True):

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
    
    def plot_sfe_bme(self):
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
        '''
        Calculate the maximum shear stress in the beam.
        '''
        
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

        return max_shear_stress, FOS_shear
    
    @DeprecationWarning
    def calculate_glue_shear_combined(self):
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
        for connection in self.cross_section.glue_connections:
            self.calculate_glue_shear_pair(connection["rect1"], connection["rect2"], connection["direction"], connection["thickness"])

    def calculate_glue_shear_pair(self, rect1_id, rect2_id, direction, thickness):
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
        FOS_glue = []
        for key, value in self.shear_stress.items():
            if "glue" in key:
                FOS_glue.append(SHEAR_STRENGTH_GLUE / value)
        return min(FOS_glue)

    def calculate_buckling_stress(self):
        '''
        Calculate the maximum stress due to buckling.
        '''
        pass

    def calculate_buckling_fos(self):
        '''
        Calculate the factor of safety against buckling failure.
        '''
        pass

    

