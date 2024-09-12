from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str

@dataclass
class GroupId:
    id : int

@dataclass
class Config:
    tg_bot: TgBot
    tg_group_id: GroupId



def load_config() -> Config:
    env : Env = Env()
    env.read_env()
    return Config(tg_bot = TgBot(token = env('BOT_TOKEN1')),tg_group_id= GroupId(id = env('chat_id')))

