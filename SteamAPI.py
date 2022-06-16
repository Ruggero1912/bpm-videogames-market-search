import requests, json, time
from datetime import datetime

class SteamAPI:
    __STEAM_API_BASE_URL = "https://store.steampowered.com/api/{API}" #appdetails/?appids=413680&l=english
    __STEAM_API_APP_DETAILS_URL = __STEAM_API_BASE_URL.format(API="appdetails/")

    __WAIT_TIMER = 300  # 5 minutes

    def print_api_url():
        print(SteamAPI.__STEAM_API_APP_DETAILS_URL)

    def get_app_details(app_id, language='english'):
        """
        receives as input a Steam app_id and returns a dict containing all the app details or null if the app_id was not found
        """
        params = {
            "l" : language,
            "appids" : app_id
        }
        response = requests.get(SteamAPI.__STEAM_API_APP_DETAILS_URL, params=params)

        if(response.status_code == 429):
            print("\n[{datetime}]You have been banned, going to lock the script for {x} seconds :) After that time I will retry the request for the app_id '{app_id}'...".format(x=SteamAPI.__WAIT_TIMER, app_id=app_id, datetime=datetime.now()))
            time.sleep(SteamAPI.__WAIT_TIMER)
            return SteamAPI.get_app_details(app_id, language=language)


        if(response.text in [None, "null"] or response.status_code != 200):
            print(f"There was an error handling the request for the app id {app_id}, status code: {response.status_code}, response.text: {response.text}")
            return None
        dict_response = json.loads(response.text)
        return dict_response

    def get_genres(app_id=None, app_dict=None) -> list:
        """
        returns a list of genres associated to the specified game
        - if no genres is associated, returns an empty list
        - if no 'data' field is found for the app or the app_id is not found, this method return None
        """
        if(app_id == None and app_dict == None):
            print("No info given, cannot get genre")
            return None
        if(app_id is not None and type(app_id) != str):
            app_id = str(app_id)
        if(app_dict is None):
            app_dict = SteamAPI.get_app_details(app_id)

        if(app_dict is None):
            print("Cannot get app infos from the API for the app_id " + app_id)
            return None

        if(app_id is None or str(app_id) not in app_dict.keys()):
            app_id = list( app_dict.keys() ) [0]

        if('data' not in list(app_dict[app_id])):
            print("No 'data' key from the API for the app_id " + app_id + " | received dict: ", app_dict)
            return None

        if('genres' not in list(app_dict[app_id]['data'])):
            print("No 'genres' key from the API for the app_id " + app_id + " | received dict: ", app_dict)
            return []

        return app_dict[app_id]['data']['genres']
