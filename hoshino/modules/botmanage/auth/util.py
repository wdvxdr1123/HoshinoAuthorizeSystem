import random
import string
from datetime import *

from hoshino import msghandler, Service, priv

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
        if gid in group_dict:
            group_dict[gid] = group_dict[gid] + timedelta(days=key_dict[key])
        else:
            group_dict[gid] = today + timedelta(days=key_dict[key])
        key_dict.pop(key)
        return f"群【{gid}】充值成功！\n授权到期时间：{group_dict[gid].isoformat()}"
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


def get_group_list():
    group_list = []
    for key, value in group_dict.iteritems():
        deadline = f'{value.year}-{value.month}-{value.day}'
        group_list.append({'gid': key, 'deadline': deadline})
    return group_list


def query_key(key):
    if key in key_dict:
        return key_dict[key]
    else:
        return 0


@sv.scheduled_job('cron', minute='*/5', jitter=20)
async def auth_update():
    today = datetime.now()
    for key, value in group_dict.iteritems():
        if value.__lt__(today):
            group_dict.pop(key)
            await sv.bot.send_group_msg(group_id=key, message='您的授权已到期！')
            sv.logger.info(f"群{key}的授权到期!")
