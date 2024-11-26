from config import *
class TrainLoad:
    def __init__(self, total_weight, base_positions, train_position, weight_per_wheel, bridge_length=1200):
        self.total_weight = total_weight  # Total weight of the train (N)
        self.weight_per_wheel = weight_per_wheel  # Weight per wheel (N)
        self.bridge_length = bridge_length  # Length of the bridge (mm)
        self.train_position = train_position  # Current position of the train on the bridge (mm)
        self.base_positions = base_positions  # Base positions of the wheels (mm)
        self.wheel_positions = [sum(base_positions[:i+1]) + train_position 
                                for i in range(len(base_positions))]

    def get_loads(self):
        """
        Calculate the loads on the bridge based on wheel positions and weights.

        This method iterates through the wheel positions and determines if each
        wheel is within the bounds of the bridge. If a wheel is within the bounds,
        its corresponding weight is added to the loads list. If a wheel is outside
        the bounds, a load of 0 is added for that position.

        Returns:
            list of tuple: A list of tuples where each tuple contains the position
            of the wheel and the corresponding load (weight). If the wheel is
            outside the bounds, the load is 0.
        """
        lower_bound = 0  # Set your lower bound here
        upper_bound = self.bridge_length  # Set your upper bound here
        loads = []
        for idx, position in enumerate(self.wheel_positions):
            if lower_bound <= position <= upper_bound:
                loads.append((position, self.weight_per_wheel[idx]))
            else:
                loads.append((position, 0))
        return loads
    
    def update_load_positions(self, shift_distance=1, direction=1):
        """
        Update the positions of the loads by shifting them.

        This method updates the positions of the wheel loads and the train position
        by shifting them a specified distance in a specified direction.

        Parameters:
        shift_distance (int, optional): The distance by which to shift the positions. Default is 1.
        direction (int, optional): The direction in which to shift the positions. Default is 1.
                                   Positive values shift to the right, negative values shift to the left.

        Returns:
        None
        """
        self.wheel_positions = [
            pos + shift_distance*direction for pos in self.wheel_positions
        ]
        self.train_position += shift_distance*direction

    def set_train_left(self):
        """
        Set the train to the leftmost position.

        This method sets the train's position to the leftmost point (position 0)
        and initializes the wheel positions relative to this point. The wheel
        positions are set to a constant list of values representing their
        distances from the leftmost position.
        """
        self.train_position = 0
        self.wheel_positions = [-856, -680, -504, -340, -176, 0] # this is constant

    def set_train_right(self):
        """
        Sets the train to the rightmost position on the bridge.

        This method updates the train's position to be at the end of the bridge
        and calculates the positions of the train's wheels relative to the bridge length.

        Attributes:
            train_position (float): The position of the train on the bridge.
            wheel_positions (list of float): The positions of the train's wheels on the bridge.
        """
        self.train_position = self.bridge_length
        self.wheel_positions = [self.bridge_length + pos for pos in [0, 176, 340, 504, 680, 856]]
