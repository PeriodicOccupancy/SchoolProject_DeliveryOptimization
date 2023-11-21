
from datetime import time, datetime
import re


class Package:

    # Initializes the Package Class object, assigning it variables based on the input from the Package File csv.
    # Also calls the special_notes_parser() to automatically parse and assign varaibles based on the 'special_notes'
    # input from the csv
    # Big-O: O(1)
    def __init__(self, id, address, city, state, zip, deadline, kilos, special_notes):
        self.id = int(id)
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        if re.match(r'^\d{1,2}:\d{2} [ap]m$', deadline.lower()):
            self.deadline = datetime.strptime(deadline, "%I:%M %p").time()
        else:
            self.deadline = deadline
        self.kilos = kilos
        self.special_notes = special_notes
        self.on_truck = False  # tracks if package has been assigned/loaded onto a truck yet.

        self.departure = None  # time when the truck the package is loaded onto leaves the facility to deliver packages
        self.delivered = None  # time when package is delivered and no longer on truck.

        # Parsing special_notes for key information
        if self.special_notes:
            self.special_notes_parser()
        else:
            self.truck = None
            self.package_group = []
            self.pickup = None  # the time when the package is available for pickup, None means it is there at start of day.

    # Parses Package notes to determine package attributes for sorting onto trucks
    # Big-O: O(1) the complexity does not change much or at all with varying inputs &
    # re.findall is assumed to be parsing a relatively small string.
    def special_notes_parser(self):
        # ensures all comparisons perform properly by making notes all lowercase
        notes = self.special_notes.lower()
        # Packages intended to be on a specific truck are checked for here, and assigned
        if "truck" in notes:
            words = notes.split()
            for i, word in enumerate(words):
                if word == "truck":
                    try:
                        self.truck = int(words[i + 1])
                        self.package_group = []
                        self.pickup = None
                        return
                    except (ValueError, IndexError):
                        print(f"Cannot parse special notes from package {self.id}, checking for truck assignment.")
                        self.truck = None
                        self.package_group = []
                        self.pickup = None
                        return

        # Checks for package groups, packages that for whatever reason must be on the same truck
        elif "delivered with" in notes:
            self.truck = None
            self.package_group = [int(x) for x in re.findall(r'\d+', notes)]
            self.pickup = None
            return
        # Packages that are not present at the start of day, are assigned to truck 2, which will be set to leave
        # whenever the last package needed is received
        elif "delayed" in notes:
            self.truck = 2
            self.package_group = []
            match = re.search(r'\d{1,2}:\d{2}\s*[aApP][mM]', notes)
            if match:
                self.pickup = datetime.strptime(match.group(0), '%I:%M %p').time()
            else:
                self.pickup = None
                print(f"Special notes mentioned delayed, but no time object could be parsed from {self}")
            return
        # Packages with the wrong address listed, will be assigned to truck 3, so that they do not slow down other
        # deliveries before having their address corrected.
        elif "wrong address" in notes:
            self.truck = 3
            self.package_group = []
            self.pickup = None
            return
        # If a package has special notes, but it cannot be parsed by any of the above messages, a notification is
        # printed to the console, and relevant attributes are all set to None
        else:
            print(
                f"Special Notes exist on Package # {self.id} but do not contain usual keywords. Package may be mishandled as a result. \n "
                f"This message shouldn't be seen with sample data provided with project.")
            self.truck = None
            self.package_group = None
            self.pickup = None

    # to string method, for determining what string to return when package objects are called as a string.
    # Big-O: O(1)
    def __str__(self):
        return f"Package ID: {self.id}  ||Address: {self.city}, {self.state}, {self.address} ({self.zip})  ||En Route: {self.departure}  ||Deadline: {self.deadline}  ||Delivered: {self.delivered}  ||Truck: {self.truck}  ||Grouped with: {self.package_group}  ||On truck: {self.on_truck} ||Special Notes: {self.special_notes}"
