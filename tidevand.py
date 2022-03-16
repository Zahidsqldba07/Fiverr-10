from datetime import datetime, timedelta
from itertools import tee, islice, chain
import matplotlib.pyplot as plt
from urllib.request import urlopen
import json

def hour_rounder(t):
    # Rounds to nearest hour by adding an hour (using timedelta) if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

dict = {}
# Take the file tidevand.txt and read the lines, then add them to the dictionary dict.
with open('tidevand.txt') as file:
    for line in file.readlines():
        line = line.split()
        line[0] = datetime.strptime(line[0], '%Y%m%d%H%M')
        # Because we don't want to deal with the minutes, we'll round up to the nearest hour
        # https://stackoverflow.com/questions/48937900/round-time-to-nearest-hour-python
        line[0] = hour_rounder(line[0])
        dict[line[0]] = int(line[1])

# Note we do some assumptions on the data, for example that there are no double entries, data is in chronological order etc.
# Since the data is static anyway, we don't bother to do any checks.

# Save the calculated water levels here:
new_dict = {}

# The function below is just to show the progress/notes, and is not used anymore.
def process_single_day(today):
    # Function takes in a date and will find and all the corresponding values
    # Function returns a dictionary with dates + values
    water_on_date = {}
    for dato, water in dict.items():
        currentdate = dato.year, dato.month, dato.day
        targetdate = (today.year, today.month, today.day)
        if currentdate == targetdate:
            water_on_date[dato] = int(water)
    # The dictionary water_on_date now contains all the values for the requested date
    # We find the min and max value, plus the corresponding key
    min_water_date = min(water_on_date, key=water_on_date.get)
    min_water_value = water_on_date[min_water_date]
    max_water_date = max(water_on_date, key=water_on_date.get)
    max_water_value = water_on_date[max_water_date]

    if(len(water_on_date)!= 4):
        print("Min water height on {}-{}-{} is {}, the maximum is {}.".format(min_water_date.day, min_water_date.month, min_water_date.year, min_water_value, max_water_value))
        print("There are {} measurements for this day.".format(len(water_on_date)))

    return water_on_date

    # Nykle: Conclusions about the data, note from the 08 february
    # Some days have 4 predictions, others have only 3. Why is that?
    # Take for example the 5th of January 2022:
    #202201050552	  -19
    #202201051153	   20
    #202201051811	  -24
    # Note that there are approximately 6 hours between each prediction.
    # This means that some days, the '4th' measurement is part of the following day.
    # The 'value' of each prediction is the expected *lowest* or *highest* water level within an ebb and flow cycle.

    # Maybe a better approach is to compare the low tide with the high tide, item [0] with item [1] etc.
    # The rule of 12ths is applied to a half a cycle of the curve,
    # because we go from high tide to low tide and 'back' again.

# Borrowed from: https://stackoverflow.com/questions/1011938/loop-that-also-accesses-previous-and-next-values
# Provide a dictionary and it will return the current and the following item
# If we had used two lists (for the dates and water levels) it would have been easier to navigate the current/next items (e.g. item[i] -> item[i+1])
def previous_and_next(some_iterable):
    items, nexts = tee(some_iterable, 2)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(items, nexts)

def calculate_intermediate_values(item, nxt, water_level_item, water_level_nxt):
    # Below is wrong:
    # Use %I to request the hour (in 12-hour format) and cast it as an int()
    # currenthour = int(item.strftime('%I'))
    # nexthour = int(nxt.strftime('%I'))
    # Calculate the difference in time and difference in water level
    # timedifference = abs(nexthour - currenthour)

    # This is correct:
    # First substract the current datetime from the next datetime
    td = nxt - item
    # td is now a timedelta object, we want to select the hours only.
    # Timedelta objects don't have a function to retrieve the hours, so we get the seconds and divide by 3600
    timedifference = td.seconds//3600
    waterdifference = abs(water_level_nxt - water_level_item)

    #print("NEXTHOUR {}  CURRENTHOUR {}".format(abs(nexthour), abs(currenthour)))

    # Compare the current and next tide, and calculate the water levels for the hours inbetween the known values.
    # Are we in a high or low tide?
    if (water_level_item > water_level_nxt):
        hightide = 1
    else:
        hightide = 0

    # The rule of 12ths assumes there are two peaks and a bottom in a 12 hour period
    # This doesn't always match our data, so we come with some different options:
    if (timedifference == 6):
        # https://en.wikipedia.org/wiki/Rule_of_twelfths
        # The rule is: 1/12, 2/12, 3/12 etc.
        # But here I've just used the *actual* values from the Wiki
        rule_increments = [0, 0.06699, 0.18301, 0.25, 0.25, 0.18301, 0.06699]
    elif (timedifference == 5):
        # This is just a rough estimation (without proof):
        # 1/9, 2/9, 3/9, 2/9, 1/9
        rule_increments = [0, 0.11111111, 0.22222222, 0.33333333, 0.22222222, 0.11111111]
    elif (timedifference == 7):
        # This is just a rough estimation (without proof):
        # 1/16, 2/16, 3/16, 4/16, 3/16, 2/16, 1/16
        rule_increments = [0, 0.0625, 0.125, 0.1875, 0.25, 0.1875, 0.125, 0.0625]

    # Add the current item to the new dictionary first
    new_dict[item] = (water_level_item)
    water_level_intermediate = water_level_item
    #print("Water difference: {} Time difference: {}".format(waterdifference, timedifference))
    #print("Current item: {} water level: {}".format(item, water_level_item))

    # Loop while there are hours remaining between the current tide (item) and the next (nxt)
    i = 0
    while(i < timedifference):
        item_plus_one = item + timedelta(hours=i)
        # Use the increments to calculate the intermediate values and add them to the dictionary
        # If we start with a low tide, add increments. If we start with a high tide, substract increments
        if(hightide == 0):
            water_level_intermediate = water_level_intermediate + (waterdifference * rule_increments[i])
            new_dict[item_plus_one] = (water_level_intermediate)
        else:
            water_level_intermediate = water_level_intermediate - (waterdifference * rule_increments[i])
            new_dict[item_plus_one] = (water_level_intermediate)
        #print("Newitem: {} Water level intermediate: {}".format(item_plus_one, water_level_intermediate))
        i += 1

    #print("Next item: {} water level: {} \n \n".format(nxt, water_level_nxt))
    return True

