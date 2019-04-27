from bs4 import BeautifulSoup
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
import json
import spectra
import requests
import urllib
from pyvirtualdisplay import Display
from selenium import webdriver

GOOGLE_MAPS_API_KEY = ""
ACCUWEATHER_API_KEY = ""
startLocation = urllib.parse.quote(input("What is your current location? "))
endLocation = urllib.parse.quote(input("Where would you like to go? "))

googleMapsHTML = requests.get("https://maps.googleapis.com/maps/api/directions/json?origin=" + startLocation + "&destination=" +
                              endLocation + "&key=" + GOOGLE_MAPS_API_KEY + "&mode=transit&alternatives=true").content
routes = json.loads(googleMapsHTML.decode('utf-8'))["routes"]

# lookup the accuweather link based on the starting location's GPS coordinates
geoCoords = routes[0]['legs'][0]['start_location']  # lat and lng
accuweatherLink = ""
accuweatherGeoLookupLink = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=" + \
    ACCUWEATHER_API_KEY + "&q=" + \
        str(geoCoords["lat"]) + "%2C" + str(geoCoords["lng"]) + "&details=true"
accuweatherMinuteCast = requests.get(accuweatherGeoLookupLink).content

datastore = json.loads(accuweatherMinuteCast.decode("utf-8"))

host = "https://www.accuweather.com/en/"
locationStem = datastore["Details"]["LocationStem"]
key = datastore["Details"]["Key"]
accuweatherLink = host + locationStem + "/minute-weather-forecast/" + key

# this is very heavy-duty because AccuWeather times out using anything else with any other user agents
# (e.g. the requests library) or throws a 401 unauthorized error
print("Downloading weather forecast... This may take several minutes...")

display = Display(visible=0, size=(800, 800))
display.start()

driver = webdriver.Chrome()
driver.get(accuweatherLink)


intensities = [
    "fff", "49e953", "02bf25", "189708", "016704", "005600", "004101", "f1d600", "f7a501", "ff5f01", "f01100", "b70902", "500200", "ff0991", "8c03cf",
              "a863cd"]

resultantIntensities = []
soup = BeautifulSoup(driver.page_source, "lxml")
driver.close()
output = soup.find("div", class_="graphic")

# find all of the colors
for anElement in output.find_all("span"):
    # hex color
    aColor = anElement.get("style").replace("background-color:#", "")
    aColorLab = spectra.html("#" + aColor).to("lab").values

    # find the color that closely matches the one that we already know about
    referenceColor = LabColor(
        lab_l=aColorLab[0], lab_a=aColorLab[1], lab_b=aColorLab[2])

    smallest_e = 999
    closestIndex = 0
    # find the closest matching color in the list
    for anIntensity in intensities:
        aHexIntensity = spectra.html("#" + anIntensity).to("lab").values
        aLabIntensity = LabColor(lab_l=aHexIntensity[
                                 0], lab_a=aHexIntensity[1], lab_b=aHexIntensity[2])
        delta_e = delta_e_cie2000(aLabIntensity, referenceColor)
        if (smallest_e > delta_e):
            smallest_e = delta_e
            closestIndex = intensities.index(anIntensity)

    resultantIntensities.append(closestIndex)

results = []

for route in routes:
    routePackage = []
    legs = route["legs"]
    for leg in legs:
        departure_time = leg["departure_time"]
        arrival_time = leg["arrival_time"]
        steps = leg["steps"]
        for step in steps:
            duration_minutes = round(
                int(step["duration"]["value"]) / 60)
            travel_mode = step["travel_mode"]
            instructions = step["html_instructions"]
            routePackage.append(
                [travel_mode, duration_minutes, instructions])
    results.append(routePackage)
    routePackage = []

minTotalRain = 999
bestRouteSoFar = ""
for aRoute in results:
    currPointer = 0
    totalRain = 0
    for aStep in aRoute:
        endTime = aStep[1]
        if (aStep[0] == 'WALKING'):
            # sum all rainfall amounts from the current pointer up to this step
            totalRain = totalRain + \
                sum(resultantIntensities[currPointer:currPointer + endTime])
        currPointer = currPointer + endTime
    if (minTotalRain > totalRain):
        minTotalRain = totalRain
        bestRouteSoFar = aRoute


print("Out of " + str(len(results)) +
      " routes, the best route will only be " + str(minTotalRain) + " units of rain")

for aStep in bestRouteSoFar:
    print(aStep[2] + " (" + str(aStep[1]) + " mins)")
