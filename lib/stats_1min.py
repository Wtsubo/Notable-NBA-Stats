#!/usr/bin/env python3
from nba_api.stats.static    import players
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import boxscoresummaryv2
from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import teamgamelog
import pandas            as pd
import numpy             as np
import matplotlib.pyplot as plt
import seaborn           as sns
from sys import argv
from datetime import datetime, timedelta, timezone
import argparse
import json
import os.path
import time
import pytest
import traceback
from pprint import pprint
#pytest.set_trace()

class Nba_Player():
    def __init__(self, id):
        self.info = commonplayerinfo.CommonPlayerInfo(player_id=id).get_data_frames()
        self.career_info = playercareerstats.PlayerCareerStats(id)
        self.season_totals_regular_season = self.career_info.season_totals_regular_season.get_data_frame()
        self.season_totals_post_season = self.career_info.season_totals_post_season.get_data_frame()
        self.player_slug = self.info[0].iloc[0].PLAYER_SLUG
        self.season = {}
        self.sourceFolder = os.path.dirname(os.path.abspath(__file__))
        self.data_path = self.sourceFolder + "/data/{}".format(self.player_slug)
        os.makedirs(self.data_path, exist_ok=True)
        self.game_1min_trad_stats = {}

    def add_season(self, season_name):
        if not season_name in self.season.keys():
            self.season[season_name] = {}
            self.season[season_name]["team_id"] = []
            self.season[season_name]["game_info"] = []
            self.season[season_name]["game_pre"] = []
            self.season[season_name]["game_post"] = []
            self.game_1min_trad_stats[season_name] = "Expected DataFrame object after check data."

    def add_current_team(self, season_name):
        if not season_name in self.season.keys():
            self.add_season(season_name)
            self.season[season_name]["team_id"].append(self.info[0].TEAM_ID)

    def add_career_team(self):
        for idx, row in self.season_totals_regular_season.iterrows():
            if not row.SEASON_ID in self.season.keys():
                self.add_season(row.SEASON_ID)
                self.season[row.SEASON_ID]["team_id"].append(row.TEAM_ID)

    def check_team_game_info(self):
        for season, value in self.season.items():
            for id in value["team_id"]:
                self.season[season]["game_info"].append(
                    teamgamelog.TeamGameLog(id, season=season).get_data_frames()[0])
            self.season[season]["game_post"] = teamgamelog.TeamGameLog(value["team_id"][-1], season=season, season_type_all_star="Playoffs").get_data_frames()[0]
            self.season[season]["game_pre"]  = teamgamelog.TeamGameLog(value["team_id"][0], season=season, season_type_all_star="Pre Season").get_data_frames()[0]
        self.add_columns_team_game_info()

    def add_columns_team_game_info(self):
        for season, value in self.season.items():
            for game in value["game_info"]:
                game["GAME_DATETIME"] = pd.to_datetime(game['GAME_DATE'],format='%b %d, %Y')
                game.sort_values("GAME_DATETIME", inplace=True)
                game.reset_index(inplace=True)
            for game in value["game_info"]:
                for idx,row in game.iterrows():
                    game.loc[idx, 'Game_No'] = "Game{:0=2}".format(int(idx)+1)
            value["game_post"]["GAME_DATETIME"] = pd.to_datetime(value["game_post"]['GAME_DATE'],format='%b %d, %Y')
            value["game_post"].sort_values("GAME_DATETIME", inplace=True)
            value["game_post"].reset_index(inplace=True)
            for idx,row in value["game_post"].iterrows():
                value["game_post"].loc[idx, 'Game_No'] = "Playoff-{:0=2}".format(int(idx)+1)
            value["game_pre"]["GAME_DATETIME"] = pd.to_datetime(value["game_pre"]['GAME_DATE'],format='%b %d, %Y')
            value["game_pre"].sort_values("GAME_DATETIME", inplace=True)
            value["game_pre"].reset_index(inplace=True)
            for idx,row in value["game_pre"].iterrows():
                value["game_pre"].loc[idx, 'Game_No'] = "Pre-{:0=2}".format(int(idx)+1)

    def check_played_game_1min_info(self):
        for season, value in self.season.items():
            for game_info in value["game_info"]:
                if not isinstance(self.game_1min_trad_stats[season], pd.core.frame.DataFrame):
                    box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_info.Game_ID[0])
                    self.game_1min_trad_stats[season] = pd.DataFrame(columns=box.get_data_frames()[0].columns)
                    self.game_1min_trad_stats[season]["Timestamp_Minutes"] = ""
                    self.game_1min_trad_stats[season]["Game_Label"] = ""
                for game_id in game_info.Game_ID:
                    pk_file_name = self.data_path + "/" + "{}_{}_Game_{}.pkl".format(self.player_slug, season, game_id)
                    res = game_info[game_info["Game_ID"] == game_id]
                    res.reset_index(inplace=True)
                    if os.path.isfile(pk_file_name):
                        played_stats = pd.read_pickle(pk_file_name)
                        played_stats['Game_Label'] = "{:<11}{:<14}{:<14}".format(res.loc[0,"Game_No"], res.loc[0,"MATCHUP"], res.loc[0,"GAME_DATE"])
                        #self.game_1min_trad_stats[season] = self.game_1min_trad_stats[season].append(pd.read_pickle(pk_file_name))
                        self.game_1min_trad_stats[season] = self.game_1min_trad_stats[season].append(played_stats)
                        print("Got the data from the file '{}' data.".format(pk_file_name))
                    else:
                        time.sleep(3)
                        game = Nba_Game(game_id=game_id)
                        game.check_trad_1min()
                        played_stats = game.trad_1min_player(self.info[0].iloc[0]["PERSON_ID"]).copy()
                        played_stats['Game_Label'] = "{:<11}{:<14}{:<14}".format(res.loc[0,"Game_No"], res.loc[0,"MATCHUP"], res.loc[0,"GAME_DATE"])
                        self.game_1min_trad_stats[season] = self.game_1min_trad_stats[season].append(played_stats)
                        pd.to_pickle(played_stats, pk_file_name)
                        print("Got the data and put the file '{}'.".format(pk_file_name))
                        time.sleep(3)
            for game_id in value["game_post"].Game_ID:
                pk_file_name = self.data_path + "/" + "{}_{}_Game_{}.pkl".format(self.player_slug, season, game_id)
                res = value["game_post"][value["game_post"]["Game_ID"] == game_id]
                res.reset_index(inplace=True)
                if os.path.isfile(pk_file_name):
                    played_stats = pd.read_pickle(pk_file_name)
                    played_stats['Game_Label'] = "{:<11}{:<14}{:<14}".format(res.loc[0,"Game_No"], res.loc[0,"MATCHUP"], res.loc[0,"GAME_DATE"])
                    #self.game_1min_trad_stats[season] = self.game_1min_trad_stats[season].append(pd.read_pickle(pk_file_name))
                    self.game_1min_trad_stats[season] = self.game_1min_trad_stats[season].append(played_stats)
                    print("Got the data from the file '{}' data.".format(pk_file_name))
                else:
                    time.sleep(3)
                    game = Nba_Game(game_id=game_id)
                    game.check_trad_1min()
                    played_stats = game.trad_1min_player(self.info[0].iloc[0]["PERSON_ID"]).copy()
                    played_stats['Game_Label'] = "{:<11}{:<14}{:<14}".format(res.loc[0,"Game_No"], res.loc[0,"MATCHUP"], res.loc[0,"GAME_DATE"])
                    self.game_1min_trad_stats[season] = self.game_1min_trad_stats[season].append(played_stats)
                    pd.to_pickle(played_stats, pk_file_name)
                    print("Got the data and put the file '{}'.".format(pk_file_name))
                    time.sleep(3)
            """
            """

            pd.to_pickle(self.game_1min_trad_stats[season], self.data_path + "/" + "{}_{}_Games_all.pkl".format(self.player_slug, season))

    def get_played_game_1min_info(self, season):
        player_season_data = pd.read_pickle(self.data_path + "/" + "{}_{}_Games_all.pkl".format(self.player_slug, season))
        for idx, row in self.season[season]["game_info"][0].iterrows():
            if row["Game_ID"] in player_season_data.values:
                True
            else:
                game_label = "{:<11}{:<14}{:<14}".format(row["Game_No"], row["MATCHUP"], row["GAME_DATE"])
                for num in range(0,48):
                    game_not_play = pd.DataFrame([row["Game_ID"],0,0,num+1,game_label],index=['GAME_ID','MIN','PTS',"Timestamp_Minutes","Game_Label"]).T
                    player_season_data = pd.concat([player_season_data, game_not_play], ignore_index=True)

        return player_season_data


    def get_heatmap(self, season, value, color):
         data = self.get_played_game_1min_info(season)
         pivot = pd.pivot_table(
             data= data,
             values= value,
             columns='Timestamp_Minutes',
             index='Game_Label',
             aggfunc= np.mean
         )
         len_y = len(set(data.GAME_ID))*20//70
         plt.figure(figsize=(14, len_y))
         plt.style.use('seaborn-white')
         plt.rcParams['font.family'] = 'monospace'
         ax = plt.axes()
         ax.set_title('{} {} "{}"'.format(self.player_slug, season, value))
         return sns.heatmap(
             pivot.sort_values(by="Game_Label", ascending=False),
             annot=False, fmt='g', cmap=color,
             xticklabels=1, yticklabels=1,
             square=True, vmin=0, ax=ax,
         )


