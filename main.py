from datetime import datetime, timedelta
from itertools import tee, islice, chain
import matplotlib.pyplot as plt
from urllib.request import urlopen
import json
import requests

def hour_rounder(t):
    # Rounds to nearest hour by adding an hour (using timedelta) if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute // 30))

dict = {}
new_dict = {}
# Take the file tidevand.txt and read the lines, then add them to the dictionary dict.
with open('tidevand.txt') as file:
    for line in file.readlines():
        line = line.split()
        line[0] = datetime.strptime(line[0], '%Y%m%d%H%M')
        # Because we don't want to deal with the minutes, we'll round up to the nearest hour
        line[0] = hour_rounder(line[0])
        dict[line[0]] = int(line[1])

def previous_and_next(some_iterable):
    items, nexts = tee(some_iterable, 2)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(items, nexts)

def calculate_intermediate_values(item, nxt, water_level_item, water_level_nxt):
    td = nxt - item
    # td is now a timedelta object, we want to select the hours only.
    # Timedelta objects don't have a function to retrieve the hours, so we get the seconds and divide by 3600
    timedifference = td.seconds // 3600
    waterdifference = abs(water_level_nxt - water_level_item)

    # We compare two values, high tide and low tide.
    # Together they make up for approximately a 6 hour period.
    # First we figure out if we start with a high tide or a low tide
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
    if (timedifference == 5):
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

    i = 0
    while (i < timedifference):
        item_plus_one = item + timedelta(hours=i)
        # Use the increments to calculate the intermediate values and add them to the dictionary
        # If we start with a low tide, add increments. If we start with a high tide, substract increments
        if (hightide == 0):
            water_level_intermediate = water_level_intermediate + (waterdifference * rule_increments[i])
            new_dict[item_plus_one] = (water_level_intermediate)
        else:
            water_level_intermediate = water_level_intermediate - (waterdifference * rule_increments[i])
            new_dict[item_plus_one] = (water_level_intermediate)
        i += 1
    return True


def rule_of_12ths():
    # The dictionary contains: key[datetime object] and value [water level]
    for item, nxt in previous_and_next(dict):
        if nxt == None:
            # Stop the loop when there is no next item available.
            break
        # Show which items we're talking about:
        calculate_intermediate_values(item, nxt, dict[item], dict[nxt])
    return new_dict

########## molslinjen_API ##########
# This function accesses data from molslinjen.dk through their API. The goal is to retrieve ferry arrival times.
# Inspecting https://www.molslinjen.dk/fartplan i find data to be passed under getdepartures/network/payload
# Using requests and the post-method, I pass 'departure_data' and get a response object.
# The following line shows list of lists of dictionaries contained in the response-object from molslinjen-API.
#[[{'id': 'SJÆ_3_20220330_0720', 'date': '2022-03-30T00:00:00', 'departureTime': '07:20:00', 'arrivalTime': '08:35:00',

def get_ferry_arrival_time(date=None):
    date = date or datetime.today()
    date = date.strftime("%Y-%m-%d")
    departure_data = {
        "date": date,
         "departureRegionId": "SJÆ",
         "transportId": "10",
         "softPassengersOnly": "False"
        }
    departure_url = "https://www.molslinjen.dk/umbraco/api/departure/getdepartures"
    response = requests.post(departure_url, json=departure_data)
    dictionary = {}
    # Iterates over response object. "resp" = de to ydre lister. "arrival" = a dictionary for each departure is
    for resp in response.json():
         for arrival in resp:
            # Checks if arrival-item is a dictionary
            # This is necessary as there is a  0 at the at the end of the data that causes an error otherwise
            if not isinstance(arrival, type(dict)):
                continue

            # Skip if the ferry departure has been cancelled.
            if arrival.get("cancelled"):
                 continue

            if arrival.get("arrivalTime"):
                # Checks if there is a key in the dictionary. Will skip to else clause otherwise.
                # "departure_data["date"]" = the key in our dictionary. This is the date we send as payload at the
                # start of this function. The values for the key = a list of arrival times.
                if departure_data["date"] in dictionary:
                    # "opens" arrival time  list
                    tmp_list = dictionary[departure_data['date']]
                    # appends to arrival time list
                    tmp_list.append(arrival.get("arrivalTime"))
                    # Puts the list back in dictionary
                    dictionary[departure_data['date']] = tmp_list
                # if the dictionary is empty, the above code would fail. The else-clause runs on first run.
                else:
                    dictionary[departure_data["date"]] = [arrival.get("arrivalTime")]

    # In order to use the arrival times in a plot we need them combined as a list of datetime strings of date + time
    datetime_strings = []
    for key, value in dictionary.items():
        for time in value:
            datetime_string = f"{key} {time}"
            datetime_strings.append(datetime_string)
    return datetime_strings

def fetch_data():
    ocean_obs = {}
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
        feature["properties"]["observed"] = feature["properties"]["observed"].replace(':00Z', '')
        # Change the date to a datetime object:
        feature["properties"]["observed"] = datetime.strptime(feature["properties"]["observed"], '%Y-%m-%dT%H:%M')
        # Add an hour (fix timezone difference)
        feature["properties"]["observed"] = feature["properties"]["observed"] + timedelta(hours=1)
        # There is one ugly outlier in the data, crudely ignore it:
        if feature["properties"]["value"] < 200:
            ocean_obs[feature["properties"]["observed"]] = feature["properties"]["value"]
    return ocean_obs

def plot():
    ocean_obs = fetch_data()
    dateList = list(ocean_obs.keys())
    waterList = list(ocean_obs.values())
    showObserved = True
    if (showObserved == True):
        observedWaterList = []
        observedDateList = []
        for date in ocean_obs.keys():
            # print("plot.date: {}".format(date))
            observedWaterList.append(ocean_obs[date])
            observedDateList.append(date)
        plt.plot(observedDateList, observedWaterList)

    # Loads and plots Molslinjen arrival times
    ferry_datetimes = get_ferry_arrival_time()
    # min_water is used to set the level of y-axis in order to plot the arrival scatter points at a lower point.
    min_water = min(waterList)
    y_axis = list([min_water for f in ferry_datetimes])
    plt.scatter(ferry_datetimes, y_axis)

    predictedWaterList = []
    predictedDateList = []

    for date in new_dict.keys():
        # Only show data for the last 30 days:
        delta = datetime.now() - date
        if int(delta.days) < 30 and delta.days > -1:
            predictedWaterList.append(new_dict[date])
            predictedDateList.append(date)

    # Do you want the points connected or not?
    connectPoints = True
    if (connectPoints == False):
        plt.plot(predictedDateList, predictedWaterList, 'ro')
    else:
        plt.plot(predictedDateList, predictedWaterList)
    plt.ylabel('Water levels')
    plt.xlabel('Date')
    plt.show()
    return True

# Get the predicted water level heights from the txt file and calculate the intermediate values:
rule_of_12ths()
# Connect with the DMI API and fetch the observed water levels:
#fetch_data()
# Use the Molslinjen API to fetch the ferry arrival time:
#get_ferry_arrival_time()
# Draw a simple graph with PyPlot:
plot()