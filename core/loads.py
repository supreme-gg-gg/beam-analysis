class TrainLoad:
    def __init__(self, total_weight, weight_per_wheel, wheel_positions):
        self.total_weight = total_weight  # Total weight of the train (N)
        self.weight_per_wheel = weight_per_wheel  # Weight per wheel (N)
        self.wheel_positions = wheel_positions  # List of wheel positions (m)

    def get_loads(self):
        """Return the load at each wheel position."""
        return list(zip(self.wheel_positions, [self.weight_per_wheel] * len(self.wheel_positions)))