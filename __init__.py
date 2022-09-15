from nonebot.adapters.onebot.v11 import Bot, Event, Message
from .info import get_says, get_role_info, mode_choose
from .utils import group_card, ban_say, unban_say, private_say, send_gm
import random
from nonebot.plugin import on_command
from nonebot.exception import ActionFailed
import asyncio

create_game = {}
group_dist = {}  # 参加人员
game_mode = {}  # 游戏是否开始
# 时间线:夜晚 - (竞选) - 宣布死亡(是否结束)(猎人) - 白天发言(自爆) - 投票 - (决斗) - 放逐(是否结束) - 黑夜
game_roles = {}  # qq:角色
roles_gamer = {}  # 翻转成 角色-玩家 qq-职业
wolf_no_get_skill = {}
roles_do = {}  # 角色行动 1-守卫 2-摄梦 3-乌鸦  4-狼人 5-预言家 6-女巫 7-骑士 8-hunter 9-狼王
who_say = {}  # 轮次发言
police = {}  # 警长
roles_dict_has = {}
skill_effect = {}  # 每个人的身上效果
maybe_die = {}  # 假死状态
die_man = {}  # 死人
nvwu_yao = {}
today = {}  # 第几天
night = {}  # 时间 0-黑夜 1-白天
vote_list = {}  # 票数列表 qq:[是否投过,得到票数]
ban_mode = {}  # 禁言模式
roles_dict = {
    0: "NULL",
    1: "shouwei",
    2: "shemeng",
    3: "wuya",
    4: "wolf",
    5: "yuyan",
    6: "nvwu",
    7: "qishi",
    8: "hunter",
    9: "wolf_king"
}
translate = {
    "shouwei": "守卫",
    "shemeng": "摄梦者",
    "wuya": "乌鸦",
    "wolf": "狼人",
    "yuyan": "预言家",
    "nvwu": "女巫",
    "qishi": "骑士",
    "hunter": "猎人",
    "wolf_king": "狼王",
    "wolf_bai": "白狼王",
    "wolf_no": "隐狼",
    "baichi": "白痴",
    "people": "平民",
}

zd = on_command("/自定义")
@zd.handle()
async def zdy(bot: Bot, event: Event):
    global create_game
    try:
        command = "/自定义"
        group = event.get_session_id().split('_')[1]
        args = str(event.get_message()).split()
        if command in args:
            args.remove(command)
        ivd = {v: k for k, v in translate.items()}
        rl = args[4:]
        ll = []
        for i in rl:
            ll.append(ivd[i])
        args[4:] = ll
        for i in range(0, 4):
            args[i] = int(args[i])
        num_wolf = int(args[1])
        for i in args[4:]:
            if "wolf_" in i:
                num_wolf -= 1
        if num_wolf > 0:
            args.append("wolf")
        if "people" not in args:
            args.append("people")

        if "people" not in create_game[group] or "wolf" not in create_game[group]:
            await zd.send(message=f"参数错误,people 和 wolf 至少一个,当前参数为:\n{str(create_game[group])}")
        else:
            if group in create_game:
                create_game[group] = args
            else:
                create_game.setdefault(group, args)
            await zd.send(message=f"自定义成功 + {str(create_game[group])}")

    except:
        res = "当前能用的角色有:"
        for i in translate:
            res += f"{translate[i]} "
        await zd.send(message="自定义失败,请参考:/自定义 神数 狼数 平明数 有无警 身份...\neg:/自定义 3 3 3 0 平民 狼人 预言家 白狼王 女巫 猎人（平民，狼人，神至少要有一个！）\n"\
                              "定义一个3神3狼3人无警长,技能有 预言家 白狼王 女巫 猎人\n" + res)


bm = on_command("/禁言模式")  # 非发言时禁言
@bm.handle()
async def set_ban(bot: Bot, event: Event):
    global ban_mode
    group = event.get_session_id().split('_')[1]
    ban_mode.setdefault(group, 0)
    args = str(event.get_message()).split()
    command = "/禁言模式"
    if command in args:
        args.remove(command)
    if args[0] == "开":
        ban_mode[group] = 1
    else:
        ban_mode[group] = 0
    await bm.send(message="right!")


yy = on_command("/参加狼人杀")  # 参加
@yy.handle()
async def attend_game(bot: Bot, event: Event):
    global group_dist, game_mode, ban_mode
    try:
        group = event.get_session_id().split('_')[1]
    except IndexError:
        await yy.send(message="请在群聊使用")
        return
    group_dist.setdefault(group, [])
    ban_mode.setdefault(group, 0)  # 禁言模式默认关
    # 参加检测
    l = group_dist[group].copy()
    game_mode.setdefault(group, 0)
    res = "error"
    if group not in create_game:
        if len(l) == 12:
            res = get_says('num_big')  # 人数已满
            await yy.send(message=res)
            return
    else:
        max_p = int(create_game[group][0]) + int(create_game[group][1]) + int(create_game[group][2])
        if len(l) == max_p:
            res = get_says('num_big')  # 人数已满
            await yy.send(message=res)
            return

    if game_mode[group] != 0:
        res = "参加失败,游戏已经开始."
        await yy.send(message=res)
        return
    else:
        qq = event.get_user_id()
        l.append(qq)
        for key in group_dist.keys():
            if qq in group_dist[key]:
                res = "你已经参加过了或在别处参加过了"
                await yy.send(message=res)
                l.remove(qq)
                return
        group_dist[group] = l
        res = f'参加成功, 已参加{len(l)}人.'
    await yy.send(message=res)


