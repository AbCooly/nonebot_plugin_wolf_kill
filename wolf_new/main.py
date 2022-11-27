# 流程处理
import random
from .info import get_says, mode_choose
from .utils import send_gm, friend_list
from .roles.man import People, Man
from .roles.god import Nvwu, Shemeng, Shouwei, Qishi, Baichi, Hunter, Wuya, Yuyan
from .roles.wolf import Wolf, Wolf_no, Wolf_bai, Wolf_king
from .config import Config, finalpool


async def game_main(cf: Config):
    group = cf.group
    l = cf.joiner  # 参加人员qq

    # 分配身份
    if cf.zdy:
        c_l = cf.create_game
        num_shen, num_wolf_all, num_people, s = c_l[0], c_l[1], c_l[2], c_l[3:]
    else:
        [num_shen, num_wolf_all, num_people], s = mode_choose(len(l))

    if "shouwei" in s:
        cf.roles_dict_have.append("shouwei")
    if "shemeng" in s:
        cf.roles_dict_have.append("shemeng")
    if "wuya" in s:
        cf.roles_dict_have.append("wuya")
    if "wolf" in s:
        cf.roles_dict_have.append("wolf")
    if "yuyan" in s:
        cf.roles_dict_have.append("yuyan")
    if "nvwu" in s:
        cf.roles_dict_have.append("nvwu")
    if "qishi" in s:
        cf.roles_dict_have.append("qishi")
    if "hunter" in s:
        cf.roles_dict_have.append("hunter")
    if "baichi" in s:
        cf.roles_dict_have.append("baichi")

    lc = l.copy()
    q_obj = {}
    try:
        # 随机分配
        wolf_k = 0
        cf.role_qq.setdefault("people", [])
        people = cf.role_qq["people"]
        for i in range(0, num_people):  # 分配平民
            x = random.randint(0, len(lc) - 1)
            qq = lc[x]
            q_obj.setdefault(qq, People(lc[x], i+1, cf))    # 创建对象
            people.append(qq)
            del lc[x]
        s.remove('people')

        if "wolf" in s:
            s.remove('wolf')
        for role in s:  # 技能身份只有一个
            if 'wolf' in role:
                wolf_k += 1
            x = random.randint(0, len(lc) - 1)
            qq = lc[x]
            num = len(q_obj) + 1
            q_obj.setdefault(qq, eval(finalpool.obj[role]))
            cf.role_qq.setdefault(role, [qq])
            del lc[x]

        cf.role_qq.setdefault("wolf", [])
        wolf = cf.role_qq["wolf"]
        for i in range(0, num_wolf_all - wolf_k):  # 分配狼
            x = random.randint(0, len(lc) - 1)
            num = len(q_obj) + 1
            qq = lc[x]
            q_obj.setdefault(qq, Wolf(lc[x], num, cf))
            wolf.append(qq)
            del lc[x]
    except:
        await send_gm(cf.bot, group, "失败,参数配置错误")

    # 随机打乱
    lll = l.copy()
    for i in range(0, len(lll)):
        x = random.randint(0, len(lll) - 1)
        num = i+1
        qq = lll[x]
        del lll[x]
        q_obj[qq].number = num
        cf.qq_obj.setdefault(qq, q_obj[qq])

    res = "本局的技能身份有:"
    for s_i in s:
        res += f"{finalpool.translate[s_i]},"
    res += f"一共{num_shen}个神人,{num_wolf_all}个狼人,{num_people}个平民."
    await send_gm(cf.bot, group, res)
    res_night = ""
    not_add = []
    friends = await friend_list(cf.bot)
    for o in list(cf.qq_obj.values()):
        await o.say_info()      # 私聊身分 改名
        if int(o.qq) not in friends:  # 是否为好友
            not_add.append(o.qq)
        res_night = res_night + f"\n{str(o.number)}号:[CQ:at,qq={o.qq}]"

    if not_add:
        res_night += "\n以下成员未添加好友,发消息有概率失败,封号概率上升！" + str(not_add)

    await send_gm(cf.bot, group, res_night)
    # 开始夜晚流程
    cf.game_start = True
    await to_night(cf)


async def to_night(cf: Config):
    cf.night = True
    cf.role_do = 0
    cf.time = 0
    await sleep_all(cf)  # 清除状态
    await send_gm(cf.bot, cf.group, "天黑请闭眼")
    await game_night(cf)


