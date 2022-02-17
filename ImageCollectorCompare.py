from PIL import Image, ImageFont, ImageDraw
import requests
from faceit_get_funcs import player_details, region_stats, player_history, match_stats
from ProjectExceptions import NothingException


class ImageCollectorCompare:
    def __init__(self, nickname1:str, nickname2:str, amount:str="50", output_type:str="games"):
        self.nickname1 = nickname1
        self.nickname2 = nickname2
        self.output_type = self.validate_output_type(output_type)
        self.amount = self.validate_amount(amount)
        self.background = Image.new(mode="RGBA", size=(960, 540))
        self.background = Image.open(f"templates/maps/black.jpg")
        self.draw_bg = ImageDraw.Draw(self.background)

    @staticmethod
    def validate_output_type(output_type):
        if output_type in ["game", "games", "month", "months", "week", "weeks", "days", "day"]:
            return output_type
        else:
            return "games"

    def validate_amount(self, amount):
        if self.output_type in ["game", "games"]:
            return int(amount) if amount.isdigit() and 10 <= int(amount) <= 100 else 20

    def collect_image(self):
        player1_stats = self.collect_stat(self.nickname1)
        player2_stats = self.collect_stat(self.nickname2)
        if player1_stats and player2_stats:
            return self.draw_image(player1_stats, player2_stats)

    def collect_stat(self, nickname):
        list_of_games = []
        try:
            pd, history, player_info = self.get_player_info(nickname)
        except NothingException:
            return None

        for match_h in history['items']:
            match_stat = match_stats(match_h['match_id'])
            if match_stat is None:
                continue
            for map_s in match_stat['rounds'][::-1]:
                game = self.compile_game(player_info, pd, map_s, match_h)
                list_of_games.append(game)
        return list_of_games

    def get_player_info(self, nickname):
        pd = player_details(nickname)
        # TODO: if output_type is not "games" -> change player_history() call
        if pd is not None:
            history = player_history(pd['player_id'], offset=0, limit=self.amount)
            if history is not None:
                region_place = region_stats(player_id=pd['player_id'],
                                            region=pd['games']['csgo']['region'])['items'][0]['position']
                country_place = region_stats(player_id=pd['player_id'],
                                             region=pd['games']['csgo']['region'],
                                             country=pd['country'])['items'][0]['position']
                player_info = {"nickname": nickname,
                               "region_place": region_place,
                               "country_place": country_place}
                return pd, history, player_info
        raise NothingException

    @staticmethod
    def compile_game(player_info, pd, map_s, match_h):
        game = {}
        for team in map_s['teams']:
            for player in team['players']:
                if pd['player_id'] == player['player_id']:
                    game = {"nickname": player_info['nickname'],
                            "steam_id": pd['games']['csgo']['game_player_id'],
                            "avatar": pd['avatar'],
                            "background": pd['cover_image'],
                            "country": pd['country'],
                            "country_place": player_info['country_place'],
                            "region_place": player_info['region_place'],
                            "player_id": pd['player_id'],
                            "region": pd['games']['csgo']['region'],
                            "skill_level": pd['games']['csgo']['skill_level'],
                            "faceit_elo": pd['games']['csgo']['faceit_elo'],
                            "result": player['player_stats']['Result'],
                            "kills": player['player_stats']['Kills'],
                            "assists": player['player_stats']['Assists'],
                            "deaths": player['player_stats']['Deaths'],
                            "kdratio": player['player_stats']['K/D Ratio'],
                            "krratio": player['player_stats']['K/R Ratio'],
                            "mvps": player['player_stats']['MVPs'],
                            "headshots%": player['player_stats']['Headshots %'],
                            "4k": player['player_stats']['Quadro Kills'],
                            "5k": player['player_stats']['Penta Kills'],
                            "mapscore": map_s['round_stats']['Score'],
                            "mapname": map_s['round_stats']['Map'],
                            "started_at": match_h['started_at']}
        return game

    def get_comparison_dict(self, player1_stats, player2_stats):
        comparison_dict = {"nickname": (player1_stats[0]['nickname'], player2_stats[0]['nickname']),
                           "steam_id": (player1_stats[0]['steam_id'], player2_stats[0]['steam_id']),
                           "avatar": (player1_stats[0]['avatar'], player2_stats[0]['avatar']),
                           "background": (player1_stats[0]['background'], player2_stats[0]['background']),
                           "country": (player1_stats[0]['country'], player2_stats[0]['country']),
                           "country_place": (player1_stats[0]['country_place'], player2_stats[0]['country_place']),
                           "region_place": (player1_stats[0]['region_place'], player2_stats[0]['region_place']),
                           "player_id": (player1_stats[0]['player_id'], player2_stats[0]['player_id']),
                           "region": (player1_stats[0]['region'], player2_stats[0]['region']),
                           "skill_level": (player1_stats[0]['skill_level'], player2_stats[0]['skill_level']),
                           "faceit_elo": (player1_stats[0]['faceit_elo'], player2_stats[0]['faceit_elo'])}
        p1_mean_stats = self.get_mean_stats(player1_stats)
        p2_mean_stats = self.get_mean_stats(player2_stats)

        for keys in zip(p1_mean_stats, p2_mean_stats):
            comparison_dict[keys[0]] = (p1_mean_stats[keys[0]], p2_mean_stats[keys[1]])

        return comparison_dict

    @staticmethod
    def get_mean_stats(player_stat):
        mean_k, mean_a, mean_d, mean_kd, mean_kr, mean_hs, total_4k, total_5k, winrate, mvps = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in range(len(player_stat)):
            mean_k += int(player_stat[i]['kills'])
            mean_a += int(player_stat[i]['assists'])
            mean_d += int(player_stat[i]['deaths'])
            mean_kd += float(player_stat[i]['kdratio'])
            mean_kr += float(player_stat[i]['krratio'])
            mean_hs += float(player_stat[i]['headshots%'])
            total_4k += int(player_stat[i]['4k'])
            total_5k += int(player_stat[i]['5k'])
            winrate += float(player_stat[i]['result'])
            mvps += int(player_stat[i]['mvps'])

        mean_k, mean_a, mean_d, mean_kd, mean_kr, mean_hs, winrate, mvps = \
            map((lambda x: x / len(player_stat)), [mean_k, mean_a, mean_d, mean_kd, mean_kr, mean_hs, winrate, mvps])
        stat_dict = {"mean_k": mean_k, "mean_a": mean_a, "mean_d": mean_d, "mean_kd": mean_kd,
                     "mean_kr": mean_kr, "mean_hs": mean_hs, "winrate": int(winrate*100),
                     "total_4k": total_4k, "total_5k": total_5k, "mvps": mvps}
        return stat_dict

    @staticmethod
    def get_avatar(avatar):
        if avatar != "":
            avatar_req = requests.get(avatar, stream=True)
            image_avatar = Image.open(avatar_req.raw)
            image_avatar = image_avatar.resize((130, 130))
        else:
            image_avatar = Image.open(f"templates/question-mark-icon.jpg")
            image_avatar = image_avatar.resize((130, 130))
        return image_avatar

    @staticmethod
    def compare_stats(value, category):
        if category in ["1f", "2f", "%"]:
            rating = max(value) / min(value)
            if value[0] >= value[1]:
                if rating >= 1.4:
                    return (0, 190, 0, 255), (170, 0, 0, 255)
                elif rating >= 1.2:
                    return (0, 190, 0, 255), (255, 255, 255, 255)
                else:
                    return (255, 255, 255, 255), (255, 255, 255, 255)
            else:
                if rating >= 1.4:
                    return (170, 0, 0, 255), (0, 190, 0, 255)
                elif rating >= 1.2:
                    return (255, 255, 255, 255), (0, 190, 0, 255)
                else:
                    return (255, 255, 255, 255), (255, 255, 255, 255)
        elif category in ["total"]:
            return (255, 255, 255, 255), (255, 255, 255, 255)

    def place_stat(self, comparison_dict):
        font = ImageFont.truetype(f"templates/fonts/Outfit/Outfit-Bold.ttf", 26)
        left_stat_x = 410
        right_stat_x = 550
        start_y = 220
        step = 30
        i = 0
        stat_percent = ["mean_hs", "winrate"]
        stat_1f = ["mvps", "mean_k", "mean_d"]
        stat_2f = ["mean_kd", "mean_kr"]
        stat_total = ["total_4k", "total_5k", "faceit_elo"]
        for key, value in comparison_dict.items():
            if key in stat_percent:
                color_left, color_right = self.compare_stats(value, "%")
                w, h = self.draw_bg.textsize(f"{int(comparison_dict[key][0])}%", font=font)
                self.draw_bg.text((left_stat_x - w, start_y + step * i), f"{int(comparison_dict[key][0])}%", font=font, fill=color_left)
                self.draw_bg.text((right_stat_x, start_y + step * i), f"{int(comparison_dict[key][1])}%", font=font, fill=color_right)
                i += 1
            elif key in stat_1f:
                color_left, color_right = self.compare_stats(value, "1f")
                w, h = self.draw_bg.textsize(f"{comparison_dict[key][0]:.1f}", font=font)
                self.draw_bg.text((left_stat_x - w, start_y + step * i), f"{comparison_dict[key][0]:.1f}", font=font, fill=color_left)
                self.draw_bg.text((right_stat_x, start_y + step * i), f"{comparison_dict[key][1]:.1f}", font=font, fill=color_right)
                i += 1
            elif key in stat_2f:
                color_left, color_right = self.compare_stats(value, "2f")
                w, h = self.draw_bg.textsize(f"{comparison_dict[key][0]:.2f}", font=font)
                self.draw_bg.text((left_stat_x - w, start_y + step * i), f"{comparison_dict[key][0]:.2f}", font=font, fill=color_left)
                self.draw_bg.text((right_stat_x, start_y + step * i), f"{comparison_dict[key][1]:.2f}", font=font, fill=color_right)
                i += 1
            elif key in stat_total:
                color_left, color_right = self.compare_stats(value, "total")
                w, h = self.draw_bg.textsize(f"{comparison_dict[key][0]}", font=font)
                self.draw_bg.text((left_stat_x - w, start_y + step * i), f"{int(comparison_dict[key][0])}", font=font, fill=color_left)
                self.draw_bg.text((right_stat_x, start_y + step * i), f"{comparison_dict[key][1]}", font=font, fill=color_right)
                i += 1

    @staticmethod
    def get_player_background(bg_link, output_width=960, output_height=540):
        if bg_link != "":
            bg_req = requests.get(bg_link, stream=True)
            background = Image.open(bg_req.raw)
        else:
            background = Image.open(f"templates/background_features/dark-right-side-for-stat.png")

        width, height = background.size
        if height != output_height:
            aspect_ratio = output_height / height
            background = background.resize((int(width * aspect_ratio), output_height))
        width, height = background.size
        if width >= output_width:
            left = int((width - output_width) / 2)
            top = 0
            right = int((width - output_width) / 2 + output_width)
            bottom = height
            background = background.crop((left, top, right, bottom))
            background.resize((output_width, output_height))
        return background

    def draw_image(self, player1_stats, player2_stats):
        dark_middle = Image.open(f"templates/background_features/dark-middle-compare.png")
        font = ImageFont.truetype(f"templates/fonts/Outfit/Outfit-Bold.ttf", 26)
        font_name = ImageFont.truetype(f"templates/fonts/Outfit/Outfit-Bold.ttf", 36)
        player1_bg = self.get_player_background(player1_stats[0]['background'], 480, 540)
        player2_bg = self.get_player_background(player2_stats[0]['background'], 480, 540)
        self.background.paste(player1_bg, (0, 0))
        self.background.paste(player2_bg, (480, 0))
        self.background.paste(dark_middle, (0, 0), dark_middle)
        avatar1 = self.get_avatar(player1_stats[0]['avatar'])
        avatar2 = self.get_avatar(player2_stats[0]['avatar'])
        self.background.paste(avatar1, (10, 10))
        self.background.paste(avatar2, (820, 10))
        self.draw_bg = ImageDraw.Draw(self.background)

        self.draw_bg.text((160, 20), player1_stats[0]['nickname'], font=font_name)
        w, h = self.draw_bg.textsize(player2_stats[0]['nickname'], font=font_name)
        self.draw_bg.text((810 - w, 20), player2_stats[0]['nickname'], font=font_name)

        comparison_dict = self.get_comparison_dict(player1_stats, player2_stats)

        w, h = self.draw_bg.textsize(f"{self.amount} {self.output_type}", font=font)
        self.draw_bg.text(((960 - w) / 2, 24), f"{self.amount} {self.output_type}", font=font)

        w, h = self.draw_bg.textsize(f"ELO", font=font)
        self.draw_bg.text(((960 - w) / 2, 220), f"ELO", font=font)
        w, h = self.draw_bg.textsize("avgK", font=font)
        self.draw_bg.text(((960 - w) / 2, 250), "avgK", font=font)
        w, h = self.draw_bg.textsize("avgD", font=font)
        self.draw_bg.text(((960 - w) / 2, 280), "avgD", font=font)
        w, h = self.draw_bg.textsize("K/D", font=font)
        self.draw_bg.text(((960 - w) / 2, 310), "K/D", font=font)
        w, h = self.draw_bg.textsize("K/R", font=font)
        self.draw_bg.text(((960 - w) / 2, 340), "K/R", font=font)
        w, h = self.draw_bg.textsize("HS", font=font)
        self.draw_bg.text(((960 - w) / 2, 370), "HS", font=font)
        w, h = self.draw_bg.textsize(f"W/L", font=font)
        self.draw_bg.text(((960 - w) / 2, 400), f"W/L", font=font)
        w, h = self.draw_bg.textsize("4K", font=font)
        self.draw_bg.text(((960 - w) / 2, 430), "4K", font=font)
        w, h = self.draw_bg.textsize("5K", font=font)
        self.draw_bg.text(((960 - w) / 2, 460), "5K", font=font)
        w, h = self.draw_bg.textsize(f"MVP", font=font)
        self.draw_bg.text(((960 - w) / 2, 490), f"MVP", font=font)

        self.draw_bg.text((160, 70), f"{comparison_dict['region'][0]}: {comparison_dict['region_place'][0]}", font=font)
        self.draw_bg.text((160, 100), f"{comparison_dict['country'][0]}: {comparison_dict['country_place'][0]}", font=font)

        self.place_stat(comparison_dict)

        w, h = self.draw_bg.textsize(f"{comparison_dict['region'][1]}: {comparison_dict['region_place'][1]}", font=font)
        self.draw_bg.text((810 - w, 70), f"{comparison_dict['region'][1]}: {comparison_dict['region_place'][1]}", font=font)
        w, h = self.draw_bg.textsize(f"{comparison_dict['country'][1]}: {comparison_dict['country_place'][1]}", font=font)
        self.draw_bg.text((810 - w, 100), f"{comparison_dict['country'][1]}: {comparison_dict['country_place'][1]}", font=font)

        return self.background
