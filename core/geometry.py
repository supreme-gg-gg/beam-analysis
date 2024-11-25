class Rectangle:
    def __init__(self, width, height, position):
        self.width = width
        self.height = height
        self.position = position
        self.centroid = self.calculate_centroid()
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
        return f"Rectangle(width={self.width}, height={self.height}, position={self.position})"
    
class CrossSection:
    def __init__(self):
        self.rectangles = []
        self.centroid = 0
        self.I = 0
        self.glue_connections = []  # Store glue information

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

    def __str__(self):
        return "\n".join(str(rectangle) for rectangle in self.rectangles)