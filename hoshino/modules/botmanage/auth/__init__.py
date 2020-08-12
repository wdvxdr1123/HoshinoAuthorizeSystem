import asyncio
from datetime import *
import re
import nonebot
from nonebot import on_command, on_request

import hoshino
from hoshino import Service, msghandler
from .web_server import auth

#app = nonebot.get_bot().server_app  #
#app.register_blueprint(auth)  # 开启网页服务请取消注释这两句

key_dict = msghandler.key_dict
group_dict = msghandler.group_dict
reply_dict = {}

sv = Service('auth', visible=False)


@on_command('添加注册码', only_to_me=True)
async def say_hello(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    key = web_server.generate_key()
    cmd = re.split(' ', session.event.message.extract_plain_text())
    print(cmd)
    length = cmd[1]
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
    uid = session.event.user_id
    raw_text = session.event.message.extract_plain_text().strip()
    cmd = re.split(' ', raw_text)
    key = cmd[1]
    print(cmd)
    if cmd[2].isdigit():
        gid = int(cmd[2])
        await session.send(f'即将为您的群{gid}注册\n请回复确认(空格)<群号>,确认后将会为您注册!')
        # 二次确认!
        reply_dict[uid] = {'gid': str(gid), 'key': key}
    else:
        await session.send(f'请输入正确的群号!')
        return


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


@on_request('group')
async def approve_group_invite(session):
    gid = session.event.group_id
    if session.event.sub_type != 'invite':
        return
    if gid in group_dict:
        bot = nonebot.get_bot()
        ev = session.event
        await bot.set_group_add_request(flag=ev.flag, sub_type=ev.sub_type, approve=True)
    else:
        bot = nonebot.get_bot()
        ev = session.event
        await bot.set_group_add_request(flag=ev.flag, sub_type=ev.sub_type, approve=False, reason='请联系维护组!')


@on_command('确认')
async def check_reply(session):
    uid = session.event.user_id
    raw_text = session.event.message.extract_plain_text().strip()
    cmd = re.split(' ', raw_text)
    gid = cmd[1]
    if uid in reply_dict:
        ugid = (reply_dict[uid])['gid']
        key = (reply_dict[uid])['key']
        if (ugid == gid) and (key in key_dict):
            web_server.reg_group(gid, key)
            await session.send(f"注册成功!\n授权截止日期:{group_dict[gid].isoformat()}")
        else:
            await session.send("注册失败！")
        reply_dict.pop(uid)