qk = on_command("/结束游戏")  # 手动结束
@qk.handle()
async def stop_game(bot: Bot, event: Event):
    global group_dist
    group = event.get_session_id().split('_')[1]
    await game_over(bot, group)
    await qk.send(message=f'清空成功.')


rs = on_command("/重新开始")  # 删除游戏残留,保留参赛人员,重新开始
@rs.handle()
async def restart_game(bot: Bot, event: Event):
    try:
        group = event.get_session_id().split('_')[1]
    except IndexError:
        await rs.send(message="请在群聊重试")
        return
    if group not in group_dist:
        await rs.send(message="进程不存在,请重新参赛.")
        return
    if group in game_mode:
        del game_mode[group]
    if group in game_roles:
        del game_roles[group]
    if group in roles_dict_has:
        del roles_dict_has[group]
    if group in roles_gamer:
        del roles_gamer[group]
    if group in roles_do:
        del roles_do[group]
    if group in who_say:
        del who_say[group]
    if group in police:
        del police[group]
    if group in night:
        del night[group]
    if group in today:
        del today[group]
    if group in wolf_no_get_skill:
        del wolf_no_get_skill[group]

    await rs.send(message="正在重开")
    await game_main(bot, group)


ks = on_command("/开始游戏")  # 进入游戏线程
@ks.handle()
async def start_gmae(bot: Bot, event: Event):
    group = event.get_session_id().split('_')[1]
    l = group_dist[group]
    n = len(l)
    res = "error"
    if n == 4:
        res = "开始成功,已为你开启游戏线程"
        await ks.send(message=res)
        await game_main(bot, group)
        # 改名-号数
        res += ".改名成功"
        for i in range(0, len(l)):
            try:
                qq = l[i]
                await group_card(bot, group, qq, str(i + 1) + "号")
            except ActionFailed:
                await send_gm(bot, group, "权限不足.无法改名")
    if group not in create_game:
        if n < 6:
            res = get_says('num_small')
            await ks.send(message=res)
            return
    else:
        max_p = int(create_game[group][0]) + int(create_game[group][1]) + int(create_game[group][2])
        if n != max_p:
            await ks.send(message=f"人数不足{str(max_p)}人, 无法开始")
            return
    if group in game_mode and game_mode[group] == 1:
        res = "游戏进程已存在,游戏正在进行中."
        await ks.send(message=res)
    else:
        res = "开始成功,已为你开启游戏线程"
        await ks.send(message=res)
        await game_main(bot, group)
        # 改名-号数
        for i in range(0, n):
            try:
                qq = l[i]
                await group_card(bot, group, qq, str(i + 1) + "号")
            except ActionFailed:
                await send_gm(bot, group, "权限不足.无法改名")


gd = on_command("/获取进度")  # 进入游戏线程
@gd.handle()
async def get_doing(bot: Bot, event: Event):
    qq = event.get_user_id()
    group = 0
    try:
        group = event.get_session_id().split('_')[1]
    except IndexError:
        for k, v in group_dist.items():
            if qq in v:
                group = k
    if group == 0:
        await gd.send(message="未参加游戏")
        return
    num = roles_do[group]
    role = translate[roles_dict[num]]
    await gd.send(message=f"现在已经轮到了{role}的回合")


