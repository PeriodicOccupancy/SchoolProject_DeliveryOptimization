# Program written by:
#      Michael Fasnacht
#       Student ID: 001321050
import sys
from datetime import datetime

#   Program written for C950 Data Structures & Algorithms II
#       Assessment NHP2 Task 1: WGUPS Routing Program

#   Written in February of 2023

# imports
from DeliveryRouting import route_delivery
from Distances import read_addresses_csv
from TruckSort import load_trucks
from HashMap import package_map
from Truck import truck_1, truck_2, truck_3, truck_list

# Program Start

# function to populate the address list for use with the distance table csv, and comparison with the package file
read_addresses_csv()

# Function to call the loading algorithms to sort packages onto trucks, Function located in TruckSort.py
load_trucks()

# variable to call the route_delivery function for every truck (passing a departure time if needed) and store the
# total accumulated distance between all trucks. Function located in DeliveryRouting.py
truck_1.mileage = route_delivery(truck_1, None)
truck_2.mileage = route_delivery(truck_2, None)
# Truck 3 cannot leave until truck 1 has returned, due to only having 3 drivers, none of its packages have
# a deadline before EOD and package #9 cannot be delivered before 10:20 so this works in our favor.
truck_3.mileage = route_delivery(truck_3, truck_1.return_time)

# variable to track total mileage of all trucks, and a for loop to add the mileage from every truck
total_distance = 0
for t in truck_list:
    total_distance += t.mileage

# nested for loop to print out each truck followed by all its assigned packages, and their status at program end.
for t in truck_list:
    print(f"\n{t}     \nPackages delivered:")
    t.packages.sort(key=lambda p1: p1.delivered)
    for p in t.packages:
        print(f"{p}")

# Prints the total accumulated distance between all 3 trucks. Must be below 140 according to project constraints.
print(f"\n\nTotal Distance traveled by all trucks was {round(total_distance, 2)}")

