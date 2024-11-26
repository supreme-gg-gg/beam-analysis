from config import *
import math
import copy
class Rectangle:
    def __init__(self, width, height, position, position_x=None):
        self.width = width
        self.height = height
        self.position = position
        self.position_x = 0 if position_x is None else position_x
        self.centroid = self.calculate_centroid()
        self.centroid_x = self.calculate_centroid_x()
        self.area = self.calculate_area()

    def calculate_area(self):
        """
        Calculate the area of the geometry.

        Returns:
            float: The area calculated as width multiplied by height.
        """
        return self.width * self.height

    def calculate_centroid(self):
        """
        Calculate the centroid of the geometry.

        The centroid is calculated as the position plus half of the height.

        Returns:
            float: The y-coordinate of the centroid.
        """
        return self.position + self.height / 2
    
    def calculate_centroid_x(self):
        """
        Calculate the centroid of the geometry.

        The centroid is calculated as the position plus half of the height.

        Returns:
            float: The y-coordinate of the centroid.
        """
        return self.position_x + self.width / 2
    
    def self_I(self):
        """
        Calculate the moment of inertia (I) of a rectangular cross-section.

        The moment of inertia is calculated using the formula:
        I = (width * height^3) / 12

        Returns:
            float: The moment of inertia of the rectangular cross-section.
        """
        return (self.width * self.height ** 3) / 12

    def __repr__(self):
        return f"Rectangle(width={self.width}, height={self.height}, position={self.position}, position_x={self.position_x})"
    
