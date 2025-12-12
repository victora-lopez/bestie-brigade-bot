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
        self.base_url = 'https://api.tracker.gg/api/v2/marvel-rivals/standard/'

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
                url = f'{self.base_url}matches/ign/{gamer_tag}'
                scaper = cloudscraper.create_scraper()
                response = scaper.get(url, params={"season": "10"}, timeout=15)
                data = response.json().get('data')
                try:
                    match_id = data.get('matches')[0].get('attributes').get('id')
                except AttributeError:
                    await ctx.send(f'Sorry there was an error fetching the match id due to a missing attribute. Tell victor to fix his bot.')
                except Exception as e:
                    await ctx.send(f'There was an error fetching match id: {e}')
            a=5

async def setup(bot):
    await bot.add_cog(RivalsCog(bot))