import csv

from Package import Package


# Class for creating a mapping table of objects, to be easily retrieved using a key value
class HashMap:
    # Initializes the Hashmap class
    # Big-O: O(1)
    def __init__(self):
        self.capacity = 20
        self.buckets = [[] for _ in range(self.capacity)]
        self.length = 0

    # Creates a key to find the correct bucket for an object
    # Big-O: O(1)
    def create_key(self, id):
        return hash(id) % self.capacity

    # inserts an object into the hashmap
    # Big-O: O(1)
    def insert(self, package):
        key = self.create_key(package.id)
        self.buckets[key].append(package)
        self.length += 1

    # Updates the variable of a object matching the ID given with a new value
    # Big-O: O(n) -> However the number of objects in each bucket will typically
    # be very small, so in practice the avg complexity should be O(1)
    def update_attr(self, id, variable, new_value):
        key = self.create_key(id)
        bucket = self.buckets[key]
        for p in bucket:
            if p.id == id:
                setattr(p, variable, new_value)
                break

    # Deletes a specified obj from the hashmap
    # Big-O: O(n) -> However the number of objects in each bucket will typically
    # be very small, so in practice the avg complexity should be O(1)
    def delete(self, id):
        success = False
        key = self.create_key(id)
        for p in self.buckets[key]:
            if p.id == id:
                del self.buckets[key]
                self.length -= 1
                success = True
                break
        if not success:
            print(f"Package with ID {id} not found.")

    # Retrieves an obj object from a given ID
    # Big-O: O(n) -> However the number of objects in each bucket will typically
    # be very small, so in practice the avg complexity should be O(1)
    def retrieve(self, id):
        key = self.create_key(id)
        for p in self.buckets[key]:
            if p.id == id:
                return p
        print(f"no package matching id {id} found.")

    # Retrieves a specified attribute from an object matching the key given
    # Big-O: O(n) -> However the number of objects in each bucket will typically
    # be very small, so in practice the avg complexity should be O(1)
    def retrieve_attr(self, id, variable_name):
        key = self.create_key(id)
        for p in self.buckets[key]:
            if p.id == id:
                return getattr(p, variable_name)
        return None


# Creates a hash map of packages from the package file csv, and returns it.
# Big-O: O(n)
def package_csv_hashmap():
    hashmap = HashMap()
    with open("WGUPS Package File.csv", "r") as file:
        reader = csv.reader(file)

        for line in reader:
            id, address, city, state, zip, deadline, kilos, special_notes, *_ = line
            package = Package(id, address, city, state, zip, deadline, kilos, special_notes)
            hashmap.insert(package)

        return hashmap


# call to the package_csv_hashmap() method to assign a global persistent variable name to the hashmap to be
# easily referenced elsewhere in the program
package_map = package_csv_hashmap()
