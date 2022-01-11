from PIL import Image, ImageFont, ImageDraw
import threading
from datetime import datetime
import calendar
import requests
from steam_funcs import user_app_stat, user_rec_played_stat
from faceit_get_funcs import player_details, region_stats, player_history, match_stats


class ImageCollector:
    def __init__(self, request_json, stat_json, prev_nick1, prev_elo1, prev_nick2, prev_elo2):
        self._fonts = self.getFonts(font_folder='Outfit', font_file='Outfit-Bold.ttf',
                                    font_file_mainscore='Outfit-ExtraBold.ttf')
        self._elo_change_team1, self._elo_change_team2 = '', ''
        self.request_json = request_json
        self.stat_json = stat_json
        self.prev_nick1 = prev_nick1
        self.prev_nick2 = prev_nick2
        self.prev_elo1 = prev_elo1
        self.prev_elo2 = prev_elo2
        self.stat_color = (255, 255, 255, 255)
        self.image_map = Image.new(mode='RGBA', size=(960, 540))
        self.draw_image_map = ImageDraw.Draw(self.image_map)
        self.image_dark_avatar_bot = Image.open('templates/background_features/for_avatar_bot.png')
        self.image_dark_avatar_top = Image.open('templates/background_features/for_avatar_top.png')
        self.image_dark_middle = Image.open('templates/background_features/dark-middle2.png')

    def collect_image(self):
        image_list = []

        for idx_match, match in enumerate(self.stat_json['rounds']):
            # elo_change_team1, elo_change_team2 = self.calculateEloChange(match, self.prev_nick1, self.prev_nick2,
            #                                                              self.prev_elo1, self.prev_elo2)
            self.drawMapImage(match)
            for idx_team, team in enumerate(match['teams']):
                for idx_player, player in enumerate(team['players']):
                    self.drawPlayerOnImage(player, idx_team, idx_player)
            image_list.append(self.image_map)
        return image_list

    def boolOvertimeCheck(self, match):
        if 'Overtime score' in match['teams'][0]['team_stats'].keys():
            if match['teams'][0]['team_stats']['Overtime score'] == '0' and \
                    match['teams'][1]['team_stats']['Overtime score'] == '0':
                isOvertimeinGame = False
            else:
                isOvertimeinGame = True
        else:
            isOvertimeinGame = False
        return isOvertimeinGame

    def calculateEloChange(self, player, player_elo):
        elo_diff = ''
        nicknames = (self.prev_nick1 + '\n' + self.prev_nick2).split('\n')
        prevelo = (self.prev_elo1 + '\n' + self.prev_elo2).split('\n')
        for idx, nick in enumerate(nicknames):
            if nick == player['nickname']:
                if int(prevelo[idx]) > int(player_elo):
                    return '(+' + str(int(prevelo[idx]) - int(player_elo)) + ')'
                else:
                    return '(' + str(int(prevelo[idx]) - int(player_elo)) + ')'
        return elo_diff

    def drawMapImage(self, match):
        self.image_map = Image.open(f'templates/maps/{match["round_stats"]["Map"]}.jpg')
        self.image_map = self.image_map.resize((960, 540))
        self.draw_image_map = ImageDraw.Draw(self.image_map)
        if match['teams'][0]['team_stats']['Team Win'] == '1':
            image_topcolor = Image.open('templates/background_features/Win-topleft.png')
            image_botcolor = Image.open('templates/background_features/Lose-botleft.png')
        else:
            image_topcolor = Image.open('templates/background_features/Lose-topleft.png')
            image_botcolor = Image.open('templates/background_features/Win-botleft.png')
        self.image_map.paste(image_topcolor, (0, 0), image_topcolor)
        self.image_map.paste(image_botcolor, (0, 0), image_botcolor)
        self.image_map.paste(self.image_dark_middle, (0, 0), self.image_dark_middle)

        w, h = self.draw_image_map.textsize(match["teams"][0]["team_stats"]["Final Score"],
                                            font=self._fonts['mainscore'])
        self.draw_image_map.text(((146 - w) / 2, 65), match["teams"][0]["team_stats"]["Final Score"],
                                 font=self._fonts['mainscore'])
        w, h = self.draw_image_map.textsize(match["teams"][1]["team_stats"]["Final Score"],
                                            font=self._fonts['mainscore'])
        self.draw_image_map.text(((146 - w) / 2, 415), match["teams"][1]["team_stats"]["Final Score"],
                                 font=self._fonts['mainscore'])

        isOvertimeinMatch = self.boolOvertimeCheck(match)
        for idx_team, team in enumerate(match['teams']):
            if isOvertimeinMatch:
                halftimes = f"{team['team_stats']['First Half Score']}" \
                            f"—{team['team_stats']['Second Half Score']}" \
                            f"—{team['team_stats']['Overtime score']}"
            else:
                halftimes = f"{team['team_stats']['First Half Score']}" \
                            f"—{team['team_stats']['Second Half Score']}"
            w, h = self.draw_image_map.textsize(halftimes, font=self._fonts['halftime'])
            self.draw_image_map.text(((146 - w) / 2, 235 + 42 * idx_team), halftimes, font=self._fonts['halftime'])

    def getFonts(self, font_folder, font_file, font_file_mainscore):
        fonts = {'mainscore': ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file_mainscore}', 50),
                 'avatar': ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 18),
                 'player_score': ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 32),
                 'player_stats': ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22),
                 'halftime': ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22)
                 }
        return fonts

    def drawPlayerOnImage(self, player, idx_team, idx_player):
        self.drawAvatarOnImage(player, idx_team, idx_player)
        self.drawPlayerStatsOnImage(player, idx_team, idx_player)

    def drawAvatarOnImage(self, player, idx_team, idx_player):
        player_elo = str(player_details(player['nickname'])['games']['csgo']['faceit_elo'])
        elo_diff = self.calculateEloChange(player, player_elo)
        for idx_req_player, req_player in enumerate(self.request_json['payload']['teams'][idx_team]['roster']):
            if player['nickname'] == req_player['nickname']:
                if req_player['avatar'] != '':
                    avatar_req = requests.get(req_player['avatar'], stream=True)
                    image_avatar = Image.open(avatar_req.raw)
                    image_avatar = image_avatar.resize((130, 130))
                else:
                    image_avatar = Image.open('templates/question-mark-icon.jpg')
                    image_avatar = image_avatar.resize((130, 130))
                draw_image_avatar = ImageDraw.Draw(image_avatar)
                faceitlvl = req_player['game_skill_level']

                if idx_team == 0:
                    image_avatar.paste(self.image_dark_avatar_bot, (0, 0), self.image_dark_avatar_bot)
                    image_avatar.paste(self.image_dark_avatar_top, (0, 0), self.image_dark_avatar_top)
                    image_avatar.paste(
                        Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                        (0, 0),
                        Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                    w, h = self.draw_image_map.textsize(elo_diff, font=self._fonts['avatar'])
                    draw_image_avatar.text((127 - w, 0), elo_diff, font=self._fonts['avatar'])
                    w, h = self.draw_image_map.textsize(player_elo, font=self._fonts['avatar'])
                    draw_image_avatar.text((26, 0), player_elo, font=self._fonts['avatar'])
                else:
                    image_avatar.paste(self.image_dark_avatar_top, (0, 0), self.image_dark_avatar_top)
                    image_avatar.paste(self.image_dark_avatar_bot, (0, 0), self.image_dark_avatar_bot)
                    image_avatar.paste(
                        Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                        (0, 106),
                        Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                    w, h = self.draw_image_map.textsize(elo_diff, font=self._fonts['avatar'])
                    draw_image_avatar.text((127 - w, 107), elo_diff, font=self._fonts['avatar'])
                    w, h = self.draw_image_map.textsize(player_elo, font=self._fonts['avatar'])
                    draw_image_avatar.text((26, 107), player_elo, font=self._fonts['avatar'])

                w, h = self.draw_image_map.textsize(req_player['nickname'], font=self._fonts['avatar'])
                if w > 130:
                    draw_image_avatar.text((0, 107 - idx_team * 107),
                                           req_player['nickname'],
                                           font=self._fonts['avatar'])
                else:
                    draw_image_avatar.text(((130 - w) / 2, 107 - idx_team * 107),
                                           req_player['nickname'],
                                           font=self._fonts['avatar'])

                self.image_map.paste(image_avatar, (146 + idx_player * 162, 20 + 370 * idx_team))

    def drawPlayerStatsOnImage(self, player, idx_team, idx_player):
        if float(player["player_stats"]["K/D Ratio"]) >= 1.3:
            self.stat_color = (0, 190, 0, 255)
        elif float(player["player_stats"]["K/D Ratio"]) < 0.6:
            self.stat_color = (170, 0, 0, 255)
        elif 0.8 > float(player["player_stats"]["K/D Ratio"]) >= 0.6:
            self.stat_color = (255, 165, 0, 255)
        else:
            self.stat_color = (255, 255, 255, 255)

        kad = f'{player["player_stats"]["Kills"]}' \
              f'/{player["player_stats"]["Assists"]}' \
              f'/{player["player_stats"]["Deaths"]}'
        w, h = self.draw_image_map.textsize(kad, font=self._fonts['player_score'])
        self.draw_image_map.text((130 + (162 - w) / 2 + idx_player * 162, 155 + 195 * idx_team), kad,
                                 font=self._fonts['player_score'])
        mvp = f'MVP: {player["player_stats"]["MVPs"]}'
        self.draw_image_map.text((156 + idx_player * 162, 240 + 36 * idx_team), mvp, font=self._fonts['player_stats'])
        kr = f'K/R: {player["player_stats"]["K/R Ratio"]}'
        self.draw_image_map.text((156 + idx_player * 162, 220 + 76 * idx_team), kr, font=self._fonts['player_stats'])
        kd = f'K/D: {player["player_stats"]["K/D Ratio"]}'
        self.draw_image_map.text((156 + idx_player * 162, 200 + 116 * idx_team), kd, font=self._fonts['player_stats'],
                                 fill=self.stat_color)


class ImageCollectorStatLast:
    def __init__(self, nickname):
        self.nickname = nickname

    def collect_image(self):
        player_stat = self.collect_stat(self.nickname)
        if player_stat is None:
            return None
        else:
            image = self.drawImage(player_stat)
            return image

    def collect_stat(self, nickname):
        lrc = []
        pd = player_details(nickname)
        player_id = pd['player_id']
        if pd is not None:
            history = player_history(pd['player_id'])
            region_place = region_stats(pd['player_id'], pd['games']['csgo']['region'])['items'][0]['position']
            country_place = region_stats(pd['player_id'], pd['games']['csgo']['region'], pd['country'])['items'][0]['position']
            if history is not None:
                while len(lrc) < 11:
                    for match_h in history['items']:
                        ms = match_stats(match_h['match_id'])
                        if ms is not None:
                            for map_s in ms['rounds'][::-1]:
                                for team in map_s['teams']:
                                    for player in team['players']:
                                        if player_id == player['player_id']:
                                            rc = {'nickname': nickname,
                                                  'steam_id': pd['games']['csgo']['game_player_id'],
                                                  'avatar': pd['avatar'],
                                                  'background': pd['cover_image'],
                                                  'country': pd['country'],
                                                  'country_place': country_place,
                                                  'region_place': region_place,
                                                  'player_id': pd['player_id'],
                                                  'region': pd['games']['csgo']['region'],
                                                  'skill_level': pd['games']['csgo']['skill_level'],
                                                  'faceit_elo': pd['games']['csgo']['faceit_elo'],
                                                  'result': player['player_stats']['Result'],
                                                  'kills': player['player_stats']['Kills'],
                                                  'assists': player['player_stats']['Assists'],
                                                  'deaths': player['player_stats']['Deaths'],
                                                  'kdratio': player['player_stats']['K/D Ratio'],
                                                  'krratio': player['player_stats']['K/R Ratio'],
                                                  'mvps': player['player_stats']['MVPs'],
                                                  'headshots%': player['player_stats']['Headshots %'],
                                                  '4k': player['player_stats']['Quadro Kills'],
                                                  '5k': player['player_stats']['Penta Kills'],
                                                  'mapscore': map_s['round_stats']['Score'],
                                                  'mapname': map_s['round_stats']['Map'],
                                                  'started_at': match_h['started_at']}
                                            lrc.append(rc)
                                            break
        else:
            return None
        return lrc

    def drawImage(self, player_stat):
        font = ImageFont.truetype(f'templates/fonts/Outfit/Outfit-Bold.ttf', 26)
        font_name = ImageFont.truetype(f'templates/fonts/Outfit/Outfit-Bold.ttf', 36)
        if player_stat[0]['background'] != '':
            bg_req = requests.get(player_stat[0]['background'], stream=True)
            image_background = Image.open(bg_req.raw)
        else:
            image_background = Image.open(f'templates/background_features/dark-right-side-for-stat.png')

        lose_bg = Image.open(f'templates/background_features/right-side-lose.png')
        win_bg = Image.open(f'templates/background_features/right-side-win.png')

        width, height = image_background.size
        if height != 540:
            aspect_ratio = 540 / height
            image_background = image_background.resize((int(width * aspect_ratio), 540))
        width, height = image_background.size
        if width >= 960:
            left = int((width - 960) / 2)
            top = 0
            right = int((width - 960) / 2 + 960)
            bottom = height
            image_background = image_background.crop((left, top, right, bottom))
            image_background.resize((960, 540))
        dark_right = Image.open(f'templates/background_features/dark-right-side-for-stat.png')
        image_background.paste(dark_right, (0, 0), dark_right)
        if player_stat[0]['avatar'] != '':
            avatar_req = requests.get(player_stat[0]['avatar'], stream=True)
            image_avatar = Image.open(avatar_req.raw)
            image_avatar = image_avatar.resize((130, 130))
        else:
            image_avatar = Image.open(f'templates/question-mark-icon.jpg')
            image_avatar = image_avatar.resize((130, 130))

        image_background.paste(image_avatar, (10, 10))
        draw_image_bg = ImageDraw.Draw(image_background)
        draw_image_bg.text((160, 20), player_stat[0]['nickname'], font=font_name)

        app_stat = user_app_stat(player_stat[0]["steam_id"])
        rec_pl_stat = user_rec_played_stat(player_stat[0]['steam_id'])

        playtime_2weeks = 'Last 2 weeks: Unknown'
        playtime_forever = 'Summary in CSGO: Unknown'
        percentage_played = 'Activity: Unknown'
        csgotime_played_hrs = 'Played in CSGO: Unknown'
        if 'response' in rec_pl_stat.keys() and 'games' in rec_pl_stat['response'].keys():
            for app in rec_pl_stat['response']['games']:
                if app['appid'] == 730:
                    playtime_2weeks = f'Last 2 weeks: {int(app["playtime_2weeks"] / 60)} hrs'
                    playtime_forever = f'Summary in CSGO: {int(app["playtime_forever"] / 60)} hrs'
                    if app_stat is not None:
                        csgotime_played_hrs = f'Played in CSGO: {int(app_stat["playerstats"]["stats"][2]["value"] / 60 / 60)} hrs'
                        percentage_played = f'Activity: {format((app_stat["playerstats"]["stats"][2]["value"] / 60 / 60) / (app["playtime_forever"] / 60) * 100, ".1f")}%'
                    else:
                        csgotime_played_hrs = f'Played in CSGO: Unknown'
                        percentage_played = f'Activity: Unknown'

        draw_image_bg.text((10, 150), playtime_2weeks, font=font)
        draw_image_bg.text((10, 180), csgotime_played_hrs, font=font)
        draw_image_bg.text((10, 210), playtime_forever, font=font)
        draw_image_bg.text((10, 240), percentage_played, font=font)

        faceitlvl = player_stat[0]['skill_level']
        image_lvl = Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA")
        image_lvl = image_lvl.resize((24, 24))
        image_background.paste(image_lvl, (155, 74), image_lvl)

        draw_image_bg.text((184, 70), str(player_stat[0]['faceit_elo']), font=font)

        mean_k, mean_a, mean_d, mean_kd, mean_kr, mean_hs, total_4k, total_5k = 0, 0, 0, 0, 0, 0, 0, 0
        for i in range(10):
            mean_k += int(player_stat[i]['kills'])
            mean_a += int(player_stat[i]['assists'])
            mean_d += int(player_stat[i]['deaths'])
            mean_kd += float(player_stat[i]['kdratio'])
            mean_kr += float(player_stat[i]['krratio'])
            mean_hs += float(player_stat[i]['headshots%'])
            total_4k += int(player_stat[i]['4k'])
            total_5k += int(player_stat[i]['5k'])

            if float(player_stat[i]["kdratio"]) >= 1.3:
                stat_color = (0, 190, 0, 255)
            elif float(player_stat[i]["kdratio"]) < 0.6:
                stat_color = (170, 0, 0, 255)
            elif 0.8 > float(player_stat[i]["kdratio"]) >= 0.6:
                stat_color = (255, 165, 0, 255)
            else:
                stat_color = (255, 255, 255, 255)

            if player_stat[i]['result'] == '1':
                image_background.paste(win_bg, (775, 50 * i + 24), win_bg)
            else:
                image_background.paste(lose_bg, (775, 50 * i + 24), lose_bg)
            draw_image_bg.text((870, 50 * i + 30), player_stat[i]['mapscore'], font=font)
            current_map = Image.open(f'templates/maps/{player_stat[i]["mapname"]}.jpg')
            current_map = current_map.resize((90, 50))
            image_background.paste(current_map, (770, 50 * i + 24))
            kad = f'{player_stat[i]["kills"]}/{player_stat[i]["assists"]}/{player_stat[i]["deaths"]}'
            draw_image_bg.text((665, 50 * i + 30), kad, font=font, fill=stat_color)
            dd = datetime.utcfromtimestamp(player_stat[i]['started_at']).strftime('%m/%d')
            cc = calendar.month_name[int(dd.split('/')[0])][:3]
            draw_image_bg.text((570, 50 * i + 30), dd.split('/')[1] + " " + cc, font=font)

        mean_k /= 10
        mean_a /= 10
        mean_d /= 10
        mean_kd /= 10
        mean_kr /= 10
        mean_hs /= 10
        draw_image_bg.text((10, 310), 'Last 10 games played:', font=font)
        draw_image_bg.text((10, 340), f'KAD: {format(mean_k, ".1f")} / {format(mean_a, ".1f")} / {format(mean_d, ".1f")}', font=font)
        draw_image_bg.text((10, 370), f'K/D: {format(mean_kd, ".2f")}', font=font)
        draw_image_bg.text((10, 400), f'K/R: {format(mean_kr, ".2f")}', font=font)
        draw_image_bg.text((10, 430), f'Total 4K: {total_4k}', font=font)
        draw_image_bg.text((10, 460), f'Total 5K: {total_5k}', font=font)
        draw_image_bg.text((10, 490), f'HS: {format(mean_hs, ".1f")}%', font=font)

        draw_image_bg.text((270, 70), f'{player_stat[0]["region"]}: {player_stat[0]["region_place"]}', font=font)
        draw_image_bg.text((270, 100), f'{player_stat[0]["country"]}: {player_stat[0]["country_place"]}', font=font)

        return image_background