class Nba_Game():
    def __init__(self, game_id):
        self.game_id   = game_id
        self.trad      = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id)
        self.trad_1min = pd.DataFrame(columns=self.trad.get_data_frames()[0].columns)
        self.trad_1min["Timestamp_Minutes"] = ""

    def check_trad_1min(self):
        try:
            for i in range(0,48):
                data = boxscoretraditionalv2.BoxScoreTraditionalV2(
                           self.game_id,
                           range_type=2,
                           start_range =600*(i),
                           end_range   =600*(i+1),
                           timeout=50,
                       ).get_data_frames()[0].assign(Timestamp_Minutes=i+1)
                self.trad_1min = self.trad_1min.append(data, ignore_index=True)
                time.sleep(5)
            f = lambda min: int(min.split(":")[0])*60 + int(min.split(":")[1])*1 
            self.trad_1min["MIN"] = self.trad_1min["MIN"].apply(f)
            #self.trad_1min["MIN"] = self.trad_1min["MIN"].apply(self.min_to_sec)
        except Exception as e:
            pprint(e)
            pprint(e.args)
            False

        finally:
            True

    def min_to_sec(min):
        sec = int(min.split(":")[0])*60
        sec = sec + int(min.split(":")[1])
        return sec

    def trad_1min_player(self, player_id):
        return self.trad_1min.loc[self.trad_1min['PLAYER_ID'] == player_id]

"""
class Nba_Team():
    def __init__(self, team_id):
        self.team_id = team_id

    def get_season_game_log(self, season):
        try:
            return teamgamelog.TeamGameLog(self.team_id, season=season).get_data_frames()[0]

        except Exception as e:
            pprint(e)
            pprint(e.args)
            False

        finally:
            True
"""

if __name__ == '__main__':
    """
    Yuta
    """
