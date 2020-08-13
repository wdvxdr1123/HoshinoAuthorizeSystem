from nonebot import on_command, scheduler
import random
import string
import re
import hoshino
from hoshino import R, Service, priv, util, sucmd, msghandler
from sqlitedict import SqliteDict
from hoshino.typing import CQEvent
from datetime import *


key_dict = msghandler.key_dict
group_dict = msghandler.group_dict

sv = Service('auth', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)

@on_command('生成卡密', only_to_me=False)
async def creat_key(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{1,5})\*(\d{1,3})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('格式输错了啦憨批！请按照“生成卡密 时长*数量”进行输入！')
    length = int(m.group(1))
    keynum = int(m.group(2))
    _keylist = []
    if keynum == 0:
        await session.finish('你搁那生你🐴空气呢？')
    for keynum in range(keynum):
        key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
        key_dict[key] = length
        _keylist.append(key)
    keylist = "\n".join(_keylist)
    await session.send(f'已生成{keynum}份{length}天的卡密：\n{keylist}')

@on_command('卡密列表', only_to_me=False)
async def key_list(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    msg = '======卡密列表======\n'
    i = 0
    for key, value in key_dict.iteritems():
        i = i + 1
        msg += f'卡密:{key}\n时长:{value}天\n'
    await session.send(msg)


@on_command('授权列表', only_to_me=False)
async def group_list(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    msg = '======授权列表======\n'
    i = 0
    for key, value in group_dict.iteritems():
        i = i + 1
        msg += f'{i}、群号:{key}\n授权时间:{value}\n'
    await session.send(msg)


@on_command('充值', only_to_me=False)
async def group_kakin(session):
    today = datetime.now()
    if not session.event.group_id:
        if not session.current_arg:
            await session.finish('私聊使用卡密请发送“充值 卡密*群号”哦~')
        else:
            origin = session.current_arg.strip()
            pattern = re.compile(r'^(\w{16})\*(\d{5,15})$')
            m = pattern.match(origin)
            if m is None:
                await session.finish('呜呜...卡密或者格式错误...\n私聊使用卡密请发送“充值 卡密*群号”，发送前请仔细核对卡密哦')
            key = m.group(1)
            gid = m.group(2)
            if key in key_dict:
                if gid in group_dict:
                    group_dict[gid] = group_dict[gid] + timedelta(days=key_dict[key])
                else:
                    group_dict[gid] = today + timedelta(days=key_dict[key])
                key_dict.pop(key)
                await session.send(f"群【{gid}】充值成功！\n授权到期时间：{group_dict[gid].isoformat()}")
            else:
                await session.send("卡密似乎无效诶QwQ")
    else:
        if not session.current_arg:
            await session.finish('如果要为本群充值的话发送“充值 卡密”就可以了哦~')
        else:
            if '*' not in session.current_arg.strip():
                gid = session.event.group_id
                key = session.current_arg.strip()
                if key in key_dict:
                    if gid in group_dict:
                        group_dict[gid] = group_dict[gid] + timedelta(days=key_dict[key])
                    else:
                        group_dict[gid] = today + timedelta(days=key_dict[key])
                    key_dict.pop(key)
                    await session.send(f"群【{gid}】充值成功！\n授权到期时间：{group_dict[gid].isoformat()}")
                else:
                    await session.send("卡密似乎无效诶QwQ")
            else:
                origin = session.current_arg.strip()
                pattern = re.compile(r'^(\w{16})\*(\d{5,15})$')
                m = pattern.match(origin)
                if m is None:
                    await session.finish('呜呜...卡密或者格式错误...\n如果要在这里给其他群充值的话请发送“充值 卡密*群号”，发送前请仔细核对卡密哦')
                key = m.group(1)
                gid = m.group(2)
                if key in key_dict:
                    if gid in group_dict:
                        group_dict[gid] = group_dict[gid] + timedelta(days=key_dict[key])
                    else:
                        group_dict[gid] = today + timedelta(days=key_dict[key])
                    key_dict.pop(key)
                    await session.send(f"群【{gid}】充值成功！\n授权到期时间：{group_dict[gid].isoformat()}")
                else:
                    await session.send("卡密似乎无效诶QwQ")                


@on_command('查询授权', only_to_me=False)
async def time_query(session):
    if not session.event.group_id:
        if not session.current_arg:
            await session.finish('请发送“查询授权 群号”来进行指定群的授权查询')
        else:
            gid = session.current_arg.strip()
            print(gid)
            if gid in group_dict:
                await session.send('您的授权截止至' + group_dict[gid].isoformat())
            else:
                await session.send('您还没有获得授权QwQ')
    else:
        if not session.current_arg:
            gid = session.event.group_id
            if gid in group_dict:
                await session.send('您的授权截止至' + group_dict[gid].isoformat())
            else:
                await session.send('您还没有获得授权QwQ')
        else:
            gid = session.current_arg.strip()
            print(gid)
            if gid in group_dict:
                await session.send('您的授权截止至' + group_dict[gid].isoformat())
            else:
                await session.send('您还没有获得授权QwQ')

@on_command('授权', only_to_me=False)
async def time_change(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    today = datetime.now()
    if not session.current_arg:
        await session.finish('请发送“授权 群号±时长”来进行指定群的授权，时长最长为99999')
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{5,15})([+-]\d{1,5})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('到底是格式出错还是群号时长出错我也不知道...\n请发送“授权 群号±时长”来进行指定群的授权，时长最长为99999')
    gid = int(m.group(1))
    days = int(m.group(2))
    if gid in group_dict:
        group_dict[gid] = group_dict[gid] + timedelta(days=days)
    else:
        group_dict[gid] = today + timedelta(days=days)
    if days < 0:
        cgmsg = '减少'
        days = abs(days)
    else:
        cgmsg = '增加'
    await session.send(f"群【{gid}】已{cgmsg}{days}天\n授权到期时间：{group_dict[gid].isoformat()}")

@on_command('转移授权', only_to_me=False)
async def group_change(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    if not session.current_arg:
        await session.finish('请发送“转移授权 旧群群号*新群群号”来进行群授权转移')
    today = datetime.now()
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{5,15})\*(\d{5,15})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('格式错误或者群号错误XD\n请发送“转移授权 旧群群号*新群群号”来转移群授权时长\n如果新群已经授权，则会增加对应时长。')
    ogid = int(m.group(1))
    ngid = int(m.group(2))
    if ngid in group_dict:
        time = group_dict[ogid] - today
        group_dict[ngid] = group_dict[ngid] + time
        group_dict.pop(ogid)
        await session.send(f"授权转移成功~\n旧群【{ogid}】授权已清空\n新群【{ngid}】授权到期时间：{group_dict[ngid].isoformat()}")
    else:
        group_dict[ngid] = group_dict[ogid]
        group_dict.pop(ogid)
        await session.send(f"授权转移成功~\n旧群【{ogid}】授权已清空\n新群【{ngid}】授权到期时间：{group_dict[ngid].isoformat()}")

@on_command('授权状态', only_to_me=False)
async def auth_status(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    for sid in hoshino.get_self_ids():
        sgl = set(g['group_id']
            for g in await session.bot.get_group_list(self_id=sid))
        frl = set(f['user_id']
            for f in await session.bot.get_friend_list(self_id=sid))
    #直接从service里抄了，面向cv编程才是真
    gpnum = len(sgl)
    frnum = len(frl)
    agpnum = 0
    keynum = 0
    for i in group_dict.iteritems():
        agpnum = agpnum + 1
    for i in key_dict.iteritems():
        keynum = keynum + 1
    msg = f'Bot账号：{sid}\n所在群数：{gpnum}\n好友数：{frnum}\n授权群数：{agpnum}\n未使用卡密数：{keynum}'
    await session.send(msg)

@on_command('退群', only_to_me=False)
async def group_leave(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    gid = int(session.current_arg.strip())
    await session.send('正在褪裙...')
    await session.bot.set_group_leave(group_id=gid)

@sv.scheduled_job('cron', minute='*/2', jitter=20)
async def auth_update():
    today = datetime.now()
    for key, value in group_dict.iteritems():
        if value.__lt__(today):
            group_dict.pop(key)
            await sv.bot.send_group_msg(group_id=key, message='您的授权已到期！')
            sv.logger.info(f"群{key}的授权到期!")