import asyncio
import parser


class ParserBackgroundService:
    def __init__(self):
        self.cooldown = 3600

    async def parse_site(self, ws_manager):
        while True:
            print('Starting parse task.')
            asyncio.run(ws_manager.broadcast({
                "action": "parsing started"
            }))
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, lambda: parser.run())
            print(f'Next parse in {self.cooldown} seconds.')
            await asyncio.sleep(self.cooldown)