class CrossSection:
    def __init__(self, diaphragm_spacing=0):
        self.rectangles = []
        self.centroid = 0
        self.centroid_x = 0
        self.I = 0
        self.glue_connections = []  # Store glue information
        self.diaphragm_spacing = diaphragm_spacing  # Number of diaphragms
        self.buckling_capacity = {}
        self.fos_buckling = {}

    def add_glue_connection(self, rect1_id, rect2_id, direction, thickness):
        """
        Adds a glue connection between two rectangles.

        Parameters:
        rect1_id (int): The ID of the first rectangle.
        rect2_id (int): The ID of the second rectangle.
        direction (str): The direction of the glue connection.
        thickness (float): The thickness of the glue connection.

        Returns:
        None
        """
        self.glue_connections.append({
            "rect1": rect1_id,
            "rect2": rect2_id,
            "direction": direction,
            "thickness": thickness
        })

    def add_rectangle(self, rectangle):
        """
        Adds a rectangle to the list of rectangles.

        Parameters:
        rectangle (Rectangle): The rectangle object to be added to the list.
        """
        self.rectangles.append(rectangle)

    def remove_rectangle(self, rectangle):
        """
        Removes a rectangle from the list of rectangles if it exists.

        Parameters:
        rectangle (Rectangle): The rectangle to be removed from the list.

        Returns:
        None
        """
        if rectangle in self.rectangles:
            self.rectangles.remove(rectangle)

    def calculate_total_area(self):
        """
        Calculate the total area of all rectangles.

        This method iterates over all rectangles in the `self.rectangles` list
        and sums their individual areas to compute the total area.

        Returns:
            float: The total area of all rectangles.
        """
        return sum(rectangle.area for rectangle in self.rectangles)

    def calculate_centroid(self):
        """
        Calculate the centroid of the composite shape formed by the rectangles.

        This method calculates the centroid of the composite shape by taking the
        weighted average of the centroids of the individual rectangles, weighted
        by their respective areas.

        Returns:
            float: The centroid of the composite shape. Returns 0 if no rectangles
            are added to avoid division by zero.
        """
        total_area = self.calculate_total_area()
        if total_area == 0:
            return 0  # Avoid division by zero if no rectangles are added

        weighted_sum = sum(rectangle.area * rectangle.centroid for rectangle in self.rectangles)
        centroid = weighted_sum / total_area
        self.centroid = centroid
        return centroid
    
    def calculate_centroid_x(self):
        """
        Calculate the centroid of the composite shape formed by the rectangles.

        This method calculates the centroid of the composite shape by taking the
        weighted average of the centroids of the individual rectangles, weighted
        by their respective areas.

        Returns:
            float: The centroid of the composite shape. Returns 0 if no rectangles
            are added to avoid division by zero.
        """
        total_area = self.calculate_total_area()
        if total_area == 0:
            return 0
        
        weighted_sum = sum(rectangle.area * rectangle.centroid_x for rectangle in self.rectangles)
        centroid_x = weighted_sum / total_area
        self.centroid_x = centroid_x
        return centroid_x

    def calculate_moment_of_inertia(self):
        """
        Calculate the moment of inertia of the composite section.

        This method calculates the moment of inertia of a composite section
        made up of multiple rectangles. It uses the parallel axis theorem
        to account for the distance of each rectangle's centroid from the
        overall centroid of the composite section.

        Returns:
            float: The total moment of inertia of the composite section.
        """
        centroid_y = self.centroid
        total_inertia = 0
        for rectangle in self.rectangles:
            I_centroid = rectangle.self_I()
            distance = abs(rectangle.centroid - centroid_y)
            I_parallel_axis = I_centroid + rectangle.area * distance**2
            total_inertia += I_parallel_axis
        self.I = total_inertia
        return total_inertia

    def get_max_y(self):
        """
        Calculate the maximum vertical distance from the centroid to the top and bottom edges of the rectangles.

        Returns:
            tuple: A tuple containing two floats:
                - The distance from the centroid to the top edge.
                - The distance from the centroid to the bottom edge.
        """
        top = max([rect.centroid + rect.height / 2 for rect in self.rectangles])
        bottom = min([rect.centroid - rect.height / 2 for rect in self.rectangles])
        centroid_y = self.centroid
        return top - centroid_y, centroid_y - bottom
    
    def _analyse_buckling_cases(self):
        """
        Analyse and classify rectangles into different buckling cases based on their positions
        relative to the centroid of the section.
        Buckling cases:
        1. Bounded on both sides
        2. Bounded on one side
        3. Unbounded
        The method performs the following steps:
        1. Copies the list of rectangles to avoid modifying the original list.
        2. Filters out rectangles that are entirely in the tension region (below the centroid).
        3. Adjusts the height and position of rectangles that partially overlap with the centroid.
        4. Classifies the remaining rectangles into one of the three buckling cases based on their
           positions relative to the centroid.
        Returns:
            dict: A dictionary with keys "1", "2", and "3" representing the three buckling cases,
                  and values as lists of rectangles that fall into each case.
        """
        buckling_cases = {
            "1": [],  # Bounded on both sides
            "2": [],  # Bounded on one side
            "3": [],  # Unbounded
        }
        # Copy the list of rectangles to avoid modifying the original
        rectangles = copy.deepcopy(self.rectangles)

        # Filter out rectangles not in the top compression region
        for rectangle in rectangles[:]:
            # Adjust partially overlapping rectangles
            if rectangle.position <= self.centroid <= (rectangle.position + rectangle.height):
                overlap_height = rectangle.height - abs(self.centroid - rectangle.position)
                rectangle.height = overlap_height  # Adjust rectangle height
                rectangle.position = self.centroid  # Update starting position of rectangle
            # Check if the rectangle is entirely in the tension region (below centroid)
            elif rectangle.centroid < self.centroid:
                rectangles.remove(rectangle)  # Remove tension region rectangles
            elif rectangle.position_x > self.centroid_x:
                rectangles.remove(rectangle)

        # Classify the remaining rectangles into buckling cases
        tmp = None
        for rectangle in rectangles:
            # Case 1: Bounded on both sides
            if rectangle.position_x < self.centroid_x and rectangle.width > rectangle.height:
                if not rectangle.position_x == 0: # skip the leftmost because it is also case 2
                    tmp = rectangle.width
                if len(buckling_cases["1"]) == 0:
                    buckling_cases["1"].append(rectangle)
                else:
                    # Combine rectangles bounded on both sides
                    buckling_cases["1"][0].height += rectangle.height

            # Case 2: Bounded on one side (left or right edge)
            if rectangle.position_x == 0:
                # adjust the width that is effective for case 2
                rectangle.width = (rectangle.width - tmp) / 2 if tmp is not None else rectangle.width
                buckling_cases["2"].append(rectangle)

            # Case 3: Not bounded (completely free)
            elif rectangle.position_x < self.centroid_x and rectangle.width < rectangle.height:
                buckling_cases["3"].append(rectangle)
            
        return buckling_cases
    
    @staticmethod
    def _calculate_buckling(k, t, b=None, a=None, h=None):
        """
        Helper function that implements the buckling equations for different cases.
        Parameters:
        k (float): Buckling coefficient.
        t (float): Thickness of the material.
        b (float, optional): Width of the material (used in cases 1-3).
        a (float, optional): Length of the material (used in case 4).
        h (float, optional): Height of the material (used in case 4).
        Returns:
        float: The calculated buckling value.
        Raises:
        ValueError: If the input parameters do not match any of the expected cases.
        """
        if b is not None: # this is case 1-3
            return k * (math.pi **2) * YOUNGS_MODULUS / (12 * (1 - POISSON_RATIO)**2) * ((t / b) ** 2)
        elif a is not None and h is not None: # this is case 4
            return k * (math.pi **2) * YOUNGS_MODULUS / (12 * (1 - POISSON_RATIO)**2) * ((t / a) ** 2 + (t / h) ** 2)
        else:
            raise ValueError("Invalid input for buckling calculation.")
    
    def calculate_buckling_capacity(self, sigma_top, tau_cent):
        """
        Calculate the buckling capacity and factor of safety (FOS) for different buckling cases.
        Parameters:
        sigma_top (float): Compressive stress at the top of the section.
        tau_cent (float): Shear stress at the centroid of the section.
        Returns:
        tuple: A tuple containing two dictionaries:
            - buckling_capacity (dict): Maximum buckling capacity for each case.
            - FOS_buckling (dict): Factor of Safety (FOS) for each buckling case.
        """
        buckling_cases = self._analyse_buckling_cases()  # Analyze and classify buckling cases
        buckling_capacity = {
            "1": 0,  # Bounded on both sides
            "2": 0,  # Bounded on one side
            "3": 0,  # Unbounded
            "4": 0,  # Shear buckling
        }

        # Iterate over each buckling case
        for case, rectangles in buckling_cases.items():
            for rectangle in rectangles:
                # Ensure valid dimensions
                if rectangle.width <= 0 or rectangle.height <= 0:
                    continue  # Skip invalid rectangles
                
                # Calculate buckling capacities for cases 1-3
                if case == "1":  # Bounded on both sides
                    capacity = self._calculate_buckling(
                        k=4, t=rectangle.height, b=rectangle.width
                    )
                elif case == "2":  # Bounded on one side
                    capacity = self._calculate_buckling(
                        k=0.425, t=rectangle.height, b=rectangle.width
                    )
                elif case == "3":  # Unbounded
                    capacity = self._calculate_buckling(
                        k=6, t=rectangle.width, b=rectangle.height
                    )
                else:
                    raise ValueError(f"Invalid buckling case: {case}")
                
                # Update the maximum capacity for the case
                buckling_capacity[case] = max(buckling_capacity[case], capacity)

        # Shear buckling capacity (Case 4)
        try:
            vertical_wall = max(
                self.rectangles, key=lambda rect: rect.height if rect.height > 0 else 0
            )
            if vertical_wall.height > 0 and vertical_wall.width > 0:
                buckling_capacity["4"] = self._calculate_buckling(
                    k=5,
                    t=vertical_wall.width,
                    a=self.diaphragm_spacing,
                    h=vertical_wall.height,
                )
        except ValueError:
            # No valid rectangles found for shear buckling
            buckling_capacity["4"] = 0

        # Calculate Factor of Safety (FOS) for each case using compressive stress and shear stress at centroid
        FOS_buckling = {
            case: (buckling_capacity[case] / sigma_top if case != "4" else buckling_capacity[case] / tau_cent)
            for case in buckling_capacity
        }

        self.buckling_capacity = buckling_capacity
        self.fos_buckling = FOS_buckling

        return buckling_capacity, FOS_buckling

    def __str__(self):
        return "\n".join(str(rectangle) for rectangle in self.rectangles)