# 开始游戏初始化 (角色分配, 轮次确定
async def game_main(bot: Bot, group):
    global game_roles, roles_gamer, roles_dict_has, police, today, night, game_mode, wolf_no_get_skill
    wolf_no_get_skill.setdefault(group, False)
    night.setdefault(group, 0)
    today.setdefault(group, 0)
    # 分身份-私聊身份-开始流程
    res = get_says('star')
    await send_gm(bot, group, res)

    l = group_dist[group].copy()  # 参加人员
    lt = group_dist[group]
    num = len(l)
    if ban_mode[group] == 1:
        for ban_qq in l:
            try:
                await ban_say(bot, group, ban_qq)  # 禁言
            except ActionFailed:
                await send_gm(bot, group, "权限不足")

    if group not in create_game:
        [num_shen, num_wolf_all, num_people, has_p], s = mode_choose(num)
    else:
        num_shen, num_wolf_all, num_people, has_p, s = int(create_game[group][0]), int(create_game[group][1]), int(create_game[group][2]), int(create_game[group][3]), create_game[group][4:]
    has_police = {}
    if has_p == 1:  # 添加警长流程
        has_police.setdefault("has_police", 1)
    else:
        has_police.setdefault("has_police", 0)
    police.setdefault(group, has_police)
    # 轮次排序
    px = []
    if "shouwei" in s:
        px.append("shouwei")
    if "shemeng" in s:
        px.append("shemeng")
    if "wuya" in s:
        px.append("wuya")
    if "wolf" in s:
        px.append("wolf")
    if "yuyan" in s:
        px.append("yuyan")
    if "nvwu" in s:
        px.append("nvwu")
    if "qishi" in s:
        px.append("qishi")
    roles_dict_has.setdefault(group, px)

    try:
        wolf_k = 0
        game_roles.setdefault(group, {})
        d = {}
        for i in range(0, num_people):  # 多平民
            x = random.randint(0, len(l) - 1)
            d.setdefault(l[x], 'people')
            del l[x]

        s.remove('people')
        s.remove('wolf')
        for role in s:  # 技能身份只有一个
            if 'wolf' in role:
                wolf_k += 1
            x = random.randint(0, len(l) - 1)
            d.setdefault(l[x], role)
            del l[x]

        for i in range(0, num_wolf_all - wolf_k):  # 多狼
            x = random.randint(0, len(l) - 1)
            d.setdefault(l[x], 'wolf')
            del l[x]
        game_roles[group] = d  # 存储角色信息
    except:
        await send_gm(bot, group, "失败,参数配置错误")
        await game_over(bot, group)
        return

    res = "本局的技能身份有:"
    for s_i in s:
        res += f"{translate[s_i]},"
    res += f"一共{num_shen}个神人,{num_wolf_all}个狼人,{num_people}个平民."
    await send_gm(bot, group, res)

    roles_gamer.setdefault(group, {})
    b = {}
    # await ks.send(message=str(d))
    for k, v in d.items():  # 字典翻转
        if v in b.keys():
            b[v].append(k)
        else:
            b.setdefault(v, [k])
    roles_gamer[group] = b

    # 私聊身分
    res_night = get_says('night')
    not_add = []
    for qq in lt:
        res = get_role_info(d[qq])
        for k in roles_gamer[group].keys():
            if qq in roles_gamer[group][k] and "wolf" in k:
                for key in roles_gamer[group].keys():  # 狼队友
                    if "wolf" in key:
                        if key != "wolf_no":
                            res += str(roles_gamer[group][key])
        try:
            await private_say(bot, qq, group, res)
        except ActionFailed:
            not_add.append(qq)
            await asyncio.sleep(1)
        res_night = res_night + f"\n{str(lt.index(qq)+1)}号:[CQ:at,qq={qq}]"

    if not_add:
        await send_gm(bot, group, "警告：以下成员未添加好友,发消息有概率失败,封号概率上升！" + str(not_add))
    game_mode[group] = 1
    # 开始夜晚流程
    await send_gm(bot, group, res_night)
    await game_night(bot, group)


# 夜晚轮次流程
async def game_night(bot: Bot, group):
    global roles_do, skill_effect, roles_dict_has, maybe_die, night, nvwu_yao, die_man
    night.setdefault(group, 0)
    skill_effect.setdefault(group, {})  # 初始化
    maybe_die.setdefault(group, [])
    roles_do.setdefault(group, 0)
    nvwu_yao.setdefault(group, [1, 1])
    die_man.setdefault(group, [])
    l = group_dist[group]
    if skill_effect[group] == {}:
        d = {}
        for q_i in l:
            d.setdefault(q_i, [])
        skill_effect[group] = d

    who_do = roles_do[group]
    if who_do == 6:
        await check_die(bot, group)  # 夜晚轮次结束, 进入检查死亡流程
        return
    else:
        who_do += 1
    roles_do[group] = who_do

    has_roles = roles_dict_has[group]  # 获取轮次
    if ("nvwu" in has_roles) and nvwu_yao[group][0] == 0 and nvwu_yao[group][1] == 0:  # 药用完了.除去女巫轮次
        has_roles.remove("nvwu")
        roles_dict_has[group] = has_roles

    zhiye = roles_dict[who_do]  # 本局若不存在该角色,轮空
    if zhiye not in has_roles:
        await game_night(bot, group)
        return

    if zhiye != "NULL":
        skiller_dict = roles_gamer[group].keys()
        qq = roles_gamer[group][zhiye].copy()
        if zhiye == "wolf":
            if "wolf_bai" in skiller_dict:
                qq.append(roles_gamer[group]["wolf_bai"][0])
            if "wolf_king" in skiller_dict:
                qq.append(roles_gamer[group]["wolf_king"][0])
            if "wolf_no" in skiller_dict and wolf_no_get_skill[group]:
                qq.append(roles_gamer[group]["wolf_no"][0])

        nvwu_yao.setdefault(group, [1, 1])  # 女巫救人回合 毒药 解药
        if maybe_die[group] != [] and nvwu_yao[group][1] != 0 and who_do == 6:
            say = str(maybe_die[group]) + "已死亡, 回复 /救 号数 或不使用技能"
            try:
                await private_say(bot, qq[0], group, say)
            except ActionFailed:
                await asyncio.sleep(1)

        say = f"(轮到{translate[zhiye]}的回合,请私聊使用)!{get_says(zhiye)})"
        for q_i in qq:  # 私发轮次信息
            try:
                await private_say(bot, q_i, group, say)
            except ActionFailed:
                await asyncio.sleep(1)