# While loop for user input to request specific data on trucks or packages.
# Loop only ends when user selects to exit the program.
# Big-O: O(n*(m+k)) -> depended on the number of loops performed by user, and the data structure of packages and trucks
while True:
    print("\n\n\nWhat would you like to do?")
    print("1: View Package info.\n2: View Truck info.\n3: Exit Program")
    print("Select Option an option. Integers only.")
    try:
        choice1 = int(input())
    except ValueError:
        print("Please only enter a single character of the option you wish to select.")
        continue

    # View Package info
    if choice1 == 1:
        print("\nPlease select an option:")
        print("1: Show all package info.")
        print("2: Package look-up(all package attributes including departure from hub and delivery times).")
        print("3: Package-Time Lookup (package status look-up for a specific time).")
        print("4: Time-Status for all packages (lookup the status of all packages at a specified time).")
        print("5: Return to first menu.")
        print("Select an option 1 through 5: ")

        try:
            choice2 = int(input().lower())
        except ValueError:
            print("Please only enter a single character of the option you wish to select.")
            continue

        # Print all packages
        if choice2 == 1:
            print_packages = []
            for bucket in package_map.buckets:
                for p in bucket:
                    print_packages.append(p)
            print_packages.sort(key=lambda ps: ps.id)
            print("\nAll Packages:")
            for p in print_packages:
                print(f"{p}")
            continue

        # Package lookup, print all attributes
        elif choice2 == 2:
            try:
                id_lookup = int(input("Please enter the id of the package you wish to lookup: "))
                print(package_map.retrieve(id_lookup))
            except ValueError:
                print("Invalid entry, returning to menu.")
                continue

        # Package-Time lookup, lookup a package status at a specific time
        elif choice2 == 3:
            try:
                id_lookup = int(input("Please enter the id of the package you wish to lookup: "))
                package = package_map.retrieve(id_lookup)
                time_lookup = input("Please enter a time. (in 24 hour, \"HH:MM\" format): ")
                time = datetime.strptime(time_lookup, "%H:%M").time()
            except ValueError:
                print("Invalid entry, returning to menu.")
                continue
            if time < package.departure:
                print(
                    f"Package {package.id} is at the HUB, as of {time}. Deadline: {package.deadline}; Package group: {package.package_group}; Special Notes: {[package.special_notes]}")
            elif package.departure <= time < package.delivered:
                print(
                    f"Package {package.id} is on truck {package.truck} and en route as of {time}. Deadline: {package.deadline}; Package group: {package.package_group}; Special Notes: {[package.special_notes]}")
            elif package.delivered <= time:
                print(
                    f"Package {package.id} is delivered as of {time}. Deadline: {package.deadline}; Package group: {package.package_group}; Special Notes: {[package.special_notes]}")
            continue

        # Time-Status lookup, lookup the status of all packages at a specified time
        elif choice2 == 4:
            print_packages = []
            for bucket in package_map.buckets:
                for p in bucket:
                    print_packages.append(p)
            print_packages.sort(key=lambda ps: ps.id)
            try:
                time_lookup = input("Please enter a time. (in 24 hour, \"HH:MM\" format): ")
                time = datetime.strptime(time_lookup, "%H:%M").time()
            except ValueError:
                print("Invalid entry, returning to menu.")
                continue
            for package in print_packages:
                if time < package.departure:
                    print(
                        f"Package {package.id} is at the HUB, as of {time}. Deadline: {package.deadline}; Package group: {package.package_group}; Special Notes: {[package.special_notes]}")
                elif package.departure <= time < package.delivered:
                    print(
                        f"Package {package.id} is on truck {package.truck} and en route as of {time}. Deadline: {package.deadline}; Package group: {package.package_group}; Special Notes: {[package.special_notes]}")
                elif package.delivered <= time:
                    print(
                        f"Package {package.id} is delivered as of {time}. Deadline: {package.deadline}; Package group: {package.package_group}; Special Notes: {[package.special_notes]}")

                continue

        # Return to first menu
        elif choice2 == 5:
            continue

        # Invalid input
        else:
            print("Please only enter a single character of the option you wish to select.")
            continue

    # View Truck Info
    elif choice1 == 2:
        print("\nWhat would you like to know:")
        print("1: All truck info (print all information on all trucks).")
        print("2: Truck lookup (specify a truck id 1-3 and view it's details).")
        print("3: Request Total Mileage.")
        print("4: Return to menu.")
        try:
            choice2 = int(input("Select an Option: "))
        except ValueError:
            print("Invalid entry, returning to menu.")
            continue

        # All Truck info
        if choice2 == 1:
            invalid_entry = True
            # Loops until the user provides a valid input, when an input is accepted,
            # invalid_entry is set to False and the appropriate operations are performed,
            # after which, the loop ends
            while invalid_entry:
                try:
                    print("Print package list of each truck? (Integers only, 1 for yes, 2 for no.)")
                    print_package_list = int(input())
                    if print_package_list == 1:
                        invalid_entry = False
                        for t in truck_list:
                            print(t)
                            for p in t.packages:
                                print(p)
                        continue
                    elif print_package_list == 2:
                        invalid_entry = False
                        for t in truck_list:
                            print(t)
                        continue
                    else:
                        print("Invalid Entry. Please only enter 1 or 2, no spaces.")
                        continue
                except ValueError:
                    print("Invalid Entry. Please only enter 1 or 2, no spaces.")
                    continue
            continue

        # Truck Lookup
        if choice2 == 2:
            truck_lookup = 0
            invalid_entry = True
            # Loops until the user provides a valid input, when an input is accepted,
            # invalid_entry is set to False and the loop ends
            while invalid_entry:
                try:
                    truck_lookup = int(input("Enter Truck id (1-3): "))
                    if truck_lookup < 1 or truck_lookup > 3:
                        print("No truck with that ID, please enter an integer between 1 and 3.")
                        invalid_entry = True
                    invalid_entry = False
                except ValueError:
                    print("Invalid entry, please only enter a single integer between 1 and 3.")
                    continue

            invalid_entry = True
            # Loops until the user provides a valid input, when an input is accepted,
            # invalid_entry is set to False and the appropriate operations are performed,
            # after which, the loop ends
            while invalid_entry:
                try:
                    print("Print package list of truck? Integers only, 1 for yes, 2 for no.")
                    print_package_list = int(input())
                    if print_package_list == 1:
                        invalid_entry = False
                        for t in truck_list:
                            if t.truck == truck_lookup:
                                print(t)
                                for p in t.packages:
                                    print(p)
                        continue
                    elif print_package_list == 2:
                        invalid_entry = False
                        for t in truck_list:
                            if t.truck == truck_lookup:
                                print(t)
                        continue
                    else:
                        print("Invalid Entry. Please only enter 1 or 2, no spaces.")
                        continue
                except ValueError:
                    print("Invalid Entry. Please only enter 1 or 2, no spaces.")
                    continue

        # Request total mileage
        if choice2 == 3:
            # Prints the variable we created earlier in the program for the sum of each truck's mileage
            print(f"\n\nTotal Distance traveled by all trucks was {round(total_distance, 2)}")
            continue

        # Return to Menu
        if choice2 == 4:
            continue

        # Invalid Input
        else:
            print("Please only enter a single character of the digit option you wish to select.")
            continue

    # Exit Program
    elif choice1 == 3:
        exit()

    # Invalid Input
    else:
        print("Please only enter a single character of the digit option you wish to select.")
        continue
