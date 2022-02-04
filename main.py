import datetime

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
        collectedData.write("\n{}".format(bmi))
        collectedData.close()
        result = 'BMI successfully written to file.'
        return result
    except:
        result = 'Failed to write to file.'
        return result

def write_bmi_and_date(bmi):
    # Dateformat as used in tildevand.txt 202201010305
    # 2022 01 01 03 05
    # year month day hour minute
    dato = datetime.datetime.now()
    dato = dato.strftime("%Y%m%d%H%M")
    try:
        collectedData = open('bmi.txt', 'a')
        collectedData.write("\n{} {}".format(dato, bmi))
        result = 'Date and BMI successfully written to file.'
        return result
    except:
        result = 'Unable to write date and BMI to file.'
        return result

def read_from_file():
    # Open the bmi.txt file in read mode
    # Maybe the file cannot be opened and will raise an exception
    fileName = 'bmi.txt'
    try:
        bmifile = open(fileName, 'r')
        # Read the lines into the variable lines
        lines = bmifile.readlines()
        # Go through each of the lines

        # See https://www.w3schools.com/python/python_lists.asp for types of arrays
        dateandBMI = {}

        for line in lines:
            x = {}
            # Remove new line (/n)
            line = line.strip()
            # Each line contains two items, date and BMI. Split them () is standard a space.
            (dato, BMI) = line.split()
            # Write date and BMI to dateandBMI dictionary, cast both as a float
            dateandBMI[float(dato)] = float(BMI)

        bmifile.close()
        return dateandBMI
    except:
        print('Was unable to read file {} with BMI data.'.format(fileName))
        return False

def statistics(dict):
    # How many items are there in our list?
    print("\n Statistics: ")
    print("There are {} items in the list.".format(len(dict)))

    # Average BMI
    sumBMI = 0
    # Loop through the dictionary and add the value of each item to the sum
    for item in dict.values():
        sumBMI += item

    averageBMI = sumBMI / len(dict)
    print("The average BMI is {}".format(round(averageBMI, 2)))

    # Som other statistics: min & max
    # We check only the .values(), and not the .key()
    minBMI = round(min(dict.values()), 2)
    maxBMI = round(max(dict.values()), 2)
    print("The lowest BMI in the list is: {}".format(minBMI))
    print("The highest BMI in the list is: {} \n".format(maxBMI))

# Ask the user for height and then weight
def choices():
    question = input('What would you like to do? (add, stats or stop)')
    if question == "add":
        height = prompter('height')
        weight = prompter('weight')
    #elif question == "write":
        # Calculate the BMI and print
        bmi = calculate_bmi(height, weight)
        # Write the userinput to a file
        print(write_bmi_and_date(bmi))
        #print(write_to_file(bmi))
        return choices()
    elif question == 'stats':
        # Open the file and read the data
        listBMI = read_from_file()
        if(listBMI != False):
        # Calculate the average BMI, return the lowest and highest BMI in the list
            statistics(listBMI)
        return choices()
    elif question == 'stop':
        return False


choices()