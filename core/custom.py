#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   custom.py
@Time    :   2022/04/02 10:17:03
@Author  :   Viperorz
@Version :   v1.2.0
@License :   (C)Copyright 2021-2022
@Desc    :   None
"""


from typing import Any, Dict

import yaml
from pyrogram import filters
from pyrogram.types import Message
from tools.constants import STORE_TRACE_DATA, COMMAND_YML
from tools.storage import SimpleStore

CMDS_DATA: Dict[str, Any] = yaml.full_load(open(COMMAND_YML, 'rb'))
CMDS_PREFIX = CMDS_DATA.get('help').get('all_prefixes')


def command(key: str):
    """匹配UserBot指令"""
    if type(CMDS_DATA.get(key).get('cmd')) == str:
        cmd = [CMDS_DATA.get(key).get('cmd'), key]
        return filters.me & filters.text & filters.command(cmd, CMDS_PREFIX)

    cmd = CMDS_DATA.get(key).get('cmd')
    return filters.me & filters.text & filters.command(cmd, CMDS_PREFIX)


def is_traced():
    """正则匹配用户输入指令及参数"""
    async def func(flt, _, msg: Message):
        async with SimpleStore(auto_flush=False) as store:
            trace_data = store.get_data(STORE_TRACE_DATA)
            if not trace_data:
                return False
            elif not trace_data.get(msg.from_user.id):
                return False
            return True

    # "data" kwarg is accessed with "flt.data" above
    return filters.incoming & filters.create(func)
