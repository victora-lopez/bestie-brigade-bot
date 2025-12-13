from discord.ext import commands
import cloudscraper


class RivalsCog(commands.Cog):
    def __init__(self, bot):
        self.gamer_tag_map = {
            'lodezel': {'main': 'lodezel', 'smurf': 'lodezei', 'solo': 'iodezel'},
            'chad_432': {'main': 'chadpiIIed', 'smurf': 'chudimus'},
            'rickygallahad': {'main': 'RickyGallahad', 'smurf': 'RickyLancelot'},
            'gurt989': {'main': 'gurt gobain', 'smurf': 'yoboygurt'}
        }
        self.bot = bot
        self.scraper = cloudscraper.create_scraper()
        self.base_url = 'https://api.tracker.gg/api/v2/marvel-rivals/standard/'
        self.user_ids: list[tuple[str, int]] = []
        self.player_peak_ranks: dict[str, dict[str, str]] = {'Our team': {}, 'Enemy team': {}}
        self.friendly_team_id: int = 0
        self.match_id: str = ''
        # TODO: Refactor include error message here and update when an error occurs?
        # TODO: solves a lot or return and weird function organization

    def fetch_match_id(self, url:str = None) -> tuple[str, bool]:
        if url is None:
            return 'Invalid url provided for fetching match id', False
        response = self.scraper.get(url, params={"season": "10"}, timeout=15)
        data = response.json().get('data')
        try:
            self.friendly_team_id = data.get('matches')[0].get('segments')[0].get('metadata').get('teamId')
            self.match_id = data.get('matches')[0].get('attributes').get('id')
            return 'No error', True
        except AttributeError:
            return f'Sorry there was an error fetching the match id due to a missing attribute. Tell victor to fix his bot.', False
        except Exception as e:
            return f'There was an error fetching match id: {e}', False

    def fetch_user_ids(self, url:str = None) -> tuple[str | None, bool]:
        if url is None:
            return 'Invalid url provided for fetching user ids', False
        response = self.scraper.get(url, timeout=15)
        try:
            data = response.json().get('data')
        except Exception as e:
            return f'Error fetching user ids: {e}', False

        segments = data.get('segments')
        for segment in segments:
            segment_type = segment.get('type')
            if segment_type is not None and segment_type == 'player':
                user_id = segment.get('metadata').get('platformInfo').get('platformUserIdentifier')
                player_team_id = segment.get('metadata').get('teamId')
                if user_id in {'lodezel', 'iodezel', 'lodezei',
                               'chadpiIIed', 'chudimus',
                               'RickyGallahad', 'RickyLancelot',
                               'gurt gobain', 'yoboigurt'}:
                    continue
                self.user_ids.append((user_id, player_team_id))
        return None, True

    def fetch_peak_ranks(self, url:str = None) -> tuple[str | None, bool]:
        if url is None:
            return 'Invalid url provided for fetching peak ranks', False
        for player_id, player_team_id in self.user_ids:
            response = self.scraper.get(url, timeout=15)
            if response.ok:
                player_data = response.json().get('data')
            elif response.status_code == 400:
                if player_team_id == self.friendly_team_id:
                    self.player_peak_ranks['Our team'][player_id] = 'Private Account'
                else:
                    self.player_peak_ranks['Enemy team'][player_id] = 'Private Account'
                continue
            else:
                print(f'An error has occurred fetching {player_id}\'s peak rank')
                continue

            for record in player_data:
                if record.get('type') == 'ranked-peaks':
                    player_peak = record.get('stats').get('lifetimePeakRanked').get('metadata').get('tierName')
                    break
            else:
                player_peak = f'No record found for {player_id}\'s peak rank'
            if player_team_id == self.friendly_team_id:
                self.player_peak_ranks['Our team'][player_id] = player_peak
            else:
                self.player_peak_ranks['Enemy team'][player_id] = player_peak


    def get_gamer_tag(self, user: str, account_type: str) -> tuple[str | None, str | None]:
        gamer_tag_map = self.gamer_tag_map.get(user)
        if gamer_tag_map is None:
            return None, f'Couldn\'t find {user}\'s gamer tag'
        else:
            if account_type not in {'main', 'smurf', 'solo'}:
                return None, 'Man just put main or smurf with the rank check command'
            gamer_tag = gamer_tag_map.get(account_type)
            return gamer_tag, None



    @commands.command(name='rankcheck', aliases=['rc'])
    async def rankcheck(self, ctx, account_type: str = 'main'):
        await ctx.send(f"Entered rankcheck function, {ctx.author} initiated")
        user = ctx.author.name.lower()
        gamer_tag, message = self.get_gamer_tag(user, account_type)
        if gamer_tag is None:
            await ctx.send(message)
        else:
            error_msg,successful_fetch = self.fetch_match_id(f'{self.base_url}matches/ign/{gamer_tag}')
            if successful_fetch:
                message,successful_fetch = self.fetch_user_ids(f'{self.base_url}matches/{self.match_id}')
                if successful_fetch:
                    try:
                        self.fetch_peak_ranks(f'{self.base_url}profile/ign/{player_id}/segments/career?mode=all', player_id, player_team_id)
                    except Exception as e:
                        print(f'An error has occurred: {e}')
                    a=5
                    b=5
                else:
                    ctx.send(message)
            else:
                await ctx.send(error_msg)


        a=5

async def setup(bot):
    await bot.add_cog(RivalsCog(bot))