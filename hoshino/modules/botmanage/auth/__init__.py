from datetime import *
import re
import nonebot
from nonebot import on_command, on_request
import hoshino
from hoshino import msghandler
from .web_server import auth
from . import util

app = nonebot.get_bot().server_app  #
app.register_blueprint(auth)  # 关闭网页服务请注释这两句

key_dict = msghandler.key_dict
group_dict = msghandler.group_dict


@on_command('生成卡密', only_to_me=True)
async def produce_key(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{1,5})\*(\d{1,3})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('格式输错了啦憨批！请按照“生成卡密 时长*数量”进行输入！')
    duration = int(m.group(1))
    key_num = int(m.group(2))
    if key_num == 0:
        await session.finish('你搁那生你🐴空气呢？')
    key_list = []
    for _ in range(key_num):
        new_key = util.add_key(duration)
        key_list.append(new_key)
    await session.send(f'已生成{key_num}份{duration}天的卡密：\n' + '\n'.join(key_list))


@on_command('卡密列表', only_to_me=False)
async def view_key_list(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    if session.event.group_id:
        return
    key_list = util.get_key_list()
    msg = '======卡密列表======\n'
    for items in key_list:
        msg += '卡密:' + items['key'] + '\n时长:' + str(items['duration']) + '天\n'
    await session.send(msg)


@on_command('授权列表', only_to_me=False)
async def view_aut_list(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    group_list = util.get_group_list()
    msg = '======授权列表======\n'
    for items in group_list:
        msg += '群号:' + items['gid'] + '\n截止日期:' + str(items['deadline']) + '天\n'
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

#su可以查询指定群，群员只能查询当前群
@on_command('查询授权', only_to_me=False)
async def time_query(session):
    if not session.event.group_id:
        if session.event.user_id not in hoshino.config.SUPERUSERS:
            return
        if not session.current_arg:
            await session.finish('请发送“查询授权 群号”来进行指定群的授权查询')
        else:
            gid = session.current_arg.strip()
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
            if session.event.user_id not in hoshino.config.SUPERUSERS:
                await session.finish('非运维组不能查询其他群的授权哟')
            gid = session.current_arg.strip()
            if gid in group_dict:
                await session.send('您的授权截止至' + group_dict[gid].isoformat())
            else:
                await session.send('您还没有获得授权QwQ')


@on_command('授权', only_to_me=False)
async def time_change(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    today = datetime.now()
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{5,15})([+-]\d{1,5})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('请发送“授权 群号±时长”来进行指定群的授权，时长最长为99999')
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
    o_gid = int(m.group(1))
    o_gid = int(m.group(2))
    if o_gid in group_dict:
        left_time = group_dict[o_gid] - today
        group_dict[o_gid] = group_dict[o_gid] + left_time
        group_dict.pop(o_gid)
        await session.send(f"授权转移成功~\n旧群【{o_gid}】授权已清空\n新群【{o_gid}】授权到期时间：{group_dict[o_gid].isoformat()}")
    else:
        group_dict[o_gid] = group_dict[o_gid]
        group_dict.pop(o_gid)
        await session.send(f"授权转移成功~\n旧群【{o_gid}】授权已清空\n新群【{o_gid}】授权到期时间：{group_dict[o_gid].isoformat()}")


@on_command('授权状态', only_to_me=False)
async def auth_status(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    for sid in hoshino.get_self_ids():
        sgl = set(g['group_id']
                  for g in await session.bot.get_group_list(self_id=sid))
        frl = set(f['user_id']
                  for f in await session.bot.get_friend_list(self_id=sid))
    # 直接从service里抄了，面向cv编程才是真
    gp_num = len(sgl)
    fr_num = len(frl)
    key_num = len(util.get_key_list())
    agp_num = len(util.get_group_list())
    msg = f'Bot账号：{sid}\n所在群数：{gp_num}\n好友数：{fr_num}\n授权群数：{agp_num}\n未使用卡密数：{key_num}'
    await session.send(msg)


@on_command('退群', only_to_me=False)
async def group_leave(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    gid = int(session.current_arg.strip())
    await session.send('正在褪裙...')
    await session.bot.set_group_leave(group_id=gid)


# 自动接受(拒绝)已(未)充值的群的邀请
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


@on_command('检验卡密')
async def key_check(session):
    if session.event.group_id:
        return
    if not session.current_arg:
        await session.finish('检验卡密请发送“检验卡密 卡密”哦~')
    else:
        origin = session.current_arg.strip()
        pattern = re.compile(r'^(\w{16})$')
        m = pattern.match(origin)
        if m is None:
            await session.finish('格式输错了啦憨批！请按照“检验卡密 卡密”进行输入！')
        key = m.group(1)
        if duration := util.query_key(key):
            await session.finish(f'该卡密有效!\n授权时长:{duration}天')
        else:
            await session.finish(f'该卡密无效!')
