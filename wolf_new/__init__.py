from typing import Tuple, List
from nonebot.rule import CommandRule, Rule, TrieRule, TRIE_VALUE
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.plugin.on import on_message
from .main import game_main, check_vote_finish, game_night, game_morning, to_morning, to_night, check_die, game_over
from .utils import send_gm
from .config import Config, finalpool


def on_command(cm, aliases=None, **kwargs,):     # 重写on_command
    commands = {cm} | (aliases or set())
    block = kwargs.pop("block", False)
    return on_message(
        command(*commands), block=block, **kwargs
    )


def command(*cmds) -> Rule:
    commands: List[Tuple[str, ...]] = []
    for command in cmds:
        if isinstance(command, str):
            command = (command,)
        commands.append(command)
        start = ""
        TrieRule.add_prefix(f"{command[0]}", TRIE_VALUE(start, command))
    return Rule(CommandRule(commands))


cg = on_command("/创建游戏", aliases={"/创建", "/开房"})    # 初始化
zd = on_command("/自定义", aliases={"/自定"})     # 自定义配置, 后面带参数
jn = on_command("/参加狼人杀", aliases={"/参加", "/加入"})  # 参加
ks = on_command("/开始游戏", aliases={"/开始"})  # 进入游戏线程
rs = on_command("/重新开始", aliases={"/重开"})  # 保留参赛人员,重新分配
gg = on_command("/结束游戏", aliases={"/结束"})  # 手动结束
# bm = on_command("/禁言模式", aliases={"/禁言"})  # 禁言模式 后面带参数: 开 关


@cg.handle()
async def _(bot: Bot, event: MessageEvent):
    if event.message_type == 'group':
        group = event.get_session_id().split('_')[1]
        if group in finalpool.configs:
            await cg.send("游戏已存在")
        else:
            cf = Config()
            finalpool.configs.setdefault(group, cf)
            finalpool.configs[group] = cf
            cf.group = group
            cf.bot = bot
            await cg.send("游戏房间初始化成功")
    else:
        await cg.send("请在群聊使用")


@zd.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    if event.message_type == 'group':
        group = event.get_session_id().split('_')[1]
        if group in finalpool.configs:
            # 构造角色配置
            args = str(arg).split()
            ivd = {v: k for k, v in finalpool.translate.items()}    # 翻转字典
            rl = []
            for i in args[3:]:
                rl.append(ivd[i])
            ll = []
            for i in range(0, 3):
                ll.append(int(args[i]))
            args[:3] = ll
            args[3:] = rl
            if "wolf" not in args:
                args.append("wolf")
            if "people" not in args:
                args.append("people")

            cf = finalpool.configs[group]
            cf.zdy = True
            cf.create_game = args
            await zd.send(f"自定义成功 + {str(cf.create_game)}")
        else:
            await zd.send("游戏房间不存在,请先创建游戏")
    else:
        await zd.send("请在群聊使用")
    # except:
    #     res = "当前能用的角色有:"
    #     for i in translate:
    #         res += f"{translate[i]} "
    #     await zd.send(
    #         message="自定义失败,请参考:/自定义 神数 狼数 平明数 有无警 身份...\neg:/自定义 3 3 3 平民 狼人 预言家 白狼王 女巫 猎人（平民，狼人，神至少要有一个！）\n" \
    #                 "定义一个3神3狼3人无警长,技能有 预言家 白狼王 女巫 猎人\n" + res)


@jn.handle()
async def _(event: MessageEvent):
    if event.message_type == 'group':
        group = event.get_session_id().split('_')[1]
        if group in finalpool.configs:
            qq = event.get_user_id()
            cf = finalpool.configs[group]
            if qq in finalpool.member_group or qq in cf.joiner:
                await jn.finish("你已参加游戏.不可重复参加")
            if len(cf.joiner) == 12:
                await jn.finish("已达到最大人数,无法参加!")
            cf.joiner.append(event.get_user_id())
            finalpool.member_group.setdefault(qq, group)
            await jn.send(f"参加游戏成功,已参加{len(cf.joiner)}人")
        else:
            await jn.send("游戏房间不存在,请先创建游戏")
    else:
        await jn.send("请在群聊使用")


@ks.handle()
async def _(event: MessageEvent):
    if event.message_type == 'group':
        group = event.get_session_id().split('_')[1]
        if group in finalpool.configs:
            cf = finalpool.configs[group]
            l = cf.joiner
            if cf.zdy:
                min_n = cf.create_game[0] + cf.create_game[1] + cf.create_game[2]
            else:
                min_n = 6
            n = len(l)
            if n < min_n:
                await ks.finish(f"人数太少了,无法开始,至少达到{min_n}人!")
            if cf.game_start:
                await ks.finish("游戏正在运行中,请勿重复开启")
            else:
                cf.group = group    # 设置群组配置
                await ks.send(f"正在为你开启游戏线程")
                await game_main(cf)
        else:
            await ks.finish("游戏房间不存在,请先创建游戏")
    else:
        await ks.finish("请在群聊使用")


