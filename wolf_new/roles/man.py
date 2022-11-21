from nonebot.adapters.onebot.v11 import ActionFailed

from ..info import get_says, get_role_info
from ..utils import send_gm, private_say, group_card
from ..config import Config, finalpool


class Man:
    role = "people"

    def __init__(self, qq: str, num: int, cf: Config):
        self.qq = qq    # 这个人的qq
        self.number = num   # 这个人的号数
        self.ticket = 0     # 这个人的票数
        self.states = []    # 这个人的状态
        self.has_says = False
        self.has_die = False
        self.maybe_die = False
        self.has_voted = False
        self.cf = cf

    async def say_info(self):
        await self.private_say(get_role_info(self.role))
        # if self.cf.ban:
        #     await self.ban_say()
        await self.group_card(str(self.number))

    # async def ban_say(self):  # 禁言
    #     # 禁言20min
    #     try:
    #         await ban_say(self.cf.bot, self.cf.group, self.qq)
    #     except ActionFailed:
    #         pass
    #
    # async def unban_say(self):  # 解禁言
    #     try:
    #         await unban_say(self.cf.bot, self.cf.group, self.qq)
    #     except ActionFailed:
    #         pass

    async def private_say(self, says):
        try:
            await private_say(self.cf.bot, self.qq, self.cf.group, says)
        except ActionFailed:
            pass

    async def group_card(self, wt):
        try:
            await group_card(self.cf.bot, self.cf.group, self.qq, wt)
        except ActionFailed:
            pass

    async def say_min(self):  # 发言: ((一分钟)(可中断)(未完成)
        # if self.cf.ban:
        #     try:
        #         await self.unban_say()  # jie言
        #     except ActionFailed:
        #         await send_gm(self.cf.bot, self.cf.group, "禁言权限不足")
        if self.cf.die_say:
            res = f"遗言发表：有请{self.number}号[CQ:at,qq={self.qq}]发言,结束发言回复 /过"
        else:
            res = f"轮流发言：有请{self.number}号[CQ:at,qq={self.qq}]发言,结束发言回复 /过"
        await send_gm(self.cf.bot, self.cf.group, res)

    # 假死状态
    async def fake_die(self):
        self.maybe_die = True
        self.cf.maybe_die.append(self)

    # 真死状态
    async def real_die(self):
        self.maybe_die = False
        if ("shemeng" or "shouhu") not in self.states:
            self.has_voted = True  # 无票数
            self.has_die = True
            await self.group_card(f"{self.number} 已死亡")

    # 添加效果
    async def add_state(self, state: str):
        self.states.append(state)

    # 睡觉来清除效果
    async def sleep(self):
        if not self.has_die:
            self.states = []
            self.has_voted = False
            self.ticket = 0
            self.has_says = False

    # async def add_ticket(self):
    #     self.ticket += 1

    async def vote(self, who) -> bool:
        if not self.has_voted and not self.has_die:
            await who.add_ticket()
            self.has_voted = True
            res = f"Finish vote to {who.number}!"
            b = True
        else:
            res = "Vote fail! You have voted or die."
            b = False
        await send_gm(self.cf.bot, self.cf.group, res)
        return b

    async def add_ticket(self):
        self.ticket += 1

    async def get_ticket(self):
        if "zuzhou" in self.states:
            self.ticket += 1
        if self.has_die:
            return 0
        else:
            return self.ticket

    async def quzhu(self):
        await self.fake_die()


    async def go(self):
        await self.private_say(f"(轮到{finalpool.translate[self.role]}的回合,请私聊使用)!" + get_says(self.role))


class People(Man):
    async def go(self):
        pass
