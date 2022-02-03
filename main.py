def promter(number):
    print('Please enter your ' + number)
    try:
        value = float(input())
        return value
    except:
        print('Input is not a float')
        return promter(number)

def calculate_bmi(height, weight):
    bmi = weight / (height * 2)
    bmi = round(bmi, 2)
    #print('Your height is ' + height) It's not possible to concatenate a string and an int / float in this way, solution on next line
    print("Your height is {} and your weight is {}".format(height, weight))
    print("Your bmi is {}".format(bmi))
    return bmi

def write_to_file(bmi):
    try:
        #Open and write to file in the current directory, w = open, create if it doesnt exist; a = append
        collectedData = open('bmi.txt', 'w')
        collectedData.write()
        collectedData.close()
        result = 'Data successfully written to file'
        return result
    except:
        result = 'Failed to write to file'
        return result

height = promter('height')
weight = promter('weight')

bmi = calculate_bmi(height, weight)

#I'd like to write this input to a file
print(write_to_file(bmi))