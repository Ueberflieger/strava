# Strava-Kudos

A script to give kudos to your Strava friends based on activity goals.

Currently it supports:
* running
* cycling
* swimming
* kayaking

## Usage

```
usage: strava.py [-h] -p PASSWORD -u USERNAME -n NUM_ACTIVITIES

optional arguments:
  -h, --help            show this help message and exit
  -p PASSWORD, --password PASSWORD
                        Password for strava, won't be stored
  -u USERNAME, --username USERNAME
                        Username for strava
  -n NUM_ACTIVITIES, --n_activities NUM_ACTIVITIES
                        Number of activities to check

```

## `user.json`

The file `user.json` contains the activiy goals that are checked against your friends uploaded activities.

It has following structure:

```
{
    "group_activity_all_kudos": "yes", // give kudos if it's a group activity
    "ignore":[], // list of people to ignore, add athlete ids here not names
    "vip":[], // people who receive kudos for every activity
    "default": // defaults for activities
    {
        "run": {"distance_km": "12", "pace_km":"5:00"}, 
        "swim":{"pace_100m":"2:00"}, 
        "ride":{"distance_km": "30"},
        "kayaking":{"time": "1:00:00"}
    },
    "athletes": // individual activity goals, these overwrite the default goals
    {
        "123456":// your friends strava id
        { 
            "name": "Your Friend 1", 
            "criteria":
            { 
                "run":{"pace_km":"4:30", "distance_km":"14"}
            }
        },
        "234567":
        { 
            "name": "Your Friend 2", 
            "criteria":
            { 
                "swim":{"pace_100m":"1:30"}
            }
        }
    }
}

```


## Todo

* based on button figure out if this is the users own activity
* reorder functions
