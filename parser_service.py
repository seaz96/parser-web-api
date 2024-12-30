import asyncio
import parser


class ParserBackgroundService:
    def __init__(self):
        self.cooldown = 3600

    async def parse_site(self):
        while True:
            print('Starting parse task.')
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, lambda: parser.run())
            print(f'Parsing stopped. Next parse in {self.cooldown} seconds.')
            await asyncio.sleep(self.cooldown)
