from PIL import Image, ImageFont, ImageDraw
import requests


def collect_image(request_json, stat_json):
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
                draw.text((25, 235 + 42 * idx_team), halftimes, font=font_halftimes)
            else:
                halftimes = f"{team['team_stats']['First Half Score']}—{team['team_stats']['Second Half Score']}"
                draw.text((45, 235 + 42 * idx_team), halftimes, font=font_halftimes)

            for idx_player, player in enumerate(team['players']):
                req_player_idx = idx_player
                skip_player = False
                for req_idx, req_player in enumerate(request_json['payload']['teams'][idx_team]['roster']):
                    if player['nickname'] == req_player['nickname']:
                        req_player_idx = req_idx
                    else:
                        skip_player = True

                if not skip_player:
                    if request_json['payload']['teams'][idx_team]['roster'][req_player_idx]['avatar'] != '':
                        avatar_req = requests.get(request_json['payload']['teams'][idx_team]['roster'][req_player_idx]['avatar'], stream=True)
                        avatar_img = Image.open(avatar_req.raw)
                        avatar_img = avatar_img.resize((130, 130))
                    else:
                        avatar_img = Image.open('templates/question-mark-icon.jpg')
                        avatar_img = avatar_img.resize((130, 130))
                    faceitlvl = request_json['payload']['teams'][idx_team]['roster'][req_player_idx]['game_skill_level']
                    if idx_team == 0:
                        avatar_img.paste(dark_avatar_bot, (0, 0), dark_avatar_bot)
                        avatar_img.paste(Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                                         (0, 0),
                                         Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                    else:
                        avatar_img.paste(dark_avatar_top, (0, 0), dark_avatar_top)
                        avatar_img.paste(Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"),
                                         (0, 106),
                                         Image.open(f'templates/faceit_icons/faceit{faceitlvl}.png').convert("RGBA"))
                    draw_avatar = ImageDraw.Draw(avatar_img)

                    w, h = draw.textsize(request_json['payload']['teams'][idx_team]['roster'][req_player_idx]['nickname'], font=font_avs)
                    if w > 130:
                        draw_avatar.text((0, 107 - idx_team * 107), request_json['payload']['teams'][idx_team]['roster'][req_player_idx]['nickname'], font=font_avs)
                    else:
                        draw_avatar.text(((130 - w) / 2, 107 - idx_team * 107), request_json['payload']['teams'][idx_team]['roster'][req_player_idx]['nickname'], font=font_avs)

                    img1.paste(avatar_img, (146 + idx_player * 162, 20 + 370 * idx_team))

                    kad = f'{player["player_stats"]["Kills"]}/{player["player_stats"]["Assists"]}/{player["player_stats"]["Deaths"]}'
                    w, h = draw.textsize(kad, font=font_player_score)
                    draw.text((130 + (162 - w) / 2 + idx_player * 162, 155 + 195 * idx_team), kad, font=font_player_score)
                    mvp = f'MVP: {player["player_stats"]["MVPs"]}'
                    draw.text((146 + idx_player * 162, 200 + 116 * idx_team), mvp, font=font_player_stats)
                    kr = f'K/R: {player["player_stats"]["K/R Ratio"]}'
                    draw.text((146 + idx_player * 162, 220 + 76 * idx_team), kr, font=font_player_stats)
                    hs = f'HS %: {player["player_stats"]["Headshots %"]}'
                    draw.text((146 + idx_player * 162, 240 + 36 * idx_team), hs, font=font_player_stats)

        w, h = draw.textsize(round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
        draw.text(((146 - w) / 2, 65), round["teams"][0]["team_stats"]["Final Score"], font=font_mainscore)
        w, h = draw.textsize(round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)
        draw.text(((146 - w) / 2, 425), round["teams"][1]["team_stats"]["Final Score"], font=font_mainscore)
        image_list.append(img1)

    return image_list
