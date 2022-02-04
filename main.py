def prompter(number):
    print('Please enter your ' + number)
    try:
        # Some info about int, float etc. https://www.w3schools.com/python/python_numbers.asp
        value = float(input())
        return value
    except:
        print('Input is not a float')
        return prompter(number)


def calculate_bmi(height, weight):
    bmi = weight / (height * 2)
    # print('Your height is ' + height) It's not possible to concatenate
    # a string and an int or float in this way, solution on next line
    print("Your height is {} m and your weight is {} kg".format(height, weight))
    print("Your BMI is {}".format(round(bmi, 2)))
    return bmi


def write_to_file(bmi):
    try:
        # Open and write to file in the current directory
        # w = open, create if it doesn't exist. Will overwrite if exists.
        # a = append, create if it doesn't exist and otherwise add.
        collectedData = open('bmi.txt', 'a')
        # Write the bmi to the file and end with a new line
        collectedData.write("{} \n".format(bmi))
        collectedData.close()
        result = 'BMI successfully written to file'
        return result
    except:
        result = 'Failed to write to file'
        return result

def read_from_file():
    # Open the bmi.txt file in read mode
    bmifile = open('bmi.txt', 'r')

    # Print the whole file
    # print(bmifile.read())

    # Read the lines into the variable lines
    lines = bmifile.readlines()
    # Go through each of the lines

    # See https://www.w3schools.com/python/python_lists.asp for types of arrays
    listBMI = []

    for line in lines:
        # Remove new line (/n)
        line = line.strip()
        # Cast it as a float
        line = float(line)
        # Add it to the list
        listBMI.append(line)

    bmifile.close()
    return listBMI

def statistics(list):
    # How many items are there in our list?
    print("\n Statistics: ")
    print("There are {} items in the list".format(len(list)))

    # Average BMI
    averageBMI = 0
    # Loop through the list and add each item to the sum
    for l in list:
        averageBMI += l

    gemiddelde = averageBMI / len(list)
    print("The average BMI is {}".format(round(gemiddelde, 2)))

    # Som other statistics: min & max
    print("The lowest BMI in the list is: {}".format(min(list)))
    print("The highest BMI in the list is: {}".format(max(list)))

# Ask the user for height and then weight
height = prompter('height')
weight = prompter('weight')

# Calculate the BMI and print
bmi = calculate_bmi(height, weight)

# Write the userinput to a file
print(write_to_file(bmi))

# Open the file and read the data
listBMI = read_from_file()

# Calculate the average BMI, return the lowest and highest BMI in the list
statistics(listBMI)