from nonebot.adapters.onebot.v11 import Bot


class Config:
    def __init__(self):
        self.bot: Bot
        self.group: str      # 该配置对应群组
        # ban: bool = False   # 未到发言是否禁言（需要权限
        self.game_start: bool = False    # 是否已开始
        self.zdy: bool = False   # 是否自定义
        self.create_game: list = []    # 自定义配置
        self.joiner: list = []    # 参加人员[qq]
        self.today: int = 0      # 天数
        self.time: int = 0   # 总体时间(群里的时间) 闭眼 - 发言 - 投票 - 遗言
        self.night: bool = True  # 是否夜晚
        self.role_qq: dict = {}  # 职业:[qq]
        self.qq_obj: dict = {}   # qq:对象
        # 职业 -> qq -> 对象
        self.roles_dict_have: list = []   # 有夜晚流程的职业
        # has_police: bool = False    # 是否有警长
        # police: str = None
        self.wolf_used_skill: bool = False
        self.role_do: int = 0    # 夜晚轮次
        self.who_say: int = 0    # 发言
        self.die_say: bool = False   # 是否为遗言
        self.say_man = []  # 发言人 [Man]
        self.maybe_die: list = []    # 假死: Man
        self.game_over: bool = False


class FinalPool:
    configs = {}  # group: Config
    member_group = {}   # qq: group
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
    obj = {
        "shouwei": "Shouwei(qq, num, cf)",
        "shemeng": "Shemeng(qq, num, cf)",
        "wuya": "Wuya(qq, num, cf)",
        "yuyan": "Yuyan(qq, num, cf)",
        "nvwu": "Nvwu(qq, num, cf)",
        "qishi": "Qishi(qq, num, cf)",
        "hunter": "Hunter(qq, num, cf)",
        "wolf_king": "Wolf_king(qq, num, cf)",
        "wolf_bai": "Wolf_bai(qq, num, cf)",
        "wolf_no": "Wolf_no(qq, num, cf)",
        "baichi": "Baichi(qq, num, cf)",
    }
    roles_dict = {      # 行动表
        0: "None",
        1: "shouwei",
        2: "shemeng",
        3: "wuya",
        4: "wolf",
        5: "yuyan",
        6: "nvwu",
        7: "None"
        # 7: "qishi",
        # 8: "hunter",
        # 9: "wolf_king"
    }


finalpool = FinalPool()
