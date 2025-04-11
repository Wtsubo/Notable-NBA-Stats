#!/usr/bin/env python3
from lib import stats_1min
import os.path
import re
from datetime import datetime, timedelta, timezone
import pytest
import traceback

if __name__ == '__main__':
    JST = timezone(timedelta(hours=+9), 'JST')
    sourceFolder = os.path.dirname(os.path.abspath(__file__))
    tyuta = stats_1min.players.find_players_by_full_name('Yuta Tabuse')
    current_season = "2024-25"
    players = []
    players.append(stats_1min.players.find_players_by_full_name('Rui Hachimura'))
    #players.append(stats_1min.players.find_players_by_full_name('Yuta Watanabe'))
    players.append(stats_1min.players.find_players_by_full_name('Yuki Kawamura'))
    for player in players:
        player_obj = stats_1min.Nba_Player(player[0]["id"])
        player_obj.data_path = sourceFolder + "/data/{}".format(player_obj.player_slug)
        #player_obj.add_career_team()
        player_obj.add_current_team(current_season)
        player_obj.check_team_game_info()
        player_obj.check_played_game_1min_info()
        #
        player_obj.add_career_team()
        filepath = sourceFolder + "/" + current_season + ".md"
        time_stamp = "Last Update: {0}".format(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))
        with open(filepath, 'r') as f:
            doc = f.read()
        doc = re.sub(r'Last Update:.*', time_stamp, doc)
        with open(filepath, 'w') as f:
            f.write(doc)
        player_obj.get_heatmap(current_season, "MIN", "Blues", save_dir=sourceFolder + "/images")
        player_obj.get_heatmap(current_season, "PTS", "BuGn",  save_dir=sourceFolder + "/images")
    """Yuta
    try:
        for idx, row in yuta_obj.season["2020-21"]["game_info"][0].iterrows():
            pk_file_name = yuta_obj.data_path + "/" + "yuta_2020_Game_{0}.pkl".format(row["Game_ID"])
            new_pk_file_name = yuta_obj.data_path + "/" + "{}_{}_Game_{}.pkl".format(yuta_obj.player_slug, "2020-21", row["Game_ID"])
            if os.path.isfile(pk_file_name):
                old_yuta = pd.read_pickle(pk_file_name)
                old_yuta['Game_Label'] = "{:<8}{:<14}{:<14}".format(row["Game_No"], row["MATCHUP"], row["GAME_DATE"])
                f = lambda min: int(min.split(":")[0])*60 + int(min.split(":")[1])*1 
                old_yuta["MIN"] = old_yuta["MIN"].apply(f)
                old_yuta.rename(columns={"TIMESTAMP": "Timestamp_Minutes"}, inplace=True)
                print("Create the '{}' from the '{}'.".format(new_pk_file_name, pk_file_name))
                pd.to_pickle(old_yuta, new_pk_file_name)
            else:
                print("No file '{}'.".format(pk_file_name))

    except Exception as e:
        pprint(e)
        pprint(e.args)
        False

    finally:
        #pytest.set_trace()
        True
    """