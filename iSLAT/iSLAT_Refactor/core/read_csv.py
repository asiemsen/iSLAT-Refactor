import os
import csv
from iSLAT_Refactor.app_globals import MOLECULES_DATA
def read_from_user_csv():
    save_folder = 'SAVES'
    filename = os.path.join(save_folder, f"molecules_list.csv")

    if os.path.exists(filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                return [tuple(row[:3]) for row in reader]
        except FileNotFoundError:
            pass
    return MOLECULES_DATA