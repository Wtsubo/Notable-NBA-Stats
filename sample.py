#!/usr/bin/env python3
from lib import stats_1min
import os.path
import pytest
import traceback

if __name__ == '__main__':
    sourceFolder = os.path.dirname(os.path.abspath(__file__))
    rui   = stats_1min.players.find_players_by_full_name('Rui Hachimura')
    yuta  = stats_1min.players.find_players_by_full_name('Yuta Watanabe')
    tyuta = stats_1min.players.find_players_by_full_name('Yuta Tabuse')
    rui_obj = stats_1min.Nba_Player(rui[0]["id"])
    rui_obj.data_path = sourceFolder + "/data/{}".format(rui_obj.player_slug)
    rui_obj.add_career_team()
    rui_obj.add_current_team("2022-23")
    rui_obj.check_team_game_info()
    rui_obj.check_played_game_1min_info()
    yuta_obj = stats_1min.Nba_Player(yuta[0]["id"])
    yuta_obj.data_path = sourceFolder + "/data/{}".format(yuta_obj.player_slug)
    yuta_obj.add_career_team()
    yuta_obj.add_current_team("2022-23")
    yuta_obj.check_team_game_info()
    yuta_obj.check_played_game_1min_info()
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