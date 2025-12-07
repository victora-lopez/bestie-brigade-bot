from discord.ext import commands

class RivalsCog(commands.Cog):
    def __init__(self, bot):
        self.gamer_tag_map = {
            'lodezel': {'main': 'lodezel', 'smurf': 'lodezei', 'solo': 'iodezel'},
            'chad_432': {'main': 'chadpiIIed', 'smurf': 'chudimus'},
            'rickygallahad': {'main': 'RickyGallahad', 'smurf': 'RickyLancelot'},
            'gurt989': {'main': 'gurt gobain', 'smurf': 'yoboygurt'}
        }
        self.bot = bot

    @commands.command()
    async def rankcheck(self, ctx):
        user = ctx.author
        gamer_tag = self.gamer_tag_map.get(user)
        if gamer_tag is None:
            await ctx.send(f'Couldn\'t find user\'s gamer tag')
        else:
           pass