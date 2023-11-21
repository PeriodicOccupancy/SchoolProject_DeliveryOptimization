from datetime import time, timedelta, datetime, date

from Distances import address_distance
from HashMap import package_map
from Package import Package
from Truck import truck_list


# determines the next package to be delivered. Will return a float distance, and a package
# Big-O: O(n) -> average complexity, worst case would be O(n^2)
def next_delivery(truck, current_address):
    # logic ensures that the method can accept an int or a truck object, and still perform as intended
    if truck is int:
        for t in truck_list:
            if t.truck == truck:
                truck = t
                break
        if truck is int:
            print(f"No Truck matching ID of {truck} Provide a valid Truck object or Truck ID")
            return

    # Logic allows an address string or a package to be passed and for the method to still function
    if type(current_address) is Package:
        current_address = current_address.address
    if type(current_address) is not str:
        print(f"Could not handle argument {current_address}, must be type package or string")
        return

    # variable assignments to persist and change throughout the for loop
    best_package = None
    bp_distance = None
    earliest_deadline = None

    # for loop to cycle between all the packages that were assigned to this truck and perform the necessary
    # logic to determine which package to deliver next
    for p in truck.packages:

        # ensures that any package with the wrong address is not selected, before it has been corrected
        if "wrong address" in p.special_notes.lower():
            continue

        # we want to skip any package that has already been delivered, delivered packages will have a
        # timestamp assigned to the delivered attribute
        if p.delivered is not None:
            continue

        # all undelivered packages will go through the logic below
        else:
            address = p.address
            deadline = p.deadline
            distance = address_distance(address, current_address)

            # If best_package has not yet been assigned, the first valid package will be assigned
            if best_package is None:
                best_package = p
                earliest_deadline = deadline
                bp_distance = distance
                continue

            # Once best package has been assigned, the following logic will determine if the next
            # package in the list has a higher priority deadline, or if it is closer
            else:
                # if distance is less than 1, it is extremely close or at the same address, and is considered
                # the best package to deliver next by default.
                if distance <= 1.0:
                    best_package = p
                    bp_distance = distance
                    break
                # If best package has a deadline, and the current package does not, we skip to the next
                # iteration of the loop
                if type(deadline) is not time and type(earliest_deadline) is time:
                    continue
                # if both the best package and current package have no deadline
                elif type(deadline) is not time and type(earliest_deadline) is not time:
                    # if the current package's distance from the current address is shorter than
                    # the best package's distance, then the current package is the new best package
                    if distance < bp_distance:
                        best_package = p
                        bp_distance = distance
                        earliest_deadline = deadline
                    continue
                # if the best package has no deadline but the current package does, the current package
                # is the new best package
                elif type(deadline) is time and type(earliest_deadline) is not time:
                    best_package = p
                    earliest_deadline = deadline
                    bp_distance = distance
                    continue

                # if this statement is reached, both packages have a deadline, and we must compare them.
                else:
                    # deadline comparison
                    if deadline < earliest_deadline:
                        best_package = p
                        earliest_deadline = deadline
                        bp_distance = distance
                        continue

                    # if both deadlines are the same, we pick best package based on distance.
                    elif deadline == earliest_deadline:
                        if distance < bp_distance:
                            best_package = p
                            earliest_deadline = deadline
                            bp_distance = distance
                            continue
                        continue
                    elif deadline > earliest_deadline:
                        continue
                    print(
                        f" Something may have gone wrong, for loop in next_delivery() achieved what should have been an impossible result. May be missing a continue statement under an if clause.")
                    continue
    return [best_package, bp_distance]


