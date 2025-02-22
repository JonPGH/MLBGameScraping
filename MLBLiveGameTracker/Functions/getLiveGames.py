import requests

def getLiveGames(date_string):
    games = []
    #sportIds = [1,11, 12, 13, 14, 15, 16, 17]
    sportIds = [1]
    sport_id_mappings = {1: 'MLB', 11: 'AAA', 12: 'AA', 13: 'A+', 14: 'A', 16: 'ROK', 17: 'WIN'}

    for sportId in sportIds:
        url = "https://statsapi.mlb.com/api/v1/schedule/?sportId={}&date={}".format(sportId,date_string)
        schedule = requests.get(url).json()

        for date in schedule["dates"]:
            for game_data in date["games"]:
                # Skip games that are not finished ("F")
                # If a game was delayed, it will show up again on a later calendar date
                #if game_data["status"]["codedGameState"] == "F":
                game = {}
                game["date"] = date_string
                game["game_id"] = game_data["gamePk"]
                game["game_type"] = game_data["gameType"]
                game["venue_id"] = game_data["venue"]["id"]
                game["venue_name"] = game_data["venue"]["name"]
                game["away_team"] = game_data["teams"]["away"]["team"]["name"]
                game["home_team"] = game_data["teams"]["home"]["team"]["name"]
                game["league_id"] = sportId
                game["league_level"] = sport_id_mappings.get(sportId)
                game["game_status"] = game_data["status"]["codedGameState"]
                game["game_status_full"] = game_data["status"]["abstractGameState"]
                game["game_start_time"] = game_data["gameDate"]
                games.append(game)
    return games