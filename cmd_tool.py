#!/usr/bin/env python3
from lib import stats_1min
import os.path
import re
import argparse
from datetime import datetime, timedelta, timezone
import pytest
import traceback

if __name__ == '__main__':
    JST = timezone(timedelta(hours=+9), 'JST')
    parser = argparse.ArgumentParser(description="This tool can make your markdown file.")
    parser.add_argument("-o", "--operation", type=str, default="create_image",
                        choices=["get_data", "create_image"],
                        help="Select the operation for the creation.")
    parser.add_argument("-s", "--season", type=str, default="2023-24",
                        help="Put the NBA season. For example '2023-24'.")
    parser.add_argument("-d", "--directory", type=str, default="./",
                        help="Put the file save directory")
    parser.add_argument("name", type=str,
                        choices=["rui", "yuta","yuki"],
                        help="Put the player's name.")
    args = parser.parse_args()
    players_fullname = {"yuta": "Yuta Watanabe", "rui": "Rui Hachimura","yuki": "Yuki Kawamura" }
    current_season = "2023-24"
    player= stats_1min.players.find_players_by_full_name(players_fullname[args.name])
    player1min_obj = stats_1min.Nba_Player(player[0]["id"])
    player1min_obj.data_path = os.getcwd() + "/data/{}".format(player1min_obj.player_slug)
    if args.operation == "create_image":
        player1min_obj.add_career_team()
        if args.season == current_season:
            player1min_obj.add_current_team(current_season)
            filepath = os.getcwd() + "/" + current_season + ".md"
            time_stamp = "Last Update: {0}".format(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))
            with open(filepath, 'r') as f:
                doc = f.read()
            doc = re.sub(r'Last Update:.*', time_stamp, doc)
            with open(filepath, 'w') as f:
                f.write(doc)
        if args.season == "2022-23" and args.name == "rui":
            player1min_obj.add_current_team(current_season)
        player1min_obj.check_team_game_info()
        player1min_obj.get_heatmap(args.season, "MIN", "Blues", save_dir=args.directory)
        player1min_obj.get_heatmap(args.season, "PTS", "BuGn",  save_dir=args.directory)
    elif args.operation == "get_data":
        player1min_obj.add_current_team(current_season)
        player1min_obj.check_team_game_info()
        player1min_obj.check_played_game_1min_info()
    else:
        print("This feature is pending now.")