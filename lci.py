from typing import List
import tweepy
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime
import dataclasses
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import json

# the bearer token is not public, so it is not included in the repo
# you can get yours  signing up for a twitter developer account
from apikey import bearer_token


@dataclasses.dataclass
class CityData:
    name: str
    times: List[str] = dataclasses.field(default_factory=list)
    counts: List[int] = dataclasses.field(default_factory=list)
    population: int = 0
    # location for plotting
    long: float = 0
    lat: float = 0


def get_city_tweets(twtr_client, citydata):
    """
    Get number of tweets for a city
    :param twtr_client: tweepy client
    :param citydata: CityData object to be filled
    """
    # thats ~ when the invasion started, earlier is not significant
    query_start_time = datetime(2022, 2, 28, 0, 0, 0)

    search_string = f"#Ukraine {citydata.name}"
    response = twtr_client.get_recent_tweets_count(search_string,
                                                   start_time=query_start_time)

    for d in response.data:
        e_time = datetime.strptime(d["end"], "%Y-%m-%dT%H:%M:%S.%fZ")
        citydata.times.append(e_time)
        citydata.counts.append(d["tweet_count"])
    return citydata


def get_city_data(twtr_client, ctyjson):
    """
    Get data for all cities in the json
    :param twtr_client: tweepy client
    :param ctyjson: json with cities
    """
    city_data_list = []
    for city in ctyjson:
        city_data = CityData(city["city"],
                             long=float(city["lng"]),
                             lat=float(city["lat"]),
                             population=int(city["population"]))
        city_data = get_city_tweets(twtr_client, city_data)
        city_data_list.append(city_data)
    return city_data_list


def plot_city_data(citydata, mapfile, ax=None):
    ukr_df = gpd.read_file(mapfile)
    ax = ukr_df.plot(ax=ax)
    for c in citydata:
        ax.scatter(c.long, c.lat, color="black")
        ax.annotate(c.name, (c.long + 0.1, c.lat + 0.1), fontsize=8)
        ax.scatter(c.long, c.lat, color="red", s=c.counts[-1], alpha=0.3)
    plt.show()


def plot_city_timeline(city_data_list):
    for cd in city_data_list:
        plt.plot(cd.times, cd.counts, label=f"{cd.name}")
    plt.legend()
    myFmt = mdates.DateFormatter('%D %H:%M')
    plt.gca().get_xaxis().set_major_formatter(myFmt)
    plt.show()


def plot_key_events(cd_list):
    # https://en.wikipedia.org/wiki/2022_Russian_invasion_of_Ukraine
    # https://en.wikipedia.org/wiki/Timeline_of_the_2022_Russian_invasion_of_Ukraine
    key_events = [
        [" Inital attacks", datetime(2022, 2, 24, 3, 0, 0)],
        [" Kyiv attacks", datetime(2022, 2, 25, 4, 0, 0)],
        [" Kyiv attacks", datetime(2022, 2, 26, 0, 0, 0)],
        [" Kharkiv pipeline",
         datetime(2022, 2, 27, 3, 0, 0)],
    ]

    fig, ax = plt.subplots()
    # plot activity timeline
    for cd in cd_list:
        ax.plot(cd.times[:-1], cd.counts[:-1], label=f"{cd.name}")
    ax.legend()
    for e in key_events:
        ax.axvline(e[1], color="black", linestyle="--")
        ax.annotate(e[0], (e[1], 12000), fontsize=7)
    ax.set_ylabel("Number of twitter mentions")
    plt.title("Twitter mentions and notable events")
    plt.show()


def write_data_to_file(city_data_list, filename):
    with open(filename, "w") as f:
        names = [cd.name for cd in city_data_list]
        f.write("time;" + ";".join(names) + "\n")
        for i in range(len(city_data_list[0].times)):
            f.write(city_data_list[0].times[i].strftime("%Y-%m-%d %H:%M:%S") +
                    ";")
            f.write(";".join([str(cd.counts[i])
                              for cd in city_data_list]) + "\n")


class UpdateCityData:

    def __init__(self, ax, cd_list, mapfile):
        """
        Class used for animating the map and the tweet activity
        Mostly taken from https://matplotlib.org/stable/gallery/animation/bayes_update.html
        :param ax: matplotlib axis: List of axis to plot on -> contains 2 axis
        :param cd_list: list of CityData objects
        :param mapfile: path to map file containing geodata for Ukraine
        """
        ukr_df = gpd.read_file(mapfile)
        self.ax_map = ax[1]
        self.ax_map.set_axis_off()
        self.ax_time = ax[0]
        self.ax_time.set_ylabel("Number of twitter mentions")
        self.ax_map.set_title(f"{cd_list[0].times[0]}")
        # plot activity timeline
        for cd in cd_list:
            self.ax_time.plot(cd.times, cd.counts, label=f"{cd.name}")
        self.ax_time.legend()
        self.timestamp = self.ax_time.axvline(cd_list[0].times[10],
                                              linestyle='--',
                                              color='black')
        # format the date so it doesnt show the year
        myFmt = mdates.DateFormatter('%D %H:%M')
        self.ax_time.xaxis.set_major_formatter(myFmt)

        # plot map and cities
        self.ax_map = ukr_df.plot(ax=self.ax_map)
        for c in cd_list:
            self.ax_map.scatter(c.long, c.lat, color="black")
            self.ax_map.annotate(c.name, (c.long + 0.1, c.lat + 0.1),
                                 fontsize=8)

        self.count_scale_factor = 3
        # scale by population and a factor for visibility
        self.tweet_activity = self.ax_map.scatter(
            [c.long for c in cd_list], [c.lat for c in cd_list],
            color="red",
            s=[(3_000_000 / c.population) *
               (c.counts[0] / self.count_scale_factor) for c in cd_list],
            alpha=0.3)
        self.cd_list = cd_list

    def __call__(self, i):
        self.ax_map.set_title(f"{self.cd_list[0].times[i]}")
        # update activity markers
        # scale by population and a factor for visibility
        self.tweet_activity.set_sizes([(3_000_000 / c.population) *
                                       (c.counts[i] / self.count_scale_factor)
                                       for c in self.cd_list])
        # update timeline indicator
        t_now = mdates.date2num(self.cd_list[0].times[i])
        self.timestamp.set_xdata([t_now, t_now])


def main():
    client = tweepy.Client(bearer_token)
    cities_file = "geodata/ua.json"
    ukr_geofile = "geodata/custom.geo.json"

    # some weird characters in the file, ignoring is fine
    with open(cities_file, errors="ignore") as f:
        city_json = json.load(f)
        city_json = city_json[:15]

    city_data_list = get_city_data(client, city_json)
    current_date = datetime.now()
    write_data_to_file(city_data_list,
                       f"data/{current_date.strftime('%Y-%m-%d')}.csv")

    plot_city_timeline(city_data_list)
    #plot_key_events(city_data_list)

    fig, ax = plt.subplots(2, 1, figsize=(8, 10))
    fig.suptitle("Ukrainian city mentions on twitter")
    ucd = UpdateCityData(ax, city_data_list, ukr_geofile)
    anim = FuncAnimation(fig,
                         ucd,
                         frames=range(len(city_data_list[0].counts)),
                         save_count=len(city_data_list[0].counts),
                         interval=200,
                         repeat=False)

    plt.tight_layout()
    anim.save('media/animation2.gif', writer='imagemagick')


if __name__ == "__main__":
    main()
