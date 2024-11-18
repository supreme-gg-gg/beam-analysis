class Rectangle:
    def __init__(self, width, height, position):
        self.width = width
        self.height = height
        self.position = position

    def calculate_area(self):
        return self.width * self.height

    def calculate_centroid(self):
        return self.position + self.height / 2

    def __str__(self):
        return f"Rectangle(width={self.width}, height={self.height}, position={self.position})"
    
class CrossSection:
    def __init__(self):
        self.rectangles = []

    def add_rectangle(self, rectangle):
        self.rectangles.append(rectangle)

    def remove_rectangle(self, rectangle):
        if rectangle in self.rectangles:
            self.rectangles.remove(rectangle)

    def calculate_total_area(self):
        return sum(rectangle.calculate_area() for rectangle in self.rectangles)

    def calculate_centroid(self):
        total_area = self.calculate_total_area()
        if total_area == 0:
            return 0  # Avoid division by zero if no rectangles are added

        weighted_sum = sum(rectangle.calculate_area() * rectangle.calculate_centroid() for rectangle in self.rectangles)
        centroid = weighted_sum / total_area
        return centroid

    def __str__(self):
        return "\n".join(str(rectangle) for rectangle in self.rectangles)