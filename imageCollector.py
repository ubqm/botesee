from PIL import Image, ImageFont, ImageDraw
import requests
from faceit_get_funcs import player_details


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
            elo_change_team1, elo_change_team2 = self.calculateEloChange(match, self.prev_nick1, self.prev_nick2,
                                                                         self.prev_elo1, self.prev_elo2)
            self.drawMapImage(match, elo_change_team1, elo_change_team2)
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

    def calculateEloChange(self, match, prev_nick1, prev_nick2, prev_elo1, prev_elo2):
        diff_elo_team_1, diff_elo_team_2 = '', ''

        for idx_team, team in enumerate(match['teams']):
            for idx_player, player in enumerate(team['players']):
                player_elo = str(player_details(player['nickname'])['games']['csgo']['faceit_elo'])
                for idn, nick in enumerate(prev_nick1.split('\n')):
                    if nick == player['nickname']:
                        if int(player_elo) > int(prev_elo1.split('\n')[idn]):
                            diff_elo_team_1 = '+' + str(abs(int(player_elo) - int(prev_elo1.split('\n')[idn])))
                            break
                        else:
                            diff_elo_team_1 = str(int(player_elo) - int(prev_elo1.split('\n')[idn]))
                            break
                for idn, nick in enumerate(prev_nick2.split('\n')):
                    if nick == player['nickname']:
                        if int(player_elo) > int(prev_elo2.split('\n')[idn]):
                            diff_elo_team_2 = '+' + str(abs(int(player_elo) - int(prev_elo2.split('\n')[idn])))
                            break
                        else:
                            diff_elo_team_2 = str(int(player_elo) - int(prev_elo2.split('\n')[idn]))
                            break

        return diff_elo_team_1, diff_elo_team_2

    def drawMapImage(self, match, elo_change_team1, elo_change_team2):
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

        w, h = self.draw_image_map.textsize(elo_change_team1, font=self._fonts['avatar'])
        self.draw_image_map.text(((146 - w) / 2, 150 - h), elo_change_team1, font=self._fonts['avatar'])
        w, h = self.draw_image_map.textsize(elo_change_team2, font=self._fonts['avatar'])
        self.draw_image_map.text(((146 - w) / 2, 390), elo_change_team2, font=self._fonts['avatar'])

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
                    w, h = self.draw_image_map.textsize(player_elo, font=self._fonts['avatar'])
                    draw_image_avatar.text((125 - w, 0), player_elo, font=self._fonts['avatar'])
                else:
                    image_avatar.paste(self.image_dark_avatar_top, (0, 0), self.image_dark_avatar_top)
                    image_avatar.paste(self.image_dark_avatar_bot, (0, 0), self.image_dark_avatar_bot)
                    image_avatar.paste(
                        Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                        (0, 106),
                        Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                    w, h = self.draw_image_map.textsize(player_elo, font=self._fonts['avatar'])
                    draw_image_avatar.text((125 - w, 107), player_elo, font=self._fonts['avatar'])

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
        self.draw_image_map.text((146 + idx_player * 162, 200 + 116 * idx_team), mvp, font=self._fonts['player_stats'])
        kr = f'K/R: {player["player_stats"]["K/R Ratio"]}'
        self.draw_image_map.text((146 + idx_player * 162, 220 + 76 * idx_team), kr, font=self._fonts['player_stats'])
        kd = f'K/D: {player["player_stats"]["K/D Ratio"]}'
        self.draw_image_map.text((146 + idx_player * 162, 240 + 36 * idx_team), kd, font=self._fonts['player_stats'],
                                 fill=self.stat_color)