@rs.handle()
async def _(event: MessageEvent):
    if event.message_type == 'group':
        group = event.get_session_id().split('_')[1]
        if group in finalpool.configs:
            cf = finalpool.configs[group]
            if cf.game_start:
                await rs.send("正在重新开始")
                cf.game_start = False
                cf.today = 0
                cf.role_qq = {}
                cf.qq_obj = {}
                cf.roles_dict_have = []
                cf.wolf_skill = False
                cf.maybe_die = []
                cf.die_say = False
                await game_main(cf)
            else:
                await rs.finish("游戏未开始")
        else:
            await rs.finish("游戏房间不存在,请先创建游戏")
    else:
        await rs.finish("请在群聊使用")


# @bm.handle()
# async def _(event: MessageEvent, arg: Message = CommandArg()):
#     if event.message_type == 'group':
#         group = event.get_session_id().split('_')[1]
#         if group in finalpool.configs:
#             cf = finalpool.configs[group]
#             if str(arg) == "开":
#                 await bm.send("开启禁言模式")
#                 cf.ban = True
#             else:
#                 cf.ban = False
#         else:
#             await bm.finish("游戏房间不存在,请先创建游戏")
#     else:
#         await bm.finish("请在群聊使用")


@gg.handle()
async def _(event: MessageEvent):
    if event.message_type == 'group':
        group = event.get_session_id().split('_')[1]
        if group in finalpool.configs:
            cf = finalpool.configs[group]
            if cf.game_start:
                await gg.send("正在结束游戏")
                await game_over(cf)
            else:
                await gg.finish("游戏未开始")
        else:
            await gg.finish("游戏房间不存在,请先创建游戏")
    else:
        await gg.finish("请在群聊使用")


tou = on_command("/投")  # 投票
guo = on_command("/过")  # 群聊结束发言 - 或结束遗言
skill = on_command("/skill", aliases={"/守护", "/摄梦", "/诅咒", "/刀", "/查", "/毒"})  # skill回合

wuya = on_command("/诅咒")  # 乌鸦回合
qishi = on_command("/决斗")  # 骑士回合
hunter = on_command("/枪")  # 猎人回合
wolf_king = on_command("/杀")  # 狼王回合
nvwu = on_command("/救")  # 女巫回合（救
wolf_bai = on_command("/自爆")
pass_do = on_command("/不使用技能", aliases={"/不使用", "跳过"})  # 跳过轮次


@tou.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    if event.message_type != "group":
        await tou.finish("请在群聊使用")
    qq = event.get_user_id()
    if qq not in finalpool.member_group:
        await tou.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    if cf.time != 2:
        await tou.finish("未到投票环节")
    try:
        num = int(str(arg))
    except ValueError:
        await tou.finish("指令输入错误,请重试")
        return

    obj = cf.qq_obj[qq]
    # if cf.ban:
    #     try:
    #         await obj.ban_say()
    #     except ActionFailed:
    #         pass

    if num == 0 or num > len(cf.joiner):
        obj.has_voted = True
        await tou.send("弃票成功")
        res = True
    else:
        v_obj = list(cf.qq_obj.values())[num - 1]
        res = await obj.vote(v_obj)
    if res:
        await check_vote_finish(cf)


@guo.handle()
async def _(event: MessageEvent):
    if event.message_type != "group":
        await guo.finish("请在群聊使用")
    qq = event.get_user_id()
    if qq not in finalpool.member_group:
        await guo.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    if not cf.die_say and cf.time != 1:
        await guo.finish("未到发言环节")
    obj = cf.qq_obj[qq]
    if obj not in cf.say_man:     # 身份验证
        await guo.finish("发言人不是你哦.")
    # if cf.ban:
    #     try:
    #         await obj.ban_say()  # 经言
    #     except ActionFailed:
    #         await send_gm(cf.bot, group, "禁言权限不足")

    cf.say_man.remove(obj)      # 移除发言人
    if cf.die_say:  # 遗言检测 , 白天死人(骑士决斗,白狼自爆)直接进入黑夜,
        cf.die_say = False
        await send_gm(cf.bot, group, "遗言结束,继续游戏.")
        if cf.night:    # 夜晚 进入白天, 白天 进入夜晚
            await to_morning(cf)
        else:
            await to_night(cf)
    else:
        await game_morning(cf)  # 下一位发言


