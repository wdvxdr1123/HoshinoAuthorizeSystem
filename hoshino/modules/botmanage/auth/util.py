import random
import string
from datetime import *
from nonebot import CQHttpError
from hoshino import msghandler, Service, priv, get_bot, get_self_ids

key_dict = msghandler.key_dict
group_dict = msghandler.group_dict
sv = Service('auth', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)


def generate_key():
    new_key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    while new_key in key_dict:  # 防止生成重复的卡密，不过概率太低了。。。
        new_key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return new_key


def reg_group(gid, key):
    if key in key_dict:
        today = datetime.now()
        key_duration = timedelta(days=key_dict[key])
        left_time = group_dict[gid] if gid in group_dict else datetime.now()
        group_dict[gid] = key_duration + left_time
        key_dict.pop(key)
        return group_dict[gid].isoformat()
    return False


def add_key(duration):
    new_key = generate_key()
    key_dict[new_key] = duration
    return new_key


def get_key_list():
    key_list = []
    for key, value in key_dict.iteritems():
        key_list.append({'key': key, 'duration': value})
    return key_list


def del_key(key):
    if key in key_dict:
        key_dict.pop(key)
        return True
    return False


def update_key(key, duration):
    if key in key_dict:
        key_dict[key] = duration
        return True
    return False


def update_group(gid, duration):
    extra_duration = timedelta(days=duration)
    left_time = group_dict[gid] if gid in group_dict else datetime.now()
    group_dict[gid] = extra_duration + left_time


async def get_group_list():
    group_list = []
    for key, value in group_dict.iteritems():
        deadline = f'{value.year}-{value.month}-{value.day} {value.hour}:{value.minute}'
        try:
            group_info = await get_bot().get_group_info(group_id=key, no_cache=True)
        except CQHttpError:
            group_info = {'group_name': '未知'}
        group_list.append({'gid': key, 'deadline': deadline, 'groupName': group_info['group_name']})
    return group_list


def query_key(key):
    return key_dict[key] if key in key_dict else 0


def query_group(gid):
    return group_dict[gid].isoformat() if gid in group_dict else 0


def transfer_group(old_gid, new_gid):
    today = datetime.now()
    left_time = group_dict[old_gid] - today if old_gid in group_dict else timedelta(days=0)
    group_dict[new_gid] = left_time + (group_dict[new_gid] if new_gid in group_dict else today)
    group_dict.pop(old_gid)


async def gun_group(gid):
    try:
        await get_bot().set_group_leave(group_id=gid)
    except CQHttpError:
        return False
    return True


async def notify_group(gid, txt):
    try:
        await get_bot().send_group_msg(group_id=gid, message=txt)
    except CQHttpError:
        return False
    return True


@sv.scheduled_job('cron', minute='*/5', jitter=20)
async def auth_update():
    today = datetime.now()
    for key, value in group_dict.iteritems():
        if value.__lt__(today):
            group_dict.pop(key)
            await sv.bot.send_group_msg(group_id=key, message='您的授权已到期！')
            sv.logger.info(f"群{key}的授权到期!")
