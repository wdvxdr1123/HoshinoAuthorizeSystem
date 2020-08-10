from nonebot import on_command, message_preprocessor
import random
import string
import re
import hoshino
from hoshino import R, Service, priv, util, sucmd
from sqlitedict import SqliteDict
from hoshino.typing import CQEvent
from datetime import *

key_dict = SqliteDict('./key.sqlite', autocommit=True)
group_dict = SqliteDict('./group.sqlite', autocommit=True)
today = datetime.now()


@on_command('添加注册码', only_to_me=True)
async def say_hello(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    length = session.event.message.extract_plain_text()
    length = length[5:].strip()
    if length.isdigit():
        length = int(length)
        key_dict[key] = length
        await session.send(f'已添加注册码:{key}\n授权时长:{length}天')
    else:
        await session.send(f'请输入正确的授权时长！')


@on_command('查看注册码', only_to_me=True)
async def say_hello(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    msg = ''
    for key, value in key_dict.iteritems():
        msg += f'注册码:{key}\n时长:{value}天\n'
    await session.send(msg)


@on_command('授权列表', only_to_me=True)
async def say_hello(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    msg = ''
    for key, value in group_dict.iteritems():
        msg += f'群号:{key}\n截至时间:{value}\n'
    await session.send(msg)


@on_command('注册', only_to_me=True)
async def say_hello(session):
    if not session.event.group_id:
        return
    gid = session.event.group_id
    raw_text = session.event.message.extract_plain_text()
    key = raw_text[3:].strip()
    if key in key_dict:
        if gid in group_dict:
            group_dict[gid] = group_dict[gid] + timedelta(days=key_dict[key])
        else:
            group_dict[gid] = today + timedelta(days=key_dict[key])
        key_dict.pop(key)
        await session.send(f"注册成功!\n授权截止日期:{group_dict[gid].isoformat()}")
    else:
        await session.send("注册码无效！")


@on_command('查看授权状态', only_to_me=True)
async def say_hello(session):
    if not session.event.group_id:
        return
    gid = session.event.group_id
    if gid in group_dict:
        await session.send('您的授权截止至'+group_dict[gid].isoformat())
    else:
        await session.send('您还没有获得授权，请联系维护组获取授权!')
