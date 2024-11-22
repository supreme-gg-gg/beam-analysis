class Rectangle:
    def __init__(self, width, height, position):
        self.width = width
        self.height = height
        self.position = position
        self.centroid = self.calculate_centroid()
        self.area = self.calculate_area()

    def calculate_area(self):
        return self.width * self.height

    def calculate_centroid(self):
        return self.position + self.height / 2
    
    def self_I(self):
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
        self.glue_connections.append({
            "rect1": rect1_id,
            "rect2": rect2_id,
            "direction": direction,
            "thickness": thickness
        })

    def add_rectangle(self, rectangle):
        self.rectangles.append(rectangle)

    def remove_rectangle(self, rectangle):
        if rectangle in self.rectangles:
            self.rectangles.remove(rectangle)

    def calculate_total_area(self):
        return sum(rectangle.area for rectangle in self.rectangles)

    def calculate_centroid(self):
        total_area = self.calculate_total_area()
        if total_area == 0:
            return 0  # Avoid division by zero if no rectangles are added

        weighted_sum = sum(rectangle.area * rectangle.centroid for rectangle in self.rectangles)
        centroid = weighted_sum / total_area
        self.centroid = centroid   
        return centroid 
    
    def calculate_moment_of_inertia(self):
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
        top = max([rect.centroid + rect.height / 2 for rect in self.rectangles])
        bottom = min([rect.centroid - rect.height / 2 for rect in self.rectangles])
        centroid_y = self.centroid
        return top - centroid_y, centroid_y - bottom


    def __str__(self):
        return "\n".join(str(rectangle) for rectangle in self.rectangles)