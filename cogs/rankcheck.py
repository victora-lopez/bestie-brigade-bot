from concurrent.futures import ThreadPoolExecutor
import cloudscraper
import discord
from datetime import datetime
from discord.ext import commands
from tqdm import tqdm
from threading import Lock

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
        self.scraper = cloudscraper.create_scraper()
        self.embed = discord.Embed(title='__**Rank Check:**__', color=0xfce1e4, timestamp=datetime.now())
        self.executor = ThreadPoolExecutor(max_workers=12)
        self.user_ids: list[tuple[str, int]] = []
        self.player_peak_ranks: dict[str, dict[str, str]] = {'Our team': {}, 'Enemy team': {}}
        self.friendly_team_id: int = 0
        self.match_id: str = ''
        self.error_message: str = ''
        self._thread_lock = Lock()

    def _initialize_rivals_defaults(self):
        self.user_ids = []
        self.player_peak_ranks = {'Our team': {}, 'Enemy team': {}}
        self.friendly_team_id = 0
        self.match_id = ''
        self.error_message = ''
        self.embed = discord.Embed(title='__**Rank Check:**__', color=0xfce1e4, timestamp=datetime.now())


    def fetch_match_id(self, url:str = None) -> bool:
        if url is None:
            self.error_message = 'Invalid url provided for fetching match id'
            return False
        response = self.scraper.get(url, params={"season": "11"}, timeout=15)
        try:
            data = response.json().get('data')
            self.friendly_team_id = data.get('matches')[0].get('segments')[0].get('metadata').get('teamId')
            self.match_id = data.get('matches')[0].get('attributes').get('id')
            return True
        except AttributeError:
            self.error_message = 'Sorry there was an error fetching the match id due to a missing attribute. Tell victor to fix his bot.'
            return False
        except Exception as e:
            self.error_message = f'There was an error fetching match id: {e}'
            return False

    def fetch_user_ids(self, url:str = None) -> bool:
        if url is None:
            self.error_message = 'Invalid url provided for fetching user ids'
            return False
        response = self.scraper.get(url, timeout=15)
        if not response.ok:
            self.error_message = response.json().get('errors')[0].get('message')
            return False
        try:
            data = response.json().get('data')

            segments = data.get('segments')
            for segment in segments:
                segment_type = segment.get('type')
                if segment_type is not None and segment_type == 'player':
                    user_id = segment.get('metadata').get('platformInfo').get('platformUserIdentifier') #TODO: refactor to use library that fetches nested json data
                    player_team_id = segment.get('metadata').get('teamId')
                    if user_id in {'lodezel', 'iodezel', 'lodezei',
                                   'chadpiIIed', 'chudimus',
                                   'RickyGallahad', 'RickyLancelot',
                                   'gurt gobain', 'yoboigurt'}:
                        continue
                    self.user_ids.append((user_id, player_team_id))
        except Exception as e:
            self.error_message = f'Error fetching user ids: {e}'
            return False
        return True

    def thread_peak_ranks(self, player_info: tuple[str, int], progress_bar: tqdm):
        player_id, player_team_id = player_info
        url = f'{self.base_url}profile/ign/{player_id}/segments/career?mode=all'
        try:
            response = self.scraper.get(url, timeout=15)
            if response.ok:
                player_data = response.json().get('data')
                player_peak = 'No ranked data'
                for record in player_data:
                    if record.get('type') == 'ranked-peaks':
                        player_peak = record.get('stats').get('lifetimePeakRanked').get('metadata').get('tierName')
                        break
            elif response.status_code == 400:
                player_peak = 'Private Account'
            elif response.status_code == 429:
                player_peak = 'Got caught botting gotta wait a day now (T-T)'
                self.error_message = 'Hit the api too many times try again later'
            else:
                player_peak = 'Error fetching rank'
                print(f'An error has occurred fetching {player_id}\'s peak rank')
        except Exception as e:
            player_peak = 'Request failed'
            print(f'Exception for {player_id}: {e}')

        with self._thread_lock:
            team = 'Our team' if player_team_id == self.friendly_team_id else 'Enemy team'
            self.player_peak_ranks[team][player_id] = player_peak
        progress_bar.update(1)

    def fetch_peak_ranks(self) -> None:
        if not self.user_ids:
            self.error_message = 'No user ids were stored'
            return
        with tqdm(total=len(self.user_ids), desc='Fetching peak ranks', unit='profiles') as progress_bar:
            def progress_thread_peak_ranks(player_info: tuple[str, int]):
                self.thread_peak_ranks(player_info, progress_bar)
            list(self.executor.map(progress_thread_peak_ranks, self.user_ids))


    def get_gamer_tag(self, user: str, account_type: str) -> tuple[str | None, str | None]:
        gamer_tag_map = self.gamer_tag_map.get(user)
        if gamer_tag_map is None:
            return None, f'Couldn\'t find {user}\'s gamer tag'
        else:
            if account_type not in {'main', 'smurf', 'solo'}:
                return None, 'Man just put main or smurf with the rank check command'
            gamer_tag = gamer_tag_map.get(account_type)
            return gamer_tag, None

    def generate_table_content(self):
        for team, peak_rank_map in self.player_peak_ranks.items():
            lines: list[str] = []
            for player, peak_rank in peak_rank_map.items():
                lines.append(f'> {player}: {peak_rank}')
            content = '\n'.join(lines)
            self.embed.add_field(name=f'**{team}**', value=content, inline=False)

    @commands.command(name='rankcheck', aliases=['rc'])
    async def rankcheck(self, ctx, account_type: str = 'main'):
        await ctx.send(f"Entered rankcheck function, {ctx.author} initiated")
        user = ctx.author.name.lower()
        gamer_tag, message = self.get_gamer_tag(user, account_type)
        if gamer_tag is None:
            await ctx.send(message)
        else:
            successful_fetch = self.fetch_match_id(f'{self.base_url}matches/ign/{gamer_tag}')
            if successful_fetch:
                successful_fetch = self.fetch_user_ids(f'{self.base_url}matches/{self.match_id}')
                if successful_fetch:
                    try:
                        self.fetch_peak_ranks()
                        self.generate_table_content()
                        await ctx.send(embed=self.embed)
                    except Exception as e:
                        print(f'An error has occurred: {e}')
                else:
                    await ctx.send(self.error_message)
            else:
                await ctx.send(self.error_message)
        self._initialize_rivals_defaults() # always want to set values back to default/empty values for each run

async def setup(bot):
    await bot.add_cog(RivalsCog(bot))