# (竞选警长先) - 杀死并宣布死亡 -
async def check_die(bot: Bot, group):  # 前夕:进入白天-(警长流程)-彻底杀死 - 开启白天流程 - 待完成
    global night, roles_do, who_say, today
    who_say.setdefault(group, 0)
    die_men = maybe_die[group]
    del maybe_die[group]    # 过夜清除
    die_say = 0
    res = ""
    if police[group]["has_police"] == 1 and today[group] == 0 and "police" not in police[group]:  # 第一天, 进入警长流程
        await send_gm(bot, group, "第一天,开始竞选警长,轮流发言后投票")
        who_say[group] = 0
        await game_morning(bot, group)  # 发言流程
        return

    if not die_men:
        res = "昨晚是平安夜~~~"
    else:
        for die_man in die_men:
            die_say = await kill(bot, group, die_man)  # 杀死

    # 如果游戏未结束
    if group in group_dist:
        if night[group] == 0:  # 进入白天
            night[group] = 1
            today[group] += 1

        who_say[group] = 0
        if die_say == 0:  # 无遗言直接天亮
            res += f"天亮了,今天是第{str(today[group])}天.进入白天轮流发言"
            await send_gm(bot, group, res)
            await game_morning(bot, group)  # 否则进入白天发言流程


# 返回有无遗言
async def kill(bot: Bot, group, who: str):  # 销毁死人:号数 (猎人,狼王检测)-  删除职业轮次 - 检查游戏是否结束 - 发遗言 -未完成
    global roles_dict_has, die_man, roles_gamer, roles_do
    num = int(who) - 1  # 获取信息
    qq_list = group_dist[group]
    qq = qq_list[num]
    role = game_roles[group][qq]
    die_say = 0
    if role in roles_dict_has[group] and role != "wolf":  # 删轮次
        roles_dict_has[group].remove(role)

    if role == "hunter":  # 开启亡语检测
        roles_do[group] = 8
        try:
            await private_say(bot, qq, group, get_says("hunter"))
        except ActionFailed:
            await asyncio.sleep(1)

    if role == "wolf_king":
        roles_do[group] = 9
        try:
            await private_say(bot, qq, group, get_says("wolf_king"))
        except ActionFailed:
            await asyncio.sleep(1)

    res = f"{str(who)}号已死亡."
    await send_gm(bot, group, res)

    roles_gamer_list = roles_gamer[group]  # 删除 职业-玩家
    for k in list(roles_gamer_list.keys()):
        if qq in roles_gamer_list[k]:
            roles_gamer[group][k].remove(qq)
        if not roles_gamer[group][k] and k != "wolf":
            del roles_gamer[group][k]

    whether_over_game = await check_game_over(bot, group)  # 检查游戏是否结束
    if whether_over_game == 1:
        await game_over(bot, group)
        return

    if (today[group] <= 1) or (night[group] == 1):  # 第一晚死或者白天死有遗言
        await say_min(bot, group, qq)  # 发遗言
        die_say = 1

    # 保存死人
    die_man[group].append(qq)
    return die_say


async def check_game_over(bot: Bot, group):
    global wolf_no_get_skill
    roles_gamer_list = roles_gamer[group]
    res = "继续游戏"
    if "people" not in roles_gamer_list:  # 判定游戏结束
        res = "游戏结束,平民死完,狼人胜利!"
        whether_over_game = 1
        await send_gm(bot, group, res)
        return whether_over_game

    key_ls = roles_gamer_list.keys()  # 此时还存在的职业
    whether_over = 1
    for key in key_ls:
        if "wolf_" in key:
            whether_over = 0
            break
        if key == "wolf" and roles_gamer_list[key]:
            whether_over = 0
            break

    if whether_over == 1:
        res = "游戏结束,狼人死完,好人胜利!"
        whether_over_game = 1
        await send_gm(bot, group, res)
        return whether_over_game

    whether_over = 1

    shen_has = roles_dict_has[group].copy()
    shen_has.remove("wolf")  # 本局的神
    for key in key_ls:
        if key in shen_has:
            whether_over = 0
            break
    if whether_over == 1:
        res = "游戏结束,神人死完,狼人胜利!"
        whether_over_game = 1
        await send_gm(bot, group, res)
        return whether_over_game

    if not roles_gamer_list["wolf"] and "wolf_no" in key_ls:  # 隐狼觉醒
        wolf_no_get_skill[group] = True

    await send_gm(bot, group, res)
    return 0