# Routes a truck through all it's packages from its departure to it's return.
# variable checks used at function start to allow int or truck objects, and to allow any variable type for
# departure, though only valid Time objects will be used, and even then only if the truck did not already
# have a departure time preset
# Big-O: O(n^2)
def route_delivery(truck, departure):
    # logic ensures that the method can accept an int or a truck object, and still perform as intended
    if truck is int:
        for t in truck_list:
            if t.truck == truck:
                truck = t
                break
        if truck is int:
            print(f"No Truck matching ID of {truck} Provide a valid Truck object or Truck ID")
            return
    # ensures preset departure times take priority over any argument passed
    if type(truck.departure_time) is time:
        departure = truck.departure_time
    # Ensures that a departure time either from the truck or argument is present
    elif type(departure) is not time and type(truck.departure_time) is not time:
        print(f"Truck {truck.truck} has no departure time, one must be provided to route deliveries.")
        return
    # if an argument is passed and truck does not have a departure time, assigns truck.departure_time
    elif type(departure) is time and type(truck.departure_time) is not time:
        truck.departure_time = departure

    # new list to use as a boolean for the while loop
    to_be_delivered = []
    for p in truck.packages:
        to_be_delivered.append(p)
        # updates all packages with a 'departure' time for checking when they are considered 'en route'
        package_map.update_attr(p.id, "departure", departure)

    # Variables to track total distance truck has traveled, as well as the current time
    truck_distance = 0
    current_time = departure

    # Initializes current package as "HUB" so that the first loop checks the distance from HUB
    current_package = "HUB"
    # While loop to operate as long as the to_be_delivered list is populated
    while to_be_delivered:

        # Variables to call next_delivery() and store it's returned values
        returned = next_delivery(truck, current_package)
        current_package = returned[0]
        distance = returned[1]
        # adds the distance returned from next_delivery() to truck_distance, and updates it
        truck_distance += distance

        # Calculates the travel time to the package, based on avg truck speed, and distance
        travel_time = timedelta(hours=(distance / truck.avg_speed))
        # Calculates the current time, based on the time of last delivery, and travel time to the current one
        current_time = (datetime.combine(date.today(), current_time) + travel_time).time()

        # Removes the current package from the list used as a boolean in the while loop
        to_be_delivered.remove(current_package)
        # Updates the package using the package_map update_attr function, adding a delivery time
        package_map.update_attr(current_package.id, "delivered", current_time)

        # checks if the package has a deadline, and if so, checks if it was delivered before that deadline,
        # issues a print statement if not
        if type(current_package.deadline) is time:
            if current_package.deadline < current_package.delivered:
                print(f"\n{current_package} \nThe above package was not delivered on time.")

        # special check for truck 3, package 9 is loaded on it, if it's current time is after 10:20 AM, when the
        # correct address is known and received, so that all it's attributes may be updated, and it can be delivered.
        if truck.truck == 3:
            if current_time >= time(10, 20):
                package_map.update_attr(9, "address", "410 S State St")
                package_map.update_attr(9, "city", "Salt Lake City")
                package_map.update_attr(9, "state", "UT")
                package_map.update_attr(9, "zip", "84111")
                # updates special notes so that the next_delivery() algorithm no longer skips over it.
                package_map.update_attr(9, "special_notes", "address corrected")

    # checks the distance for returning to the HUB from final delivery, and stores it in the 'distance' variable
    distance = address_distance("HUB", current_package.address)
    # adds distance to truck_distance, and updates its value
    truck_distance += distance
    # Calculates the travel time back to hub, the same way it's done within the loop
    travel_time = timedelta(hours=(distance/truck.avg_speed))
    # gets the current time on the trucks return to the HUB
    current_time = (datetime.combine(date.today(), current_time) + travel_time).time()

    # Initialized boolean as True
    all_delivered = True
    # Iterates through all packages assigned to the truck
    for p in truck.packages:
        # If any of them have not received a delivery time, print to console and set all_delivered to False
        if type(p.delivered) is None:
            print(f"Package \n  {p}\n   was not Delivered.")
            all_delivered = False
    # If all_delivered is still True, meaning all packages have been given a delivery time (and have been delivered),
    # Print a statement to console of the success, the truck number, total distance, and return time.
    if all_delivered:
        print(f"All Packages on Truck {truck.truck} Delivered successfully, Total distance traveled was {round(truck_distance, 2)} miles. Return time was {current_time}")
    # Otherwise print of the failure to deliver all packages, along with the same variable as before.
    else:
        print(f"Not all Packages on Truck {truck.truck} were delivered. Total Distance traveled was {round(truck_distance, 2)} miles. Return time was {current_time}")

    # Update the trucks return time with the current_time at end of operation. Especially important for truck_1.
    truck.return_time = current_time

    # Return the total distance/mileage of the truck
    return truck_distance
