import math
import csv
import os

def calculate_point_coordinates_from_csv(csv_file_path):
    x = 0
    y = 0
    z = 0
    w = 0

    with open(csv_file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)

        #counters
        header = 0
        counter = 0

        for row in reader:
            
            #skip header
            if header < 8:
                header += 1
                continue
            
            if (counter == 9):
                break
            print(row[2:6])
            x += float(row[6]) if row[6]!= "" else 0.0
            y += float(row[7]) if row[7]!= "" else 0.0
            z += float(row[8]) if row[8]!= "" else 0.0
            w += float(row[5]) if row[5] != "" else 0.0
            counter += 1
    print("Total",x,y,z)
        
    x = x/9
    y = y/9
    z = z/9
    w = w/9
    distance = float(csv_file_path.split("_")[-1].split("m")[0])

    # Convert rotation angle from degrees to radians
    rotation_radians = math.radians(w)

    # Calculate the coordinates of the point in the laser's local coordinate system
    point_x_local = distance * math.cos(rotation_radians)
    point_y_local = distance * math.sin(rotation_radians)
    point_z_local = 0  

    # Calculate the global coordinates of the point by adding the laser's coordinates
    point_x_global = x + point_x_local
    point_y_global = y + point_y_local
    point_z_global = z + point_z_local
    print(x,y,z,point_x_local,point_y_local,point_z_local)

    return (point_x_global, point_y_global, point_z_global)


folder_path = '/Volumes/T7/Data/Day2/Measurements/mocap_positions'

# Get a list of all files in the folder that end with "m.csv"
csv_files = [file for file in os.listdir(folder_path) if "CameraAbove1" in file]
print(csv_files)
results = []
# Iterate through the list of CSV files and call the function for each one
for csv_file in csv_files:
    csv_file_path = os.path.join(folder_path, csv_file)
    outcome = calculate_point_coordinates_from_csv(csv_file_path)
    results.append(outcome)


average = [0,0,0]
for pos in results:
    average[0] += pos[0]
    average[1] += pos[1]
    average[2] += pos[2]

average[0] = average[0]/ len(results)
average[1] = average[1]/ len(results)
average[2] = average[2]/ len(results)

print("Final:" ,average)
    