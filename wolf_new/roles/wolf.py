from .man import Man


class Wolf(Man):
    role = "wolf"

    async def say_info(self):
        await super().say_info()
        res = "你的队友qq是"
        for k in self.cf.role_qq.keys():
            if "wolf" in k and k != "wolf_no":  # 狼队友消息
                res += f" {str(self.cf.role_qq[k])}"
        await self.private_say(res)

    async def skill(self, who: Man) -> bool:
        if not self.cf.wolf_used_skill and not who.has_die:
            if "shouhu" not in who.states and "shemeng" not in who.states:
                await who.fake_die()
            self.cf.wolf_used_skill = True
            res = "正在提刀的路上!"
            b = True
        else:
            res = "击杀失败,我方已使用过技能或对象不存在"
            b = False
        await self.private_say(res)
        return b

    async def sleep(self):
        await super().sleep()
        self.cf.wolf_used_skill = False


class Wolf_bai(Wolf):
    role = "wolf_bai"

    async def boom(self, who: Man) -> bool:
        if self.has_die:
            res = "你已经死亡"
            b = False
        elif self.cf.night:
            res = "还未到白天哦"
            b = False
        elif not who.has_die:
            res = "自爆成功"
            await self.fake_die()
            await who.fake_die()
            b = True
        else:
            res = "自爆失败,对象已死亡."
            b = False
        await self.private_say(res)
        return b


class Wolf_king(Wolf):
    role = "wolf_king"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.has_skill = False

    async def real_die(self):
        if "shemeng" not in self.states and "du" not in self.states:
            self.has_skill = True
            await self.go()

    async def bring(self, who: Man) -> bool:
        if not who.has_die:
            self.has_skill = False
            if self.has_skill:
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


class Wolf_no(Wolf):
    role = "wolf_no"

    def __init__(self, qq, num, cf):
        super().__init__(qq, num, cf)
        self.has_skill = False

    async def get_skill(self):
        self.has_skill = True

    async def skill(self, who: Man) -> bool:
        if not who.has_die:
            if self.has_skill:
                await who.real_die()
                res = "击杀成功"
                self.cf.wolf_used_skill = True
                b = True
            else:
                res = "未拥有技能"
                b = False
        else:
            res = "使用技能失败,对象已死亡"
            b = False
        await self.private_say(res)
        return b
