import asyncio

from nonebot.adapters.onebot.v11 import Bot


# 解禁
async def ban_say(bot: Bot, group, qq):
    # 禁言20min
    await bot.set_group_ban(
        group_id=int(group),
        user_id=int(qq),
        duration=20 * 60,
    )


# 禁言
async def unban_say(bot: Bot, group, qq):
    await bot.set_group_ban(
        group_id=int(group),
        user_id=int(qq),
        duration=0,
    )


# 群聊
async def send_gm(bot: Bot, group, says):
    await bot.send_group_msg(group_id=group, message=says)
    await asyncio.sleep(1)


# 私聊
async def private_say(bot: Bot, qq, group, says):
    await bot.send_private_msg(
        user_id=int(qq),
        group_id=int(group),
        message=str(says),
    )
    await asyncio.sleep(1)


# 改卡片名称
async def group_card(bot:Bot, group, qq, wt):
    await bot.set_group_card(
        group_id=int(group),
        user_id=int(qq),
        card=str(wt),
    )


# 获取卡片名称
async def get_member_card_name(bot: Bot, group, qq) -> str:
    j = await bot.get_group_member_info(group_id=group, user_id=qq)
    return j["card"]


# 成员是否为管理员
async def get_member_permission(bot: Bot, group, qq) -> bool:
    j = await bot.get_group_member_info(group_id=group, user_id=qq)
    return j["card"] in ["owner", "admin"]


# 返回好友列表
async def friend_list(bot: Bot) -> list:
    lj = await bot.get_friend_list()
    l = []
    for j in lj:
        l.append(j["user_id"])
    return l
