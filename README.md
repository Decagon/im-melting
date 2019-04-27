# im-melting
I'm melting: optimally schedule public transit routes to minimize exposure to rain.

I want to get from A to B, but I don't want to get wet. `im-melting` will tell you when you have to leave for a public transit route which will ensure that you won't get wet, or will minimize it. This includes choosing a longer route if the rain will last for a long time, so that you stay nice and dry on the bus. Where data exists, it will choose transfers which have covered bus stops. This includes getting off the bus early and walking to another stop if it is not raining, but will ultimately minimize your total walking time in the rain.

## How to run

Run `python3 im-melting.py` and follow the on-screen instructions. Requires a Google Maps API key (free) and an AccuWeather API Key (free) to get the directions and getr the weather.

## Sample output

```
What is your current location? Vancouver, British Columbia
Where would you like to go? Vancouver Aquarium, 845 Avison Way, Vancouver, BC V6G 3E2
Downloading weather forecast... This may take several minutes...
Out of 4 routes, the best route will only be 0 units of rain
Subway towards Expo Line to King George (2 mins)
Walk to Westbound W Pender St @ Burrard St (3 mins)
Bus towards 19 Stanley Park (8 mins)
Walk to 845 Avison Way, Vancouver, BC V6G 3E2, Canada (10 mins)
```

Currently, `im-melting` just calculates the current routes if you were to leave right now, and finds the one where you'd get the least wet. In the future, additional routes in the future will be used once I figure out how to use the Google Maps API to change the startTime.

## Roadmap

This will first find all transit routes to the destination for this entire day using Google Transit API. It will then use AccuWeather's MinuteCast API to find the forecast on a minute-per-minute interval for the next two hours. The time it takes to walk to the stop and to walk to the destination will be converted into absolute times, then the transit routes will be shifted such that the walking times' total rain amount will be minimized using brute-force.

If more than one solution exists, then the route that leaves the earliest or has the lowest walking time will be chosen.

### How wet will I get?

Humidity, temperature, air pressure, wind speed, amount of rain, time spent in bus and estimated bus convection heating, dew point, presumed material (e.g. cotton for summer, sweaters for fall, and jackets for winter), and time spent in the rain can be used to calculate total wetness levels and final destination wetness level using thermodynamics equations with respect to a perfectly dry self. 

### But what if it's raining for the next two hours?

The solution will be chosen based on the minimum time it will be raining. The user can also choose how wet they'd like to be at most, and that will keep checking the Weather API as to when the user should leave, however, this means that a solution might not be able to be found if it is raining the entire day. Where data exists, a route could be chosen such that the user is only dropped off to covered bus stops, so that they would not have to get wet for their next transfer.

### I don't want to take the bus, I just want to walk

If the route is short enough, it will automatically suggest walking as a route.

