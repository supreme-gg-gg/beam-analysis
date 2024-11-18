import matplotlib.pyplot as plt
import streamlit as st

from config import *

class Beam:
    def __init__(self, length, supports, loads, cross_section=None):
        self.length = length      # Total length of the beam
        self.supports = supports  # List of support locations (e.g., ['A', 'B'])
        self.Load = loads     # TrainLoad object
        self.loads = loads.get_loads()   # List of loads with (location, magnitude)
        self.cross_section = cross_section  # CrossSection object

        # Calculate reaction forces based on applied loads and support locations
        self.reaction_forces = self.calculate_reactions()
        self.shear_forces, self.bending_moments = self.calculate_sfd_bmd()
        self.max_shear_force = max(self.shear_forces)
        self.max_bending_moment = max(self.bending_moments)

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

        stress_top = self.max_bending_moment * y_t / I
        stress_bottom = self.max_bending_moment * y_b / I

        # Calculate Factor of Safety (FOS)
        FOS_top = COMPRESSIVE_STRENGTH / stress_top
        FOS_bottom = TENSILE_STRENGTH / stress_bottom

        return stress_bottom, stress_top, FOS_bottom, FOS_top

