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
        lower_bound = 0  # Set your lower bound here
        upper_bound = self.bridge_length  # Set your upper bound here
        loads = []
        for position in self.wheel_positions:
            if lower_bound <= position <= upper_bound:
                loads.append((position, self.weight_per_wheel))
            else:
                loads.append((position, 0))
        return loads
    
    def update_load_positions(self, shift_distance=1, direction=1):
        self.wheel_positions = [
            pos + shift_distance*direction for pos in self.wheel_positions
        ]
        self.train_position += shift_distance*direction

    def set_train_left(self):
        self.train_position = 0
        self.wheel_positions = [-856, -680, -504, -340, -176, 0] # this is constant

    def set_train_right(self):
        self.train_position = self.bridge_length
        self.wheel_positions = [self.bridge_length + pos for pos in [0, 176, 340, 504, 680, 856]]
