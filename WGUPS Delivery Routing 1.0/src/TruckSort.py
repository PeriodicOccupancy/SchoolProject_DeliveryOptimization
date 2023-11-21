from datetime import time

from Distances import package_distance, hub_distance
from HashMap import package_map
from Truck import truck_list, truck_1, truck_2


# Creates a list of all packages that have not yet been loaded onto a
# truck, for iterating over when sorting packages onto trucks
# Big-O: O(n log n) if we ignore the sorting operation, complexity would be O(n)
def list_unloaded():
    packages = []
    for bucket in package_map.buckets:
        for p in bucket:
            if not p.on_truck:
                packages.append(p)
    return sorted(packages, key=lambda package: package.id)


# Assigns a global variable to the list returned by list_unloaded()
unloaded_packages = list_unloaded()


# Method to load all packages that are assigned to a specific truck
# Big-O: O(n*m) -> 2 inputs  truck_list and unloaded_packages. However, Truck_list is,
# for the purposes of this project, static, so the complexity can be considered O(n)
def load_assigned_packages():
    # temporary list to track packages for removal from the unloaded_packages list
    packages_to_remove = []
    for t in truck_list:                # iterates over the list of trucks
        for p in unloaded_packages:     # iterates over the list of unloaded packages
            # if the assigned truck id on a package (p.truck), matches the truck id (t.truck), it is
            # loaded on the truck and added to the temp list for removal from the unloaded list
            if p.truck == t.truck:
                t.packages.append(p)
                package_map.update_attr(p.id, 'on_truck', True)
                packages_to_remove.append(p)
                continue
    # after finishing iterating through all packages and each truck,
    # we remove all packages in the temp list from the unloaded list
    for p in packages_to_remove:
        unloaded_packages.remove(p)


# This method is run before truck_sort, to ensure all packages with deadline besides EOD are prioritized on trucks that
# have a driver at the start of the day.
# This method references Truck objects directly instead of dynamically, and may need updating if the number of trucks changes
# Big-O: O(n^2*m) ->  truck_list is ignored for complexity as we consider it to be relatively constant.
# as package groups should be relatively rare and the nested loop should only run once (only 1 group of packages exit)
# we can realistically consider this to be O(n log n), or O(n^2) depending on if we want to include the sorting operation
# in our complexity evaluation, as early packages should be relatively short.
def load_early_packages():
    early_packages = []     # temp list for storing early packages for iterating over
    for p in unloaded_packages:     # iterate over the list of unloaded packages
        if type(p.deadline) == str or type(p.deadline) is None:     # if no deadline is set, move on to the next
            continue
        else:       # Otherwise append the package to early_packages
            early_packages.append(p)
    early_packages.sort(key=lambda ep: ep.deadline)     # Sort the early packages list by deadline
    while_iterations = 0    # tracks iterations of the while loop
    while early_packages:   # loop will iterate until list is empty, or the set iteration limit is reached
        if while_iterations >= 50:  # Infinite loop prevention
            print(
                f"while loop in load_early_packages reached {while_iterations} iterations, terminating potential infinite loop.")
            return
        for p in early_packages:    # iterates over early packages
            if p.on_truck:      # if statement to remove packages that have already been added to a truck. Redundancy check.
                early_packages.remove(p)
                unloaded_packages.remove(p)
                continue
            # If a package has a deadline before or equal to 10:30 AM, and does
            # not have a pickup time (delayed packages) it will be added to truck 1
            if (p.deadline <= time(10, 30)) and (p.pickup is None) and (
                        # Also performs a capacity check to ensure there is room on the truck.
                    (len(truck_1.packages) + len(p.package_group) + 1) <= truck_1.capacity):
                truck_1.packages.append(p)
                unloaded_packages.remove(p)
                package_map.update_attr(p.id, 'on_truck', True)
                package_map.update_attr(p.id, 'truck', 1)
                # If the package also has a package group, the entire package group will be added, so long as
                # there is space for it, as checked by the previous if statement
                if p.package_group:
                    for pid in p.package_group:     # Iterates over the package group
                        p1 = package_map.retrieve(pid)  # Looks up each package id, and assigns a reference
                        truck_1.packages.append(p1)        # adds the package to truck 1
                        package_map.update_attr(p1.id, 'on_truck', True)    # Updates package status
                        package_map.update_attr(p1.id, 'truck', 1)
                        unloaded_packages.remove(p1)        # removes package from unloaded packages
                        if p1 in early_packages:            # removes package if it is in early packages
                            early_packages.remove(p1)
                early_packages.remove(p)        # removes the package from the first for loop
                # the while loop ensures that any packages skipped by index changes are not left
                # behind, and loops until the list is empty

            # Otherwise any package with a deadline after 10:30 or that has a deadline prior,
            # but cannot be physically on the truck until a later time is loaded on truck 2
            elif len(truck_2.packages) + len(p.package_group) + 1 <= truck_2.capacity:  # Capacity check
                # All the same operations as above are performed, but on truck 2 instead.
                truck_2.packages.append(p)
                unloaded_packages.remove(p)
                package_map.update_attr(p.id, 'on_truck', True)
                package_map.update_attr(p.id, 'truck', 2)
                if p.package_group:
                    for pid in p.package_group:
                        p1 = package_map.retrieve(pid)
                        truck_2.packages.append(p1)
                        package_map.update_attr(p1.id, 'on_truck', True)
                        package_map.update_attr(p1.id, 'truck', 2)
                        unloaded_packages.remove(p1)
                        if p1 in early_packages:
                            early_packages.remove(p1)
                early_packages.remove(p)

        while_iterations += 1
        # the iteration count is incremented at the end of each loop, as an infinite loop prevention measure