async def game_over(bot: Bot, group):
    await send_gm(bot, group, "正在结束进程")
    # 解除禁言
    if ban_mode[group] == 1:
        qq_ls = group_dist[group]
        for qq in qq_ls:
            try:
                await unban_say(bot, group, qq)  # jie言
            except ActionFailed:
                await send_gm(bot, group, "禁言权限不足")
    try:
        # 清除数据 - 必有的
        if group in create_game:
            del create_game[group]
        if group in game_mode:
            del game_mode[group]
        if group in game_roles:
            del game_roles[group]
        if group in roles_dict_has:
            del roles_dict_has[group]
        if group in roles_gamer:
            del roles_gamer[group]
        if group in roles_do:
            del roles_do[group]
        if group in who_say:
            del who_say[group]
        if group in police:
            del police[group]
        if group in night:
            del night[group]
        if group in today:
            del today[group]
        if group in wolf_no_get_skill:
            del wolf_no_get_skill[group]
        if group in group_dist:
            del group_dist[group]
        if group in maybe_die:
            del maybe_die[group]
        if group in die_man:
            del die_man[group]
        # 未必有的
        if group in skill_effect:
            del skill_effect[group]
        if group in nvwu_yao:
            del nvwu_yao[group]
    except:
        pass

async def say_min(bot: Bot, group, qq):  # 发言一分钟: (创造定时任务(可中断)(未完成)
    if ban_mode[group] == 1:
        try:
            await unban_say(bot, group, qq)  # jie言
        except ActionFailed:
            await send_gm(bot, group, "禁言权限不足")

    num = "error"
    for i in range(0, len(group_dist[group])):
        if qq == group_dist[group][i]:
            num = str(i + 1)

    await send_gm(bot, group, Message(f"有请{num}号[CQ:at,qq={qq}]发言,结束发言回复 /过"))


# 白天轮流发言
async def game_morning(bot: Bot, group):
    global who_say, roles_do
    num = who_say[group]
    qq_ls = group_dist[group]
    if num == len(qq_ls):  # 超出范围,警长发言(×) -骑士行动 -进入投票- 待完成
        if "qishi" in roles_gamer[group] and roles_do[group] == 6:  # 发言结束,骑士行动先
            roles_do[group] = 7
            qq = roles_gamer[group]["qishi"][0]
            await send_gm(bot, group, "发言结束,等待骑士行动")
            try:
                await private_say(bot, qq, group, get_says("qishi"))
            except ActionFailed:
                pass
            return
        else:
            who_say[group] += 1  # 可能有遗言
            await send_gm(bot, group, "发言结束,进入投票环节")
        await vote_private(bot, group)
        return
        # 获取发言人信息
    qq = qq_ls[num]
    num += 1
    who_say[group] = num
    if qq in die_man[group]:  # 死人跳过发言
        await game_morning(bot, group)
        return
    else:
        await say_min(bot, group, qq)  # 发言


# 票数初始化
async def vote_private(bot: Bot, group):  # 私聊/群聊投票(死人跳过
    global vote_list
    vote_list.setdefault(group, {})
    qq_list = group_dist[group]
    v_d = {}
    for qq in qq_list:
        # 死人跳过
        if qq in die_man[group]:
            continue
        if game_roles[group][qq] == "baichi_real":
            v_d.setdefault(qq, [1, 0])
        else:
            v_d.setdefault(qq, [0, 0])
        if ban_mode[group] == 1:
            try:
                await unban_say(bot, group, qq)
            except ActionFailed:
                pass
    await send_gm(bot, group, get_says("vote"))
    vote_list[group] = v_d


# 投票是否完成
async def check_vote_finish(bot: Bot, group):
    global vote_list
    for k, v in vote_list[group].items():
        if v[0] == 0:  # 投票未完成
            return
    if police[group]["has_police"] == 1 and today[group] == 0 and "police" not in police[group]:  # 第一天, 获选警长
        v_ls = []
        for k, v in vote_list[group].items():
            v_ls.append(v[1])
        v_sort = v_ls.copy()
        v_sort.sort(reverse=True)
        if v_sort[0] != v_sort[1]:
            num = v_ls.index(max(v_ls))
            await send_gm(bot, group, f"{str(num + 1)}号获选警长, 警长一票顶两票")
            police[group]["police"] = group_dist[group][num]
        else:
            await send_gm(bot, group, "最大同票,本局无警长")
            police[group]["police"] = "null"
        # 结束.删除投票信息
        del vote_list[group]
        await check_die(bot, group)
        return

    if "wuya" in roles_dict_has[group]:  # 乌鸦诅咒检测
        qq_ls = group_dist[group]
        for qq in qq_ls:
            if qq in skill_effect[group] and "zuzhou" in skill_effect[group][qq]:
                vote_list[group][qq][1] += 1
    # 投票完成, 进入驱逐
    await quzhu(bot, group)


# 票数检测 -(白痴检测) - 杀死进入黑夜
async def quzhu(bot: Bot, group):  # 驱逐
    global night, roles_do, game_roles
    # 驱逐环节(投票最大-同票
    v_ls = []
    for k, v in vote_list[group].items():
        v_ls.append(v[1])
    v_sort = v_ls.copy()
    v_sort.sort(reverse=True)  # 排序
    die_say = 0
    if v_sort[0] != v_sort[1]:
        num = v_ls.index(max(v_ls))
        qq = group_dist[group][num]
        role = game_roles[group][qq]
        if role != "baichi":
            await send_gm(bot, group, f"驱逐{str(num + 1)}号成功")
            die_say = await kill(bot, group, str(num + 1))
        else:
            await send_gm(bot, group, f"{str(num + 1)}号是白痴哒!")
            await group_card(bot, group, qq, f"{str(num + 1)}号白痴!")
            game_roles[group][qq] = "baichi_real"
    else:
        if v_sort[0] != 0:
            await send_gm(bot, group, "最大同票,无人被驱逐")
        else:
            await send_gm(bot, group, "全员弃票,无人被驱逐")

    # 如果游戏未结束.删除投票信息
    if group in group_dist:
        del vote_list[group]
        if die_say == 0:  # 无遗言, 进入黑夜
            await send_gm(bot, group, "天黑请闭眼")
            del night[group]
            roles_do[group] = 0
            await game_night(bot, group)


