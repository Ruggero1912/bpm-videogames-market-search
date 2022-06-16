import json
import requests

from Utils import Utils

class IGDBAPI:
    __API_BASE_URL = "https://api.igdb.com/v4/{API}"    #https://api.igdb.com/v4/keywords
    __KEYWORDS_URL = __API_BASE_URL.format(API="keywords")
    __GAMES_URL = __API_BASE_URL.format(API="games")
    __GENRES_URL = __API_BASE_URL.format(API="genres")
    __TWITCH_CLIENT_ID = Utils.load_config("TWITCH_CLIENT_ID")
    __TWITCH_CLIENT_SECRET = Utils.load_config("TWITCH_CLIENT_SECRET")
    __TWITCH_API_ENDPOINT = "https://id.twitch.tv/oauth2/token"
    __API_TOKEN = None
    __API_TOKEN_INFOS = None
    __HEADERS = None

    __IGDB_API_MAXIMUM_LIMIT = 500

    def __load_api_token() -> bool:
        query_parameters = {
            "client_id" : IGDBAPI.__TWITCH_CLIENT_ID,
            "client_secret": IGDBAPI.__TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        response = requests.post(IGDBAPI.__TWITCH_API_ENDPOINT, params=query_parameters)
        if(response.status_code != 200):
            print("An error occurred when trying to obtain the token from twitch")
            return False
        IGDBAPI.__API_TOKEN_INFOS = response.json()
        IGDBAPI.__API_TOKEN = IGDBAPI.__API_TOKEN_INFOS["access_token"]
        IGDBAPI.__HEADERS = {
            "Client-ID": IGDBAPI.__TWITCH_CLIENT_ID,
            "Authorization": "Bearer {api_token}".format(api_token=IGDBAPI.__API_TOKEN)
        }
        return True
        """
        response is in the format:
                {
        "access_token": "access12345token",
        "expires_in": 5587808,
        "token_type": "bearer"
        }
        """

    #the categories in IGDB are identified by an enum

    def get_genres(all=True, how_many=-1, limit=-1, offset=0) -> list:
        """
        returns a list of dict of categories
        - because of pagination we have to make more than one request if the results are many
        - the maximum limit of results per request are 500
        """
        if IGDBAPI.__API_TOKEN is None:
            IGDBAPI.__load_api_token()

        query = f"fields *; offset {offset}; "
        if type(limit) != int or limit <= 0:
            limit = IGDBAPI.__IGDB_API_MAXIMUM_LIMIT
        query += f"limit {limit};"

        if all is False and how_many > 0:
            how_many -= limit

        r = requests.post(IGDBAPI.__GENRES_URL, headers = IGDBAPI.__HEADERS, data = query)
        if(r.status_code != 200):
            print("error http: {type}".format(type=r.status_code), r.text)
            return []
        if all is False and how_many == 0:
            return r.json()
        elif len(r.json()) == 0:
            return r.json()
        else:
            return r.json() + IGDBAPI.get_genres(all, how_many, limit, offset + limit)

    DEFAULT_GENRE  = 5 #5,1297555200,Shooter,shooter,1323216000

    def get_most_popular_games(genre_id : int, limit=500) -> list:
        """
        - @return list of popular games for the specified genre
        - there is no check on the validity of the specified genre
        """
        if limit <= 0:
            limit = IGDBAPI.__IGDB_API_MAXIMUM_LIMIT

        if IGDBAPI.__API_TOKEN is None:
            IGDBAPI.__load_api_token()
        
        query = f"fields *; where keywords != null; where total_rating_count != null; sort total_rating_count desc; limit: {limit};"  #sort popularity does not work!

        print("Going to request the games with the following query for the genre '{genre_id}' query: ".format(genre_id=genre_id), query)

        r = requests.post(IGDBAPI.__GAMES_URL, headers = IGDBAPI.__HEADERS, data = query)

        if(r.status_code != 200):
            print("error http: {type}".format(type=r.status_code), r.text)
            return []

        return r.json()

    def get_keywords_details(keyword_ids : list) -> list:
        
        if IGDBAPI.__API_TOKEN is None:
            IGDBAPI.__load_api_token()

        limit = len(keyword_ids)

        if limit > IGDBAPI.__IGDB_API_MAXIMUM_LIMIT:
            print(f"WARNING: trying to request in one request too much data! The maximum limit is {IGDBAPI.__IGDB_API_MAXIMUM_LIMIT} requested {limit}")

        query = "fields *; where id = ({ids}); limit {limit};".format(ids=",".join(map(str,keyword_ids)), limit=limit)

        print("Going to request the keywords details for {x} keywords with the following query: ".format(x=len(keyword_ids)), query)

        r = requests.post(IGDBAPI.__KEYWORDS_URL, headers = IGDBAPI.__HEADERS, data = query)

        if(r.status_code != 200):
            print("error http: {type}".format(type=r.status_code), r.text)
            return []

        return r.json()