# 夜晚轮次流程
async def game_night(cf: Config):
    if cf.role_do == 6:
        cf.role_do += 1  # 加至超出范围,防止重复使用
        await to_morning(cf)  # 夜晚轮次结束
        return
    else:
        cf.role_do += 1

    if ("nvwu" in cf.roles_dict_have) and not cf.qq_obj[cf.role_qq["nvwu"][0]].save_med and not cf.qq_obj[cf.role_qq["nvwu"][0]].kill_med:  # 药用完了.除去女巫轮次
        cf.roles_dict_have.remove("nvwu")

    zhiye = finalpool.roles_dict[cf.role_do]  # 当前轮次的职业
    if zhiye not in cf.roles_dict_have:     # 本局若不存在该角色,轮空
        return await game_night(cf)

    if zhiye != "NULL":
        qs = cf.role_qq[zhiye]
        say = f"(轮到{finalpool.translate[zhiye]}的回合,请私聊使用)!{get_says(zhiye)})"
        for qq in qs:
            obj = cf.qq_obj[qq]
            if cf.maybe_die and ("nvwu" in cf.roles_dict_have) and cf.qq_obj[cf.role_qq["nvwu"][0]].save_med and cf.role_do == 6:  # 女巫救人回合
                dl = []
                for dm in cf.maybe_die:
                    dl.append(dm.number)
                await obj.private_say(str(dl) + "号已死亡, 回复 /救 号数 或 /不使用技能")
            if not obj.has_die:
                await obj.private_say(say)
            # if not obj.has_die:
            #     await obj.go()
        if zhiye == "wolf":     # 狼轮次给狼队友发
            if "wolf_bai" in cf.roles_dict_have:
                o = cf.qq_obj[cf.role_qq["wolf_bai"][0]]
                await o.private_say(say)
            if "wolf_king" in cf.roles_dict_have:
                o = cf.qq_obj[cf.role_qq["wolf_king"][0]]
                await o.private_say(say)
            if "wolf_no" in cf.roles_dict_have and cf.qq_obj[cf.role_qq["wolf_no"][0]].has_skill:
                o = cf.qq_obj[cf.role_qq["wolf_no"][0]]
                await o.private_say(say)


# 杀死死人 -
async def to_morning(cf: Config):  # 前夕:进入白天-(警长流程)-彻底杀死 - 开启白天流程 - 待完成
    maybe_die = cf.maybe_die
    if maybe_die:
        await check_die(cf)     # 清理死人

    # 如果游戏未结束
    if not cf.game_over and not cf.die_say:  # 进入白天
        cf.who_say = 0
        if cf.night:  # 进入白天
            cf.night = False
            cf.today += 1

        res = f"天亮了,今天是第{str(cf.today)}天.进入白天轮流发言"
        await send_gm(cf.bot, cf.group, res)
        if ("wolf_bai" or "qishi") in cf.role_qq.keys():    # 白天可行动
            for obj in list(cf.qq_obj.values()):
                if obj.role in ["wolf_bai", "qishi"]:
                    await obj.go()
        cf.time = 1
        await game_morning(cf)  # 否则进入白天发言流程


async def sleep_all(cf: Config):
    for o in list(cf.qq_obj.values()):
        await o.sleep()


async def check_die(cf: Config):   # 销毁死人:号数 (猎人,狼王检测)-  删除职业轮次 - 检查游戏是否结束 - 发遗言
    maybe_die = cf.maybe_die
    for who in maybe_die:
        num = who.number  # 获取信息
        qq = who.qq
        role = who.role
        await who.real_die()
        if role in cf.roles_dict_have and role != "wolf":  # 删轮次
            cf.roles_dict_have.remove(role)

        await send_gm(cf.bot, cf.group, f"{num}号已死亡.")
        # 删除 职业-玩家
        kl = list(cf.role_qq.keys()).copy()
        for k in kl:
            if qq in cf.role_qq[k]:
                cf.role_qq[k].remove(qq)
            if not cf.role_qq[k] and k != "wolf":
                del cf.role_qq[k]

        cf.game_over = await check_game_over(cf)  # 检查游戏是否结束
        if cf.game_over:
            await game_over(cf)
            return

        if cf.today <= 1 or not cf.night:  # 第一晚死或者白天死有遗言
            cf.die_say = True
            cf.say_man.append(who)
            await who.say_min()  # 发遗言(一分钟未完成
    cf.maybe_die = []


