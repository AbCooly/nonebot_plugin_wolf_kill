<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

# nonebot_plugin_wolf_kill

——基于nonebot2的狼人杀游戏插件

Name: nonebot2
Version: 2.0.0rc1

## 2022-11-22 更新

—— 重写了代码，修复了一些bug

—— 移除 警长，禁言

## 简介

在群里玩狼人杀

<p align="center">
  <a href="https://pypi.org/project/nonebot-plugin-wolf-kill/">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-wolf-kill.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
</p>

## 功能介绍

### /自定义(可选)

/自定义 神数 狼数 民数 技能身份...

如：/自定义 2 2 2 预言家 猎人

默认内置6-12局

![image-20220911155327686](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-591548816-8A438D00E61BEFD29263CD8CE736FBBD/0)

例如:(平民跟狼人至少有一个,目前只有屠边模式)

![image-20220911155433627](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-1058972522-6E4349F5BD2512DD9720B01EE75FBF70/0)



### /参加狼人杀

![image-20220911155804888](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-533425835-B46A6A9D6268C926F6974845873816F3/0)

### /开始游戏

![](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-261819240-6995762E2B1F29CDD5EC7173C4B3462C/0)

(没有自定义,默认6-12人局)

### /结束游戏

![image-20220911160335098](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-3037391408-682331DD6D7077F8CD51C6E5353EB233/0)

中途结束游戏,清空所有配置

## 游戏详细流程

人数足够,开始游戏

![image-20220911161004916](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-1551632577-BBF3007EF9DCF8A9CE5B956CFB5C3A1B/0)

机器人私发身份

![image-20220911161114031](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-2115011916-CCFAAD4AA530D8BEE88F2E828F19CF81/0)

轮流发言

![image-20220911161232705](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-432810983-96BBFBDF45207AB798B405F5060B5851/0)

投票环节

![image-20220911161250683](https://c2cpicdw.qpic.cn/offpic_new/2553997408//2553997408-2074920659-9A9A26A47FD8ADFFBE449F838F0AE63E/0)



## 另外

记得把配置文件的临时会话打开

