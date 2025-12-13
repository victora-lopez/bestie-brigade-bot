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
            match_id = data.get('matches')[0].get('attributes').get('id')
            return match_id, True
        except AttributeError:
            return f'Sorry there was an error fetching the match id due to a missing attribute. Tell victor to fix his bot.', False
        except Exception as e:
            return f'There was an error fetching match id: {e}', False

    def fetch_user_ids(self, url:str = None) -> tuple[str, bool]:
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
                if user_id in {'lodezel', 'iodezel', 'lodezei',
                               'chadpiIIed', 'chudimus',
                               'RickyGallahad', 'RickyLancelot',
                               'gurt gobain', 'yoboigurt'}:
                    continue
                self.user_ids.append(user_id)
        return f'Successfully fetched user_ids', True


    @commands.command(name='rankcheck', aliases=['rc'])
    async def rankcheck(self, ctx, account_type: str = None):
        await ctx.send(f"Entered rankcheck function, {ctx.author} initiated")
        user = ctx.author.name.lower()
        gamer_tag = self.gamer_tag_map.get(user)

        if gamer_tag is None:
            await ctx.send(f'Couldn\'t find {user}\'s gamer tag')
        else:
            if account_type is None:
                account_type = 'main'

            gamer_tag = gamer_tag.get(account_type)

            if gamer_tag is None:
                await ctx.send(f'Invalid account type was entered please use one of the following: main, smurf, solo')
            else:
                match_id,successful_fetch = self.fetch_match_id(f'{self.base_url}matches/ign/{gamer_tag}')
                if successful_fetch:
                    message,successful_fetch = self.fetch_user_ids(f'{self.base_url}matches/{match_id}')
                    if successful_fetch:
                        pass
                    else:
                        ctx.send(message)
                else:
                    await ctx.send(match_id) # match_id returns either the match id or error_message


            a=5

async def setup(bot):
    await bot.add_cog(RivalsCog(bot))