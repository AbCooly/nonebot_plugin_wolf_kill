from nonebot.adapters.onebot.v11 import Bot


async def ban_say(bot: Bot, group, qq):  # 传入禁言列表
    # 禁言20min
    await bot.set_group_ban(
        group_id=int(group),
        user_id=int(qq),
        duration=20 * 60,
    )


async def unban_say(bot: Bot, group, qq):
    await bot.set_group_ban(
        group_id=int(group),
        user_id=int(qq),
        duration=0,
    )


async def send_gm(bot: Bot, group, says):
    await bot.send_group_msg(group_id=group, message=says)



async def private_say(bot: Bot, qq, group, says):
    await bot.send_private_msg(
        user_id=int(qq),
        group_id=int(group),
        message=str(says),
    )


async def group_card(bot:Bot, group, qq, wt):
    await bot.set_group_card(
        group_id=int(group),
        user_id=int(qq),
        card=str(wt),
    )
