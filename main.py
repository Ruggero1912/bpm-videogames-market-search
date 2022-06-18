from SteamAPI import SteamAPI
from IGDBAPI import IGDBAPI

import pandas as pd

from Utils import Utils


def collect_games_genres(output_file="dumpone.csv", input_file="steam_app_ids.csv"):
    steam_ids = pd.read_csv(input_file)
    total_len = len(steam_ids)

    genres_of_all_games = []

    for index, row in steam_ids.iterrows():    
        print("\r[{num} / {tot}]Collecting info for the game '{game_name}' | app_id: {app_id}...\t\t\t".format(num=index, tot=total_len, game_name=row['app_name'], app_id=row['app_id']), end="")
        genres_list = SteamAPI.get_genres(app_id=row['app_id'])
        if genres_list is None:
            #optionally we could remove this row
            genres_list = []
        assert(type(genres_list) == list)
        # if len(genres_list) == 0: can handle this case
        genres_of_all_games.append(genres_list)

    steam_ids['genres'] = genres_of_all_games
    steam_ids.to_csv(output_file, index=False)


def load_all_IGDB_genres_and_store_in_csv(output_file="IGDB_genres.csv"):
    print("Going to load all the genres available on IGDBAPI")
    all_genres_list = IGDBAPI.get_genres()
    print(f"Loaded {len(all_genres_list)} genres from IGDBAPI", f"going to store them in {output_file}")
    genres_dataframe = pd.DataFrame(all_genres_list)
    genres_dataframe.to_csv(output_file, index=False)
    return genres_dataframe


def load_tags_dict(games_genre_id_IGDB = 4, keyword_ids_file="keyword_ids.csv", keyword_infos_file="keyword_infos.csv"):    
    """
    1. get most pop games (sorted by total reviews counter)
    2. salvo i games in una list
    - e salvo le keyword ids in una list prevenendo duplicati
    (optional): salvo le row trovate in un dataframe
    3. chiamo get keywords infos
    4. salvo name e id delle keywords (o volendo anche tutte le info delle keyword) in un dataframe
    5. esporto i dataframe in csv
    nel dataframe risultante ho anche informazione su quante volte è stata incontrata la keyword
    """
    print(f"Going to load the most reviewed games from IGDB whose IGDB genre_id is {games_genre_id_IGDB}")
    pop_games_list = IGDBAPI.get_most_popular_games(games_genre_id_IGDB)
    keyword_ids_dict = {}
    for game in pop_games_list:
        assert isinstance(game, dict)
        if "keywords" in game.keys():
            keyword_ids_list_local = list(game["keywords"])
            for keyword_id in keyword_ids_list_local:
                if keyword_id in keyword_ids_dict.keys():
                    keyword_ids_dict[keyword_id] += 1
                else:
                    keyword_ids_dict[keyword_id] = 1
    #here i have a keywords dict (keyword_id : keyword_how_many_occurency)
    print(f"gathered the keyword ids from IGDB | found {len(keyword_ids_dict.keys())} different keywords for the most reviewed games of genre {games_genre_id_IGDB}")
    #in order to prevent error and store this partial result, here i save the dict to file
    keyword_ids_counter_df = pd.DataFrame.from_dict(keyword_ids_dict, orient='index')
    keyword_ids_counter_df.to_csv(keyword_ids_file, index=False)
    print(f"stored the dict of keyword ids to file '{keyword_ids_file}'")

    print("Going to request full infos for each keyword id")

    #here I have to use the method IGDBAPI.get_keywords_details([list of keyword ids]) but it is better to split the request in to smaller lists to prevent size exceed

    full_keyword_infos = []

    SPLITTED_ARRAY_SIZE = (len(keyword_ids_dict)//500)+1

    for some_keyword_ids in Utils.split_list(list( keyword_ids_dict.keys() ), SPLITTED_ARRAY_SIZE ):
        full_keyword_infos += IGDBAPI.get_keywords_details(some_keyword_ids)
        print(f"\rObtained full infos of {len(full_keyword_infos)} out of {len(keyword_ids_dict)} keyword found")

    print("Requested full keyword infos for all the keywords!")

    keyword_infos_dataframe = pd.DataFrame(full_keyword_infos)

    keyword_infos_dataframe['counter'] = keyword_infos_dataframe["id"].map(keyword_ids_dict)
    print("Going to store the full infos of all keywords to file...")

    keyword_infos_dataframe.to_csv(keyword_infos_file, index=False)

def export_dictionary(input_file="keyword_infos.csv", output_file="tags_dict.csv"):
    """
    receives as input the tags dict with all the attributes, 
    stores a new csv with only the tag wich counter > THRESHOLD and stores only the slug of the tag word (lowered word, unique)
    """
    THRESHOLD = 20
    tags_all_infos = pd.read_csv(input_file)
    tags_df = tags_all_infos[["slug", "counter"]]
    tags_df = tags_df[tags_df["counter"] >= THRESHOLD].sort_values(by=['counter'], ascending=False)
    tags_df["slug"] = tags_df["slug"].str.replace("-", " ")
    tags_df.to_csv(output_file, index=False)
