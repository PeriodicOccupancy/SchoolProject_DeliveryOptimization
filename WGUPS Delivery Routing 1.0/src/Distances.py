import csv

from Package import Package


# AddressMap class, used for creating a list of addresses, and assigning them an index that corresponds
# to the distance table. Also Appends itself to the global address_list
class AddressMap:
    # Initialize the Address mapping
    # Big-O: O(1)
    def __init__(self, address, zip, distance_id):
        self.address = address
        self.zip = zip
        self.distance_id = int(distance_id)
        address_list.append(self)

    # What to return when an AddressMapping is printed
    # Big-O: O(1)
    def __str__(self):
        return f"Address: {self.address} ({self.zip}) || Distance mapping ID: {self.distance_id}"


# Global Address list to be called anywhere in the program when needed to iterate through all address mappings
address_list = []


# Readings through the Delivery Addresses csv file and create entries for all addresses
# Big-O: O(n)
def read_addresses_csv():
    # Opens the CSV
    with open("WGUPS Delivery Addresses.csv", 'r') as file:
        reader = csv.reader(file)
        # loops over each row in the csv reader and keeps an index of the loop count for assigning distance_id's
        for i, row in enumerate(reader):
            address = row[0].strip()
            # Special check for the HUB address mapping
            if address == 'HUB':
                AddressMap(address, None, i)
            # All other address mappings are handled the same
            else:
                address, zip_code = address.rsplit('(', 1)
                address = address.strip()
                zip_code = zip_code.strip(')')
                AddressMap(address, zip_code, i)


# Reading through the distance table csv to create a matrix/2D list for finding the distance between
# any 2 address mappings
# Big-O: O(n^2)
def read_distance_csv():
    with open("WGUPS Distance Table.csv", 'r') as file:
        reader = csv.reader(file)
        distances = []
        # separating the csv into rows
        for row in reader:
            distances_row = []
            # separating the rows into cells/columns
            for cell in row:
                # Try/Catch block to fill in null cells with 0.0
                try:
                    distances_row.append(float(cell))
                except ValueError:
                    distances_row.append(0.0)
            # appends the new row to the list of rows
            distances.append(distances_row)
    # Returns the matrix
    return distances


# Stores the matrix created by read_distance_csv()
distance_map = read_distance_csv()


# Basic function call to return the value at the row and column specified, but in some cases it may return 0.0 when
# the distance is not 0.0, because only the lower left half of the table contains the actual distances, and the
# rest of the table is 0.0. To fix this it swaps the index mappings when they return 0.0 and tries again, if it
# still returns 0.0 the actual distance is 0.0, otherwise it gets the true distance
# Big-O: O(1)
def int_distance(a1: int, a2: int):
    distance = distance_map[a1][a2]
    if distance == 0.0:
        distance = distance_map[a2][a1]
    if type(distance) is None:
        print(f"something went wrong, int_distance({a1}{a2}) returned a NoneType")
    return distance


# This serves the same purpose as int_distance, but is instead fed 2 string arguments, which it then converts into
# distance_ids before passing them along to the int_distance function
# Big-O: O(n)
def address_distance(a1: str, a2: str):
    d1 = None
    d2 = None
    for a in address_list:
        if str(a.address) == a1:
            d1 = a.distance_id
        if str(a.address) == a2:
            d2 = a.distance_id
    if d1 is None or d2 is None:
        print("No distance mapping found for one or both of provided addresses.")
        print(f"address 1 is {a1} id: {d1} \naddress 2 is {a2} id: {d2}")
        return
    distance = int_distance(int(d1), int(d2))
    return distance


# This function again serves the same purpose as int_distance() and address_distance(), but is passed 2
# package objects instead, grabs their addresses and passes them to address_distance()
# Big-O: O(n)
def package_distance(p1: Package, p2: Package):
    a1 = p1.address
    a2 = p2.address
    distance = address_distance(a1, a2)

    return distance


# This function also returns a distance like the others, but has a specific use case for when the distance
# to the hub is needed, and can be passed an int distance_id, an address string or a package obj
# Big-O: O(n)
def hub_distance(package):
    if type(package) == int:
        return int_distance(0, package)
    elif type(package) == str:
        for a in address_list:
            if a.address == package:
                return int_distance(0, a.distance_id)
    elif type(package) == Package:
        for a in address_list:
            # print(f"{a.address} <-> {package.address}")
            if a.address == package.address:
                return int_distance(0, a.distance_id)
        print(
            f"Package #: {package.id} does not return an address matching any address in the database, distance cannot be mapped")
        return
    else:
        print(f"{package} is an invalid  argument, cannot return distance from hub")
        return
