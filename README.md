# Notable-NBA-Stats
日本人が注目すべきNBAスタッツ

## 概要
- NBAで活躍する日本人の1min毎のPlaytimeとStatsを取得するツール。

## 活躍状況
- [シーズン2024-25](2024-25.md)
- [シーズン2023-24](2023-24.md)
- [シーズン2022-23](2022-23.md)
- [シーズン2021-22](2021-22.md)
- [シーズン2020-21](2020-21.md)
- [シーズン2019-20](2019-20.md)
- [シーズン2018-19](2018-19.md)

## 操作方法
- 以下を参考に。
  ```
  $ ./cmd_tool.py -h
  usage: cmd_tool.py [-h] [-o {get_data,create_image}] [-s SEASON] [-d DIRECTORY] {rui,yuta}
  
  This tool can make your markdown file.
  
  positional arguments:
    {rui,yuta}            Put the player's name.
  
  options:
    -h, --help            show this help message and exit
    -o {get_data,create_image}, --operation {get_data,create_image}
                          Select the operation for the creation.
    -s SEASON, --season SEASON
                          Put the NBA season. For example '2023-24'.
    -d DIRECTORY, --directory DIRECTORY
                          Put the file save directory
  $
  ```
