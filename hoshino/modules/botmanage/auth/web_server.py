from datetime import *
import string
import random

import nonebot
from quart import request, Blueprint, jsonify, render_template

from hoshino import Service, priv, msghandler

manage_password = 'test'  # 管理密码
key_dict = msghandler.key_dict
group_dict = msghandler.group_dict

sv = Service('homework', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)
auth = Blueprint('auth', __name__, url_prefix='/auth', template_folder="./vue", static_folder='./vue',
                 static_url_path='')
bot = nonebot.get_bot()
app = bot.server_app


def generate_key():
    return ''.join(random.sample(string.ascii_letters + string.digits, 16))


def reg_group(gid, key):
    if key in key_dict:
        today = datetime.now()
        if gid in group_dict:
            group_dict[gid] = group_dict[gid] + timedelta(days=key_dict[key])
        else:
            group_dict[gid] = today + timedelta(days=key_dict[key])
        key_dict.pop(key)
        return True
    return False


@auth.route('/')
async def index():
    return await render_template("index.html")


@auth.route('/api/login', methods=['POST'])
async def login_auth():
    password = request.args.get('password')
    if password == manage_password:
        return 'success'
    return password


@auth.route('/api/get/key', methods=['GET'])
async def get_key():
    password = request.args.get('password')
    if password != manage_password:
        return 'failed'
    key_list = []
    for key, value in key_dict.iteritems():
        key_list.append({'key': key, 'length': value})
    return jsonify(key_list)


@auth.route('/api/addkey', methods=['POST'])
async def add_key():
    if request.method == 'POST':
        length = request.args.get('length')
        key = generate_key()
        key_dict[key] = length
        return 'success'
    return 'failed'


@auth.route('/api/delkey', methods=['DELETE'])
async def del_key():
    if request.method == 'DELETE':
        key = request.args.get('key')
        if key in key_dict:
            key_dict.pop(key)
            return 'success'
    return 'failed'


@auth.route('/api/get/group', methods=['GET'])
async def get_group():
    password = request.args.get('password')
    if password != manage_password:
        return 'failed'
    group_list = []
    for key, value in group_dict.iteritems():
        deadline = f'{value.year}-{value.month}-{value.day}'
        group_list.append({'gid': key, 'deadline': deadline})
    return jsonify(group_list)


@auth.route('/api/activate', methods=['POST'])
async def activate_group():
    key = request.args.get('key')
    gid = request.args.get('gid')
    if reg_group(gid, key):
        return 'success'
    return 'failed'
