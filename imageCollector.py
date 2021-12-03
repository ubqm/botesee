from PIL import Image, ImageFont, ImageDraw
import requests
from faceit_get_funcs import player_details


def collect_image(request_json, stat_json, prev_nick1, prev_elo1, prev_nick2, prev_elo2):
    image_list = []
    font_folder = 'Outfit'
    font_file = 'Outfit-Bold.ttf'
    font_file_mainscore = 'Outfit-ExtraBold.ttf'

    font_avs = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 18)
    font_mainscore = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file_mainscore}', 50)
    font_player_score = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 32)
    font_player_stats = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22)
    font_halftimes = ImageFont.truetype(f'templates/fonts/{font_folder}/{font_file}', 22)

    dark_avatar_bot = Image.open('templates/background_features/for_avatar_bot.png')
    dark_avatar_top = Image.open('templates/background_features/for_avatar_top.png')

    for idx_round, round in enumerate(stat_json['rounds']):
        img1 = Image.open(f'templates/maps/{round["round_stats"]["Map"]}.jpg')
        img1 = img1.resize((960, 540))
        draw = ImageDraw.Draw(img1)
        if round['teams'][0]['team_stats']['Team Win'] == '1':
            img2 = Image.open('templates/background_features/Win-topleft.png')
            img3 = Image.open('templates/background_features/Lose-botleft.png')
        else:
            img2 = Image.open('templates/background_features/Lose-topleft.png')
            img3 = Image.open('templates/background_features/Win-botleft.png')
        img1.paste(img2, (0, 0), img2)
        img1.paste(img3, (0, 0), img3)
        dark_middle = Image.open('templates/background_features/dark-middle2.png')
        img1.paste(dark_middle, (0, 0), dark_middle)

        if 'Overtime score' in round['teams'][0]['team_stats'].keys():
            if round['teams'][0]['team_stats']['Overtime score'] == '0' and round['teams'][1]['team_stats']['Overtime score'] == '0':
                isOvertimeinGame = False
            else:
                isOvertimeinGame = True
        else:
            isOvertimeinGame = False

        for idx_team, team in enumerate(round['teams']):
            if isOvertimeinGame:
                halftimes = f"{team['team_stats']['First Half Score']}—{team['team_stats']['Second Half Score']}—{team['team_stats']['Overtime score']}"
                w, h = draw.textsize(halftimes, font=font_halftimes)
                draw.text(((146 - w) / 2, 235 + 42 * idx_team), halftimes, font=font_halftimes)
            else:
                halftimes = f"{team['team_stats']['First Half Score']}—{team['team_stats']['Second Half Score']}"
                w, h = draw.textsize(halftimes, font=font_halftimes)
                draw.text(((146 - w) / 2, 235 + 42 * idx_team), halftimes, font=font_halftimes)

            for idx_player, player in enumerate(team['players']):
                for idx_req_player, req_player in enumerate(request_json['payload']['teams'][idx_team]['roster']):
                    if player['nickname'] == req_player['nickname']:

                        player_elo = str(player_details(player['nickname'])['games']['csgo']['faceit_elo'])
                        if float(player["player_stats"]["K/D Ratio"]) >= 1.3:
                            stat_color = (0, 190, 0, 255)
                        elif float(player["player_stats"]["K/D Ratio"]) < 0.6:
                            stat_color = (170, 0, 0, 255)
                        elif 0.8 > float(player["player_stats"]["K/D Ratio"]) >= 0.6:
                            stat_color = (255, 165, 0, 255)
                        else:
                            stat_color = (255, 255, 255, 255)

                        if req_player['avatar'] != '':
                            avatar_req = requests.get(req_player['avatar'], stream=True)
                            avatar_img = Image.open(avatar_req.raw)
                            avatar_img = avatar_img.resize((130, 130))
                        else:
                            avatar_img = Image.open('templates/question-mark-icon.jpg')
                            avatar_img = avatar_img.resize((130, 130))
                        draw_avatar = ImageDraw.Draw(avatar_img)
                        faceitlvl = req_player['game_skill_level']

                        if idx_team == 0:
                            avatar_img.paste(dark_avatar_bot, (0, 0), dark_avatar_bot)
                            avatar_img.paste(dark_avatar_top, (0, 0), dark_avatar_top)
                            avatar_img.paste(Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                                             (0, 0),
                                             Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                            w, h = draw.textsize(player_elo, font=font_avs)
                            draw_avatar.text((125 - w, 0), player_elo, font=font_avs)
                            for idn, nick in enumerate(prev_nick1.split('\n')):
                                if nick == player['nickname']:
                                    if int(player_elo) > int(prev_elo1.split('\n')[idn]):
                                        diff_elo_team_1 = '+' + str(abs(int(player_elo) - int(prev_elo1.split('\n')[idn])))
                                    else:
                                        diff_elo_team_1 = str(abs(int(player_elo) - int(prev_elo1.split('\n')[idn])))

                        else:
                            avatar_img.paste(dark_avatar_top, (0, 0), dark_avatar_top)
                            avatar_img.paste(dark_avatar_bot, (0, 0), dark_avatar_bot)
                            avatar_img.paste(Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                                             (0, 106),
                                             Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                            w, h = draw.textsize(player_elo, font=font_avs)
                            draw_avatar.text((125 - w, 107), player_elo, font=font_avs)
                            for idn, nick in enumerate(prev_nick2.split('\n')):
                                if nick == player['nickname']:
                                    if int(player_elo) > int(prev_elo2.split('\n')[idn]):
                                        diff_elo_team_2 = '+' + str(abs(int(player_elo) - int(prev_elo2.split('\n')[idn])))
                                    else:
                                        diff_elo_team_2 = str(abs(int(player_elo) - int(prev_elo2.split('\n')[idn])))

                        w, h = draw.textsize(req_player['nickname'], font=font_avs)
                        if w > 130:
                            draw_avatar.text((0, 107 - idx_team * 107), req_player['nickname'], font=font_avs)
                        else:
                            draw_avatar.text(((130 - w) / 2, 107 - idx_team * 107), req_player['nickname'], font=font_avs)

                        img1.paste(avatar_img, (146 + idx_player * 162, 20 + 370 * idx_team))

                        kad = f'{player["player_stats"]["Kills"]}/{player["player_stats"]["Assists"]}/{player["player_stats"]["Deaths"]}'
                        w, h = draw.textsize(kad, font=font_player_score)
                        draw.text((130 + (162 - w) / 2 + idx_player * 162, 155 + 195 * idx_team), kad, font=font_player_score)
                        mvp = f'MVP: {player["player_stats"]["MVPs"]}'
                        draw.text((146 + idx_player * 162, 200 + 116 * idx_team), mvp, font=font_player_stats)
                        kr = f'K/R: {player["player_stats"]["K/R Ratio"]}'
                        draw.text((146 + idx_player * 162, 220 + 76 * idx_team), kr, font=font_player_stats)
                        kd = f'K/D: {player["player_stats"]["K/D Ratio"]}'
                        draw.text((146 + idx_player * 162, 240 + 36 * idx_team), kd, font=font_player_stats, fill=stat_color)
                        # hs = f'HS %: {player["player_stats"]["Headshots %"]}'
                        # draw.text((146 + idx_player * 162, 240 + 36 * idx_team), hs, font=font_player_stats)

        w, h = draw.textsize(round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
        draw.text(((146 - w) / 2, 65), round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
        w, h = draw.textsize(round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)
        draw.text(((146 - w) / 2, 415), round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)
        image_list.append(img1)

        w, h = draw.textsize(diff_elo_team_1, font=font_avs)
        draw.text(((146 - w) / 2, 150 - h), diff_elo_team_1, font=font_avs)
        w, h = draw.textsize(diff_elo_team_2, font=font_avs)
        draw.text(((146 - w) / 2, 390), diff_elo_team_2, font=font_avs)

        # w, h = draw.textsize('+25', font=font_avs)
        # draw.text(((146 - w) / 2, 150 - h), '+25', font=font_avs)
        # w, h = draw.textsize('-25', font=font_avs)
        # draw.text(((146 - w) / 2, 390), '-25', font=font_avs)

    return image_list
