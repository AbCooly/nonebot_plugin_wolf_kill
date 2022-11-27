from .man import Man


class God(Man):
    pass


class Nvwu(God):
    role = "nvwu"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.save_med = True
        self.kill_med = True

    async def save_man(self, who: Man) -> bool:
        if who.maybe_die and self.save_med:
            who.maybe_die = False
            self.save_med = False
            res = "解救成功."
            b = True
        else:
            res = "解救失败,对象不存在!"
            b = False
        await self.private_say(res)
        return b

    async def skill(self, who: Man) -> bool:
        if not who.has_die and self.kill_med:
            who.states.append("du")
            self.kill_med = False
            await who.fake_die()
            res = "毒杀成功"
            b = True
        else:
            res = "使用技能失败"
            b = False
        await self.private_say(res)
        return b


class Yuyan(God):
    role = "yuyan"

    async def skill(self, who: Man) -> bool:
        if "wolf" in who.role:
            res = "He is a bad guy!"
        else:
            res = "He is a good man."
        await self.private_say(res)
        return True


class Hunter(God):
    role = "hunter"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.has_skill = False

    async def real_die(self):
        if "shemeng" not in self.states and "du" not in self.states:
            self.has_skill = True
            await self.go()

    async def skill(self, who: Man) -> bool:
        if not who.has_die:
            if self.has_skill:   # 触发技能
                await who.fake_die()
                res = "成功带走"
                b = True
            else:
                res = "未触发技能"
                b = False
        else:
            res = "使用技能失败,对象已死亡"
            b = False
        await self.private_say(res)
        return b


class Shouwei(God):
    role = "shouwei"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.release = None

    async def skill(self, who: Man) -> bool:
        if self.release != who:
            if not who.has_die:
                self.release = who
                who.states.append("shouhu")
                res = "守护成功!"
                b = True
            else:
                res = "守护失败!对象已死亡!"
                b = False
        else:
            res = "守护失败!不能连续守护同一人!"
            b = False
        await self.private_say(res)
        return b


class Baichi(Man):  # 无主动技能
    role = "baichi"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.has_skill = False

    async def quzhu(self):
        await self.go()
        self.has_skill = True
        await self.group_card(f"{self.number} 白痴")

    async def vote(self, who):
        if not self.has_voted and not self.has_skill:
            await who.add_ticket()
            self.has_voted = True
            res = "Finish vote!"
        else:
            res = "Vote fail!"
        await self.private_say(res)


class Wuya(God):
    role = "wuya"

    async def skill(self, who: Man) -> bool:
        if not who.has_die:
            b = True
            who.states.append("zuzhou")
            res = "诅咒成功!"
        else:
            res = "使用技能失败,对象已死亡!"
            b = False
        await self.private_say(res)
        return b


class Qishi(God):
    role = "qishi"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.has_skill = True

    async def skill(self, who: Man) -> bool:
        if not self.has_skill:
            res = "技能只能使用一次哦"
            b = False
        elif self.cf.night:
            res = "还未到白天哦"
            b = False
        elif not who.has_die:
            self.has_skill = False
            await self.group_card(f"{self.number}号 骑士")
            b = True
            if "wolf" in who.role:
                res = "成功击杀, 对面是坏人"
                await who.fake_die()
            else:
                res = "自己死亡, 对面是好人"
                await self.fake_die()
        else:
            res = "使用技能失败,对象已死亡"
            b = False
        await self.private_say(res)
        return b


class Shemeng(God):
    role = "shemeng"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.release = None     # Man

    async def fake_die(self):
        await super().fake_die()

        if self.release:
            self.release.maybe_die = True

    async def skill(self, who: Man) -> bool:
        if self.release != who:
            if not who.has_die:
                self.release = who
                who.states.append("shemeng")
                res = "释放成功!对方免疫伤害,自己死亡对方也死亡."
                b = True
            else:
                res = "使用技能失败,对象已死亡!"
                b = False
        else:
            res = "释放成功!对象已死亡!"
            b = True
            who.states.append("shemeng")
            await who.fake_die()
            if who.role == "hunter" or who.role == "wolf_king":
                who.has_skill = False   # 不触发技能
        await self.private_say(res)
        return b