# Method to sort any packages not loaded by load_assigned_packages(), or
# load_early_packages() onto trucks, based on distance
# Big-O: O(n^2)
def truck_sort(truck):
    # Value check. Allows passing of an int as long as it corresponds to a truck id, instead of just a truck obj
    if truck is int:
        for t in truck_list:
            if t.truck == truck:
                truck = t
                break
        if truck is int:
            print(f"No Truck matching ID of {truck} Provide a valid Truck object or Truck ID")
            return

    unproductive_loop_counter = 0   # infinite loop protection variable
    # While truck is below capacity, and there are still packages to load
    while len(truck.packages) < truck.capacity and unloaded_packages:

        # infinite loop detection, This counter should be adjusted depending on the number packages that are part of a group.
        # if an infinite loop occurs due to the only packages left being in a group too large to fit on the truck, this statement
        # will end the loop, leaving the truck below full capacity, but allowing the program to continue.
        if unproductive_loop_counter > 50:
            print(
                f"A potential infinite loop has been detected and halted. Unproductive loop counter reached: {unproductive_loop_counter}.")
            # packages = []
            # for p in truck.packages:
            # packages.append(p)
            return

        # checks if any packages are already loaded onto the truck
        if truck.packages:
            min_distance = None
            min_package = None
            # Iterate over packages on truck to find an unloaded package
            # with the smallest distance to any package already onboard
            for tp in truck.packages:

                for p in unloaded_packages:     # Iterate over unloaded packages for comparison
                    if p.on_truck:
                        unproductive_loop_counter += 1
                        print("You shouldn't see this message. package in unloaded_packages was already loaded")
                        continue

                    # checks if package is part of a group (needs to be on same truck)
                    if p.package_group:

                        # If the package group would exceed the capacity of a truck, the current loop iteration
                        # is skipped and the unproductive loop counter is increased
                        if len(truck.packages) + (len(p.package_group) + 1) > truck.capacity:
                            unproductive_loop_counter += 1
                            continue

                        sum_distance = 0  # tracks the sum distance from location to all packages in group for averaging
                        distance_list = [package_distance(tp, p)]  # Creates a list of distances
                        for pid in p.package_group:     # Iterates over package group and adds each distance to the list
                            p1 = package_map.retrieve(pid)
                            distance_list.append(package_distance(tp, p1))
                        for d in distance_list:     # adds all the distances in the list together
                            sum_distance += d
                        # Assigns the average distance of the group to the distance variable
                        distance = sum_distance / len(distance_list)

                    else:   # if not part of a group, assigns distance to package address
                        distance = package_distance(tp, p)

                    if min_distance is None:  # if no min_distance is set, assigns the current distance and package

                        min_distance = distance
                        min_package = p
                    else:   # Otherwise a comparison is performed for the lowest distance.
                        if distance < min_distance:     # If new distance is lower, it becomes the new min package
                            min_distance = distance
                            min_package = p
            # Redundancy check incase for some reason min_package is still None, if unloaded
            # packages is not empty will continue the while loop, otherwise returns
            if min_package is None:
                if unloaded_packages:
                    continue
                else:
                    return
            # Appends the minimum/best package to the truck and updates it, and removes it from the unloaded package list
            truck.packages.append(min_package)
            package_map.update_attr(min_package.id, 'on_truck', True)
            package_map.update_attr(min_package.id, 'truck', truck.truck)
            unloaded_packages.remove(min_package)

            # if min_package is part of a package group, this statement ensures all packages
            # in it's group are loaded onto the truck, updated in the package_map, and
            # removed from the unloaded_packages list
            if min_package.package_group:
                for pid in min_package.package_group:
                    p1 = package_map.retrieve(pid)
                    truck.packages.append(p1)
                    package_map.update_attr(p1.id, 'on_truck', True)
                    package_map.update_attr(p1.id, 'truck', truck.truck)
                    unloaded_packages.remove(p1)

            # Checks for truck capacity
            if len(truck.packages) == truck.capacity:
                return
            if len(truck.packages) > truck.capacity:
                print(f"Truck {truck.truck} has been loaded beyond capacity, something went wrong.")
                return

        # if truck has no packages loaded currently, uses similar logic, but uses distance from hub instead of from other packages
        else:
            min_package = None
            min_distance = None
            for p in unloaded_packages:
                if p.on_truck:
                    unproductive_loop_counter += 1
                    print("You shouldn't see this message. package in unloaded_packages was already loaded")
                    continue

                # if p (current package) is part of a package group, the distance of all
                # packages in the group are averaged. If there are too many packages to fit
                # in the truck's capacity, the current loop iteration is skipped.
                if p.package_group:
                    # print(f" if package group {p} || {p.package_group}")
                    if len(truck.packages) + (len(p.package_group) + 1) > truck.capacity:
                        unproductive_loop_counter += 1
                        continue
                    sum_distance = 0
                    distance_list = [hub_distance(p)]
                    for pid in p.package_group:
                        p1 = package_map.retrieve(pid)
                        distance_list.append(hub_distance(p1))
                    for d in distance_list:
                        # print(f"variable d is {type(d)}")
                        sum_distance += d
                    distance = sum_distance / len(distance_list)
                else:
                    distance = hub_distance(p)

                # if min_package has not been set yet, it uses the first package it checks.
                if min_package is None:
                    min_package = p
                    min_distance = distance
                else:
                    # print(f"distance is {type(distance)} and min distance is {type(min_distance)}")
                    if distance < min_distance:
                        min_package = p
                        min_distance = distance

            truck.packages.append(min_package)
            package_map.update_attr(min_package.id, 'on_truck', True)
            package_map.update_attr(min_package.id, 'truck', truck.truck)
            unloaded_packages.remove(min_package)

            # if min_package is part of a package group, this statement ensures all packages
            # in it's group are added loaded onto the truck, updated in the package_map, and
            # removed from the unloaded_packages list
            if min_package.package_group:
                for pid in min_package.package_group:
                    p1 = package_map.retrieve(pid)
                    truck.packages.append(p1)
                    package_map.update_attr(p1.id, 'on_truck', True)
                    package_map.update_attr(p1.id, 'truck', truck.truck)
                    unloaded_packages.remove(p1)

            if len(truck.packages) == truck.capacity:
                return
            if len(truck.packages) > truck.capacity:
                print(f"Truck {truck.truck} has been loaded beyond capacity, something went wrong.")
                return


# Method to perform all the necessary tasks to load all trucks in the truck list.
# Big-O: O(n^2*m) -> load_early_packages has the largest complexity, so we use that, however truck_sort()
# will always have a larger input and more operations, dominating most of this function, so we can also
# realistically use its complexity of O(n^2) as the 'average' for this function.
def load_trucks():
    # Method calls
    load_assigned_packages()
    load_early_packages()
    packages_loaded = 0     # variable to count loaded packages
    for truck in truck_list:  # iterate over the truck list
        print(f"\nTruck {truck.truck} loaded with following packages: ")
        truck_sort(truck)       # sort packages for each truck
        for p in truck.packages:    # count packages on each truck
            print(f"{p}")
            packages_loaded += 1
        print(f"Packages loaded on truck {truck.truck}: {len(truck.packages)}")
    print(f"\nTotal packages loaded: {packages_loaded}")
    # If loaded packages is equal to the length/current storage of the package map, print a success statement.
    if packages_loaded == package_map.length:
        print("All packages loaded successfully.\n")