async def check_game_over(cf: Config) -> bool:
    if "people" not in cf.role_qq:  # 判定游戏结束
        res = "游戏结束,平民死完,狼人胜利!"
        await send_gm(cf.bot, cf.group, res)
        return True

    key_ls = cf.role_qq.keys()  # 此时还存在的职业
    whether_over = True     # 判断狼死完
    for key in key_ls:
        if "wolf_" in key:
            whether_over = False
            break
        if key == "wolf" and cf.role_qq[key]:
            whether_over = False
            break
    if whether_over:
        res = "游戏结束,狼人死完,好人胜利!"
        await send_gm(cf.bot, cf.group, res)
        return whether_over

    whether_over = True
    shen_has = cf.roles_dict_have.copy()
    shen_has.remove("wolf")  # 本局的神职
    for key in key_ls:
        if key in shen_has:
            whether_over = False
            break
    if whether_over:
        res = "游戏结束,神人死完,狼人胜利!"
        await send_gm(cf.bot, cf.group, res)
        return True

    if not cf.role_qq["wolf"] and "wolf_no" in key_ls:  # 隐狼觉醒
        cf.qq_obj[cf.role_qq["wolf_no"][0]].has_skill = True

    await send_gm(cf.bot, cf.group, "继续游戏...")
    return False


async def game_over(cf: Config):
    # 解除禁言
    # if cf.ban:
    #     if get_member_permission(cf.bot,cf.group,cf.bot.self_id):
    #         res = ""
    #         for o in list(cf.qq_obj.values()):
    #             try:
    #                 await o.unban_say()  # jie言
    #             except ActionFailed:
    #                 res += f"解禁[CQ:at,qq={o.qq}]权限不足 "
    #         if res != "":
    #             await send_gm(cf.bot, cf.group, res)
    #     else:
    #         await send_gm(cf.bot, cf.group, "权限不足")
    await send_gm(cf.bot, cf.group, "游戏结束")
    # 清除配置项
    if cf.group in finalpool.configs:
        for qq in cf.joiner:    # 删除参加, (改回卡片名称 未完成
            if qq in finalpool.member_group:
                del finalpool.member_group[qq]
        del finalpool.configs[cf.group]
        del cf


# 白天轮流发言
async def game_morning(cf: Config):
    cf.time = 1
    maxdo = len(cf.qq_obj)
    if maxdo == cf.who_say:     # 进去投票
        return await to_vote(cf)
    obj = list(cf.qq_obj.values())[cf.who_say]  # 获取发言人
    cf.say_man.append(obj)
    cf.who_say += 1
    if not cf.die_say:
        if obj.has_die:  # 死人跳过发言
            cf.say_man.remove(obj)
            await game_morning(cf)
        else:
            await obj.say_min()  # 发言


# 投票初始化
async def to_vote(cf):  # 群聊投票(死人跳过
    cf.time = 2
    # if cf.ban:      # 解禁言
    #     for obj in list(cf.qq_obj.values()):
    #         # 死人跳过
    #         if obj.has_die:
    #             continue
    #         await obj.unban_say()
    await send_gm(cf.bot, cf.group, get_says("vote"))


# 投票是否完成
async def check_vote_finish(cf: Config):
    for obj in list(cf.qq_obj.values()):
        if not obj.has_voted:  # 投票未完成
            return
    obj = await ticket_max(cf)  # 投票完成, 取得最大对象

    # 投票完成, 驱逐
    if obj is not None:
        await obj.quzhu()
        await send_gm(cf.bot, cf.group, f"{obj.number}号被驱逐")
        # 检查死亡情况
        await check_die(cf)
    else:   # 进入黑夜
        await send_gm(cf.bot, cf.group, "最大同票,无人被驱逐")
        await to_night(cf)



# 得到最大票数者
async def ticket_max(cf: Config) -> Man:
    v = []
    l = list(cf.qq_obj.values())
    for obj in l:
        v.append(await obj.get_ticket())
    v_sort = v.copy()
    v_sort.sort(reverse=True)
    if v_sort[0] != v_sort[1]:
        num = v.index(v_sort[0])
        obj = l[num]
    else:
        obj = None
    await send_gm(cf.bot, cf.group, "投票结果:" + str(v))
    return obj