# 只能在群聊投票
tou = on_command("/投")  # 投票


@tou.handle()
async def vote_to(bot: Bot, event: Event):
    global vote_list
    args = str(event.get_message()).split()
    command_str = "/投"  # 版本兼容
    whether_return = 0
    res = "error"
    num = 0
    group = 0
    qq = event.get_user_id()
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1

    try:
        group = event.get_session_id().split('_')[1]
    except IndexError:
        res = "请在群聊投票"
        whether_return = 1

    if group == 0:
        res = "未参加游戏"
        whether_return = 1
    elif night[group] == 0 and "police" in police[group]:
        res = "未到投票环节"
        whether_return = 1
    elif qq in die_man[group]:
        res = "你已经死亡"
        whether_return = 1
    elif vote_list[group][qq][0] == 1:
        res = "你已经投过了请勿重复投"
        whether_return = 1
    elif game_roles[group][qq] == "baichi_real":
        res = "明牌白痴不能投票哦!"
        whether_return = 1

    if whether_return == 1:
        try:
            await tou.send(message=res)
        except ActionFailed:
            pass
        return

    if ban_mode[group] == 1:
        try:
            await unban_say(bot, group, qq)
        except ActionFailed:
            pass

    # 加票
    try:
        if args[0] != "0" and num < len(group_dist[group]):
            voted_qq = group_dist[group][num]
            voted_list = vote_list[group][voted_qq]
            if "police" in police[group] and (qq == police[group]["police"]):
                voted_list[1] += 1  # 警长在家一票
            voted_list[1] += 1
            vote_list[group][voted_qq] = voted_list
            res = f"投{str(num + 1)}号成功"
        else:
            res = f"弃票成功"
        qq_list = vote_list[group][qq]
        qq_list[0] += 1
        vote_list[group][qq] = qq_list
    except:
        res = "投票失败请稍后重试"
    # 检测是否全投
    await tou.send(message=res)
    await check_vote_finish(bot, group)


guo = on_command("/过")  # 群聊结束发言 - 或结束遗言


@guo.handle()
async def skip_say(bot: Bot, event: Event):
    global group_dist, skill_effect, roles_do, roles_gamer
    whether_return = 0

    res = "error"
    group = "0"
    try:
        group = event.get_session_id().split('_')[1]
    except IndexError:
        res = "请在群聊用"
        whether_return = 1

    qq_ls = group_dist[group]
    his_qq = event.get_user_id()

    if his_qq not in qq_ls:
        res = "未参加游戏"
        whether_return = 1

    # 身份验证
    num = int(who_say[group]) - 1
    if who_say[group] != 0 and who_say[group] < len(qq_ls) and his_qq != qq_ls[num]:
        res = "爬!还没到你."
        whether_return = 1

    if whether_return == 1:
        await guo.send(message=res)
        return

    if ban_mode[group] == 1:
        try:
            await ban_say(bot, group, his_qq)  # 经言
        except ActionFailed:
            await send_gm(bot, group, "禁言权限不足")

    if who_say[group] == len(qq_ls) + 1:  # 遗言检测 , 白天死人(骑士决斗,白狼自爆)直接进入黑夜
        await send_gm(bot, group, "遗言结束,继续游戏.")
        roles_do[group] = 0
        await game_night(bot, group)
    else:
        await game_morning(bot, group)  # 下一位发言


shouwei = on_command("/守护")  # 守卫回合


@shouwei.handle()
async def guard(bot: Bot, event: Event):
    global skill_effect, roles_do, roles_gamer
    args = str(event.get_message()).split()
    command_str = "/守护"  # nonebot版本兼容
    whether_return = 0
    num = 0
    res = "error"
    if command_str in args:
        args.remove(command_str)

    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
        whether_return = 1
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do]:  # 不是他的轮次
            res = "未轮到你的回合"
            whether_return = 1
        qq_list = group_dist[group]
        obj = qq_list[num]  # 获取对象
        l = skill_effect[group][obj]  # 获取效果,防止连续
        if "shouhu" in l:
            res = "不可连续两次守护同一对象,请重试"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await shemeng.send(message=res)
            except ActionFailed:
                pass
            return

        await effect_clear(group, "shouhu")
        l.append("shouhu")  # 添加
        skill_effect[group][obj] = l
        await game_night(bot, group)
    try:
        await shouwei.send(message=res)
    except ActionFailed:
        pass