@skill.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    qq = event.get_user_id()
    if qq not in finalpool.member_group:
        await skill.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    role = finalpool.roles_dict[cf.role_do]
    if cf.time != 0:
        await skill.finish("未到闭眼环节")
    try:
        num = int(str(arg))
    except ValueError:
        await skill.finish("指令输入错误,请重试")
        return
    obj = cf.qq_obj[qq]
    if obj.role != role:  # 身份检测
        await skill.finish("未轮到你的回合")
    if num == 0 or num > len(cf.joiner):
        await skill.send("对象不存在")
        return
    else:
        v_obj = list(cf.qq_obj.values())[num - 1]
        res = await obj.skill(v_obj)
    if res:     # 技能释放成功 继续
        await game_night(cf)


@qishi.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    qq = event.get_user_id()
    role = "qishi"
    if qq not in finalpool.member_group:
        await qishi.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    try:
        num = int(str(arg))
    except ValueError:
        await qishi.finish("指令输入错误,请重试")
        return
    obj = cf.qq_obj[qq]
    if role != finalpool.roles_dict[cf.role_do] and obj.role != role:  # 身份检测
        await qishi.finish("未轮到你的回合")
    if num == 0 or num > len(cf.joiner):
        await qishi.send("对象不存在")
        return
    else:
        v_obj = list(cf.qq_obj.values())[num - 1]
        res = await obj.skill(v_obj)
        if res:
            await check_die(cf)


@hunter.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    qq = event.get_user_id()
    role = "hunter"
    if qq not in finalpool.member_group:
        await hunter.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    try:
        num = int(str(arg))
    except ValueError:
        await hunter.finish("指令输入错误,请重试")
        return
    obj = cf.qq_obj[qq]
    if role != finalpool.roles_dict[cf.role_do] and obj.role != role:  # 身份检测
        await hunter.finish("未轮到你的回合")
    if num == 0 or num > len(cf.joiner):
        await hunter.send("对象不存在")
        return
    else:
        v_obj = list(cf.qq_obj.values())[num - 1]
        res = await obj.skill(v_obj)
        if res:     # 技能释放成功 检查死亡
            await check_die(cf)


@wolf_king.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    qq = event.get_user_id()
    role = "wolf_king"
    if qq not in finalpool.member_group:
        await wolf_king.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    try:
        num = int(str(arg))
    except ValueError:
        await wolf_king.finish("指令输入错误,请重试")
        return
    obj = cf.qq_obj[qq]
    if role != finalpool.roles_dict[cf.role_do] and obj.role != role:  # 身份检测
        await wolf_king.finish("未轮到你的回合")
    if num == 0 or num > len(cf.joiner):
        await wolf_king.send("对象不存在")
        return
    else:
        v_obj = list(cf.qq_obj.values())[num - 1]
        res = await obj.bring(v_obj)
        if res:
            await check_die(cf)


@nvwu.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    qq = event.get_user_id()
    role = "nvwu"
    if qq not in finalpool.member_group:
        await nvwu.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    try:
        num = int(str(arg))
    except ValueError:
        await nvwu.finish("指令输入错误,请重试")
        return
    obj = cf.qq_obj[qq]
    if role != finalpool.roles_dict[cf.role_do] and obj.role != role:  # 身份检测
        await nvwu.finish("未轮到你的回合")
    if num == 0 or num > len(cf.joiner):
        await nvwu.send("对象不存在")
        return
    else:
        v_obj = list(cf.qq_obj.values())[num - 1]
        res = await obj.save_man(v_obj)
    if res:  # 技能释放成功 继续夜晚流程
        cf.maybe_die.remove(v_obj)
        await game_night(cf)


@wolf_bai.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    qq = event.get_user_id()
    role = "wolf_bai"
    if qq not in finalpool.member_group:
        await wolf_bai.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    try:
        num = int(str(arg))
    except ValueError:
        await wolf_bai.finish("指令输入错误,请重试")
        return
    obj = cf.qq_obj[qq]
    if role != finalpool.roles_dict[cf.role_do] and obj.role != role:  # 身份检测
        await wolf_bai.finish("未轮到你的回合")
    if num == 0 or num > len(cf.joiner):
        await wolf_bai.send("对象不存在")
        return
    else:
        v_obj = list(cf.qq_obj.values())[num - 1]
        res = await obj.boom(v_obj)
    if res:     # 技能释放成功 死亡检查
        await check_die(cf)


@pass_do.handle()
async def skip_do(event: MessageEvent):
    qq = event.get_user_id()
    if qq not in finalpool.member_group:
        await wolf_bai.finish("未参加游戏")
    group = finalpool.member_group[qq]
    cf = finalpool.configs[group]
    obj = cf.qq_obj[qq]
    if obj.role != finalpool.roles_dict[cf.role_do]:  # 身份检测
        await pass_do.finish("未轮到你的回合")
    await obj.private_say("跳过回合成功")
    if cf.night:     # 继续流程
        await game_night(cf)
    else:
        await game_morning(cf)