def average_ebb_and_flow():
    # Calculate the average of all ebbs and the average of all flows
    ebb = 0
    flow = 0
    for water in dict.items():
        if water < 0:
            ebb += water
        else:
            flow += water
    dictsize = len(dict) / 2
    average_ebb = ebb / dictsize
    average_flow = flow / dictsize
    print("\nAverage tides: \nEbb: {} Flow: {}\n".format(average_ebb, average_flow))

def rule_of_12ths():
    # We compare two values, high tide and low tide.
    # Together they make up for approximately a 6 hour period.
    # First we figure out if we start with a high tide or a low tide

    # The dictionary contains: key[datetime object] and value [water level]
    # print("Number of items in our dictionary: {} \n".format(len(dict)))

    for item, nxt in previous_and_next(dict):
        if nxt == None:
            # Stop the loop when there is no next item available.
            break
        #Show which items we're talking about:
        calculate_intermediate_values(item, nxt, dict[item], dict[nxt])

    #print("Number of items in our new dictionary after calculating the rule of 12'ths: {} \n".format(len(new_dict)))
    #print(365*24)
    #Result: 8751 -- 8760.
    #There's missing 9 hours.

data = {}
def fetch_data():
    # Connect with the API
    # Using the following parameters:
    # API key=7216c782-6b41-4c8b-8801-4b5370e3e9ba
    # stationId= 22332 (Station name: Århus Havn I, latitude: 56,1466 longitude: 10,2226 see for details: https://confluence.govcloud.dk/pages/viewpage.action?pageId=30015718)
    # Station on Google Maps: https://www.google.com/maps/place/56%C2%B008'47.8%22N+10%C2%B013'21.4%22E/@56.1463894,10.1956551,13.51z/data=!4m5!3m4!1s0x0:0x550961a1a7095293!8m2!3d56.1466!4d10.2226
    # periode=latest-month
    # limit=10000 (This defines the max number of items that are returned. If not defined, it's set to 1000.)
    # parameterId= sealev_dvr (Pick one of the three available measurements for each timeslot, see specification here: https://confluence.govcloud.dk/pages/viewpage.action?pageId=30015716&fbclid=IwAR09lDnKrgfv3HpLY8ACodUUX8t-snkuxLtXH8UiCQo16QXLGbTgyXt-Ij8)
    # Note that the water temperature is also available via parameterId.
    with urlopen("https://dmigw.govcloud.dk/v2/oceanObs/collections/observation/items?api-key=7216c782-6b41-4c8b-8801-4b5370e3e9ba&stationId=22331&period=latest-month&limit=100000&parameterId=sealev_dvr") as response:
        source = response.read()
    data_json = json.loads(source)

    for feature in data_json['features']:
        # Observed time format: 2022-03-09T01:10:00Z
        #                        Year-Month-Day Hour:Minute:Second Timezone
        # Strip the :00Z at the end.
        feature["properties"]["observed"] = feature["properties"]["observed"].replace(':00Z','')
        # Change the date to a datetime object:
        feature["properties"]["observed"] = datetime.strptime(feature["properties"]["observed"], '%Y-%m-%dT%H:%M')
        # Add an hour (fix timezone difference)
        feature["properties"]["observed"] = feature["properties"]["observed"] + timedelta(hours=1)
        # There is one ugly outlier in the data, crudely ignore it:
        if feature["properties"]["value"] < 200:
            data[feature["properties"]["observed"]] = feature["properties"]["value"]
    return True

def plot():
    observedWaterList = []
    observedDateList = []
    for date in data.keys():
        #print("plot.date: {}".format(date))
        observedWaterList.append(data[date])
        observedDateList.append(date)
    plt.plot(observedDateList, observedWaterList)

    predictedWaterList = []
    predictedDateList = []
    for date in new_dict.keys():
        # Only show data for the last 30 days:
        delta = datetime.now() - date
        if int(delta.days) < 30 and delta.days > -1:
            predictedWaterList.append(new_dict[date])
            predictedDateList.append(date)

    plt.plot(predictedDateList, predictedWaterList)
    plt.ylabel('Predicted and observed water levels')
    plt.xlabel('Date')
    plt.show()
    return True

def write_data():
    # This writes the expected tides (not the observed).
    try:
        with open("ruleof12ths.txt", "w") as file:
            # Loop through the dictionary new_dict and add a new line with the date and values, seperated with comma's and a new line at the end.
            for keys, value in new_dict.items():
                keys = keys.strftime('%d-%m-%y %H:%M')
                #value = round(value, 2)
                file.write("{},{},\n".format(keys, value))
        return "TXT file created"
    except:
        return "Unable to create TXT file"

rule_of_12ths()
fetch_data()
plot()
#print(write_data())