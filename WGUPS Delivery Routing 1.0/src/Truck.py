from datetime import time


class Truck:

    # Initializes the truck class, only needing a numer, the rest of its
    # attributes must be initialized or filled in later
    # Big-O: O(1)
    def __init__(self, truck):
        self.truck = truck
        self.avg_speed = 18
        self.capacity = 16
        self.departure_time = None
        self.return_time = None
        self.packages = []
        self.mileage = 0

    # What to return when a truck object is printed.
    # Big-O: O(1)
    def __str__(self):
        return f"Truck #: {self.truck}  ||Capacity: {len(self.packages)}/{self.capacity} ||Mileage: {self.mileage}  ||Departure: {self.departure_time}  ||Return: {self.return_time}"


# Creates all 3 Trucks used in the project scenario, and assigns them a departure time, to meet project constraints.
# Truck 3 is assigned a departure time later in runtime to coincide with truck 1's Return time, since we only have 2
# drivers.
# Everything below is also O(1) as it is constant.
truck_1 = Truck(1)
truck_1.departure_time = time(8, 00)
truck_2 = Truck(2)
truck_2.departure_time = time(9, 5)
truck_3 = Truck(3)
# Creates a truck list, so that we may iterate over it for ease of performing operations on all trucks.
truck_list = [truck_1, truck_2, truck_3]