shemeng = on_command("/摄梦")  # 摄梦回合


@shemeng.handle()
async def dreaming(bot: Bot, event: Event):
    global skill_effect, roles_do, maybe_die
    args = str(event.get_message()).split()
    command_str = "/摄梦"  # 版本兼容
    whether_return = 0
    res = "error"
    num = 0
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do]:
            res = "未轮到你的回合"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await shemeng.send(message=res)
            except ActionFailed:
                pass
            return

        qq_list = group_dist[group]
        obj = qq_list[num]  # 获取对象

        l = skill_effect[group][obj]
        # 获取效果,连续则击杀
        if "shemeng" in l:
            maybe_die[group].append(args[0])
            res = "击杀成功"
        else:
            await effect_clear(group, "shemeng")  # 先移除
            l.append("shemeng")  # 添加
            skill_effect[group][obj] = l
            res = "已添加摄梦状态,对方免疫伤害,自己死亡对方也死亡,连续两晚摄梦对方死亡!"
        await game_night(bot, group)
    try:
        await shemeng.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


wuya = on_command("/诅咒")  # 乌鸦回合


@wuya.handle()
async def curse(bot: Bot, event: Event):
    global skill_effect, roles_do
    args = str(event.get_message()).split()
    command_str = "/诅咒"  # 版本兼容
    whether_return = 0
    num = 0
    res = "error"
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do]:
            res = "未轮到你的回合"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await wuya.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        qq_list = group_dist[group]
        obj = qq_list[num]  # 获取对象
        l = skill_effect[group][obj]  # 获取对象身上效果
        await effect_clear(group, "zuzhou")
        l.append("zuzhou")  # 添加
        skill_effect[group][obj] = l
        res = "已添加诅咒,对方被投票加1."
        await game_night(bot, group)
    try:
        await wuya.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


wolf = on_command("/刀")  # 狼人回合


@wolf.handle()
async def wolf_kill(bot: Bot, event: Event):
    global skill_effect, roles_do, maybe_die
    args = str(event.get_message()).split()
    command_str = "/刀"  # 版本兼容
    num = 0
    whether_return = 0
    res = "error"
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1

    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do] and "wolf_" not in game_roles[group][qq]:
            res = "未轮到你的回合"
            whether_return = 1
        if "wolf_no" == game_roles[group][qq] and not wolf_no_get_skill[group]:
            res = "技能未觉醒"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await wolf.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        qq_list = group_dist[group]
        obj = qq_list[num]  # 获取对象
        l = skill_effect[group][obj]  # 获取效果,无异常则击杀
        if ("shouhu" not in l) and ("shemeng" not in l):
            maybe_die[group].append(args[0])
        res = "yes sir!正在提刀的路上."
        await game_night(bot, group)
    try:
        await wolf.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


qishi = on_command("/决斗")  # 骑士回合


@qishi.handle()
async def fight(bot: Bot, event: Event):
    global roles_do
    args = str(event.get_message()).split()
    command_str = "/决斗"  # 版本兼容
    num = 0
    whether_return = 0
    res = "error"
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do] or night[group] == 0:
            res = "未轮到你的回合"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await qishi.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        qq_list = group_dist[group]
        obj = qq_list[num]  # 获取对象
        if "wolf" in game_roles[group][obj]:
            res = "他是个坏人!成功击杀."
            await kill(bot, group, str(num + 1))  # 杀死 - 进入天黑

            roles_do[group] = 0
        else:
            res = "他是个好人!你已死亡!"
            await kill(bot, group, qq_list.index(qq) + 1)
            await game_morning(bot, group)
    await send_gm(bot, group, "骑士发动技能,进入天黑.")
    try:
        await qishi.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


hunter = on_command("/枪")  # 猎人回合


@hunter.handle()
async def shoot(bot: Bot, event: Event):
    args = str(event.get_message()).split()
    command_str = "/枪"  # 版本兼容
    num = 0
    whether_return = 0
    res = "error"
    if command_str in args:
        args.remove(command_str)
    if args[0] == "0":  # 不使用
        return
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1

    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do]:
            res = "未轮到你的回合"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await hunter.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        roles_do[group] = 0
        await kill(bot, group, str(num + 1))
        res = "直接击杀."
    try:
        await hunter.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


wolf_king = on_command("/杀")  # 狼王回合


@wolf_king.handle()
async def die_sk(bot: Bot, event: Event):
    args = str(event.get_message()).split()
    command_str = "/杀"  # 版本兼容
    num = 0
    res = "error"
    whether_return = 0
    if command_str in args:
        args.remove(command_str)
    if args[0] == "0":  # 不使用
        try:
            await wolf_king.send(message="跳过回合.")
        except ActionFailed:
            await asyncio.sleep(1)
        return

    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试."
        whether_return = 1
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏."
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do]:
            res = "未轮到你的回合."
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await wolf_king.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return
        roles_do[group] = 0
        await kill(bot, group, str(num + 1))
        res = "直接击杀."
    try:
        await wolf_king.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


yuyan = on_command("/查")  # 预言家回合


