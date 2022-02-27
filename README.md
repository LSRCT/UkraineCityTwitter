# UkraineCityTwitter
Visualize the invasion using twitter data.
I strongly condemn the russian invasion of ukraine.

## Idea
The basic idea behind this project is that twitter data should reflect the russian attacks on ukraine. 

In the following twitter data is gonna be parsed, filtering by "#Ukraine" and specific cities to localize the attacks.

## City Data
In order to limit the amount of twitter API requests only the 15 most populated cities will be analized. 
For each city the number of tweets mentioning it is requested by the twitter API. A mention is defined as a tweet containing "#Ukraine {cityname}"

This number of tweets, twittered during certain timespan, is assumed to be an indicator about a potential attack on the city.
To compensate for different city sizes, the number of tweets is rescaled using the population count of the city.

## Geodata
The data used for city population and location is taken from https://simplemaps.com/data/ua-cities
Vectordata for the Ukraine map background was obtained from https://geojson-maps.ash.ms/

## Results
In the following the results for the top 15 cities are displayed. The top graph shows the amount of mentions for each city since the initial attacks, the bottom one is an animation of the activity at a certain time.

![](media/animation.gif)

## Notable events
Next the claim that twitter mentions are indicators for attacks is checked.
In the plot below the some notable events are as well as the twitter mentions per city is shown.
It is clear that there is some correlation between events and the number of mentions, although not all features are explained by the events. 
![](media/timeline.png)

(events take from https://en.wikipedia.org/wiki/2022_Russian_invasion_of_Ukraine and https://en.wikipedia.org/wiki/Timeline_of_the_2022_Russian_invasion_of_Ukraine)

## Further work
- Refine twitter query: Include negativity to filter attacks
- Add more notable events

## Libraries
This project was created using:
- geopandas
- tweepy
- matplotlib

## Слава Україні!
