from datetime import *

import nonebot
from nonebot import on_command

import hoshino
from hoshino import Service, msghandler
from .web_server import auth

#app = nonebot.get_bot().server_app    # 打开网页服务请注释这两句
#app.register_blueprint(auth)          # 打开网页服务请注释这两句

key_dict = msghandler.key_dict
group_dict = msghandler.group_dict

sv = Service('auth', visible=False)


@on_command('添加注册码', only_to_me=True)
async def say_hello(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    key = web_server.gerenate_key()
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
    today = datetime.now()
    raw_text = session.event.message.extract_plain_text().strip()
    key = raw_text[2:].strip()
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
        await session.send('您的授权截止至' + group_dict[gid].isoformat())
    else:
        await session.send('您还没有获得授权，请联系维护组获取授权!')


@sv.scheduled_job('cron', minute='*/2', jitter=20)
async def auth_update():
    today = datetime.now()
    for key, value in group_dict.iteritems():
        if value.__lt__(today):
            group_dict.pop(key)
            await sv.bot.send_group_msg(group_id=key, message='您的授权已到期！')
            sv.logger.info(f"群{key}的授权到期!")