@yuyan.handle()
async def inquire(bot: Bot, event: Event):
    global skill_effect, roles_do
    args = str(event.get_message()).split()
    command_str = "/查"  # 版本兼容
    num = 0
    res = "error"
    whether_return = 0
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重shu"
        whether_return = 1

    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
        whether_return = 1
    else:
        who_do = roles_do[group]  # 身份验证
        if game_roles[group][qq] != roles_dict[who_do]:
            res = "未轮到你的回合"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await yuyan.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        qq_list = group_dist[group]
        obj = qq_list[num]  # 获取对象信息
        what_role = game_roles[group][obj]
        if "wolf" in what_role and what_role != "wolf_no":
            res = "我的天哪,这是个bad guy!"
        else:
            res = "我想这个应该是个好人."
        await game_night(bot, group)
    try:
        await yuyan.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


nvwu = on_command("/毒")  # 女巫回合（毒


@nvwu.handle()
async def poison(bot: Bot, event: Event):
    global skill_effect, roles_do, nvwu_yao
    args = str(event.get_message()).split()
    command_str = "/毒"  # 版本兼容
    num = 0
    res = "error"
    whether_return = 0
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1

    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]
        if game_roles[group][qq] != roles_dict[who_do] or nvwu_yao[group][0] == 0:
            res = "未轮到你的回合或药已用完"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:  # return检测
            try:
                await nvwu.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        maybe_die[group].append(args[0])
        nvwu_yao[group][0] = 0
        await game_night(bot, group)
    try:
        await nvwu.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)


nvwu_jiu = on_command("/救")  # 女巫回合（救


@nvwu_jiu.handle()
async def cure(bot: Bot, event: Event):
    global skill_effect, roles_do, nvwu_yao
    args = str(event.get_message()).split()
    res = "error"
    whether_return = 0
    command_str = "/救"  # 版本兼容
    if command_str in args:
        args.remove(command_str)
    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]
        if game_roles[group][qq] != roles_dict[who_do] or maybe_die[group] == [] or nvwu_yao[group][1] == 0:
            res = "未轮到你的回合"
            whether_return = 1
        if whether_return == 1:
            try:
                await nvwu.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        die_l = maybe_die[group]  # 救人
        if args[0] in die_l:
            die_l.remove(args[0])
            res = "解救成功"
            nvwu_yao[group][1] = 0
            await game_night(bot, group)
        else:
            res = "号数不在死亡列表内,请重试"
        maybe_die[group] = die_l
    try:
        await nvwu.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)
    return


wolf_bai = on_command("/自爆")


@wolf_bai.handle()
async def boom(bot: Bot, event: Event):
    args = str(event.get_message()).split()
    command_str = "/自爆"  # 版本兼容
    num = 0
    res = "error"
    whether_return = 0
    if command_str in args:
        args.remove(command_str)
    if args[0] == "0":  # 不使用
        res = "0?哪里有0!"
        whether_return = 1

    try:
        num = int(args[0]) - 1
    except ValueError:
        res = "指令输入错误,请重试"
        whether_return = 1
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        if night[group] == 0:
            res = "未轮到你的回合(还没有到白天)"
            whether_return = 1
        # 身份检测
        your_role = game_roles[group][qq]
        if your_role != "wolf_bai":
            res = "与你角色不符合"
            whether_return = 1
        # 范围判定
        if num < 0 or num >= len(group_dist[group]):
            res = "对象不存在"
            whether_return = 1
        if whether_return == 1:
            try:
                await wolf_bai.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return
        await kill(bot, group, str(num + 1))
        await kill(bot, group, str(group_dist[group].index(qq) + 1))
        res = "成功自爆!"
    try:
        await wolf_bai.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)
    return


# 跳过轮次
pass_do = on_command("/不使用技能")


@pass_do.handle()
async def skip_do(bot: Bot, event: Event):
    global skill_effect, roles_do
    res = "error"
    whether_return = 0
    group = 0
    qq = event.get_user_id()  # 通过qq获取群号
    for k, v in group_dist.items():
        if qq in v:
            group = k
    if group == 0:
        res = "未参加游戏"
    else:
        who_do = roles_do[group]  # 身分判定
        your_role = game_roles[group][qq]
        if "wolf" in your_role:
            your_role = "wolf"
        doing_role = roles_dict[who_do]
        if your_role != doing_role:
            res = "未轮到你的回合"
            whether_return = 1
        if whether_return == 1:
            try:
                await pass_do.send(message=res)
            except ActionFailed:
                await asyncio.sleep(1)
            return

        res = "跳过回合成功"
        if your_role == "qishi":  # 继续白天
            await game_morning(bot, group)
        else:  # 继续黑夜
            await game_night(bot, group)
    try:
        await pass_do.send(message=res)
    except ActionFailed:
        await asyncio.sleep(1)
    return


async def effect_clear(group, effect_remove):  # 清除场上存在的某种效果
    global skill_effect
    qq_list = group_dist[group]
    for q_i in qq_list:  # 先移除效果
        effect = skill_effect[group][q_i]
        if effect_remove in effect:
            effect.remove(effect_remove)
            skill_effect[group][q_i] = effect
