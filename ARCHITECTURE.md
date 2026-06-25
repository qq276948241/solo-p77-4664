# 接水果大作战 · 架构说明

## 入口和整体运行方式

游戏启动文件是根目录的 `fruit_catcher.py`，运行 `python fruit_catcher.py` 即可开始。入口处会初始化 pygame、音频、高分存档，然后实例化一个 `Game` 对象并调用它的 `run()` 方法。`run()` 方法就是一个标准的游戏循环：每帧先处理输入事件，然后根据当前游戏状态决定要不要更新游戏逻辑，最后把相应的画面画到屏幕上。循环帧率被锁在 60 FPS。

全局共享的屏幕尺寸、颜色常量和 pygame 初始化都放在 `config.py` 里，其它模块按需 import，避免每个文件重复写一遍。

## 游戏状态机

`Game` 类内部用一个简单的字符串状态机控制流程，一共五个状态：

- `menu`：开始菜单，显示标题、最高分和操作说明。按回车或空格，或者点击"开始游戏"按钮进入 `playing`。
- `playing`：正常游戏中。这一帧会移动篮子、让掉落物下落、刷新 combo 计时器、按间隔生成新的水果和金苹果、做碰撞检测、扣关卡倒计时。按 P 或 ESC 切到 `paused`，倒计时归零切到 `level_complete`，血量归零切到 `game_over`。
- `paused`：暂停。逻辑层面除了 combo 计时器继续倒计（防止暂停被当成"刷 combo 时长"的漏洞），其它更新全部冻结。画面会叠一层半透明黑，再画三个按钮：继续、音乐开关、返回主菜单。
- `level_complete`：过关界面。提示当前关卡完成，显示得分和剩余生命。按任意键回到 `playing`，关卡号加一，重置 30 秒倒计时，并略微缩短生成间隔来提难度。
- `game_over`：游戏结束或通关。显示最终分数、历史最高，达到新纪录时会高亮。回车重开，ESC 返回主菜单。

状态切换统一由 `_start_game()`、`_toggle_pause()`、`_next_level()`、`_game_over()`、`_set_state()` 这些方法处理，不用在事件循环里硬改 state 字段。

## 主要 Sprite 类怎么工作

所有会动的、会画到屏幕上的游戏对象都继承自 `pygame.sprite.Sprite`，统一塞进 `Game.all_sprites` 这个 Group 里，最后一行 `all_sprites.draw(screen)` 就能全部画出来。

`Basket`（篮子）的逻辑很直接：`__init__` 里用 pygame 的基本绘图函数画一个棕色的篮子，再把 `rect.bottom` 贴到屏幕底部。`update(keys)` 每帧读一次键盘，根据左右方向键增减 `rect.x`，并做边界检查不让篮子飞出屏幕。

`FallingItem` 是四种常规掉落物——苹果、香蕉、葡萄、炸弹——的统一实现。`TYPES` 字典里存了每种的颜色、得分、碰撞半径、是否为炸弹。初始化时按权重随机选一种（关卡越高炸弹权重越高），然后调用 `_draw_item()` 根据类型画不同的像素画。`update()` 让它按速度匀速下落，掉出屏幕底部就 `kill()`。

`GoldenApple` 和 `Star` 是两个独立的子类，分别对应金苹果和炸弹弹飞后的星星。它们各自带 `is_golden` 和 `is_star` 标记，碰撞检测里靠这两个布尔值走不同分支。

## 碰撞处理、Combo 和关卡难度

碰撞用 pygame 自带的 `spritecollide` 做矩形检测，每个篮子命中的物品根据上面说的类型标记分支处理：

- 普通水果：加分，累加 combo，播接水果音效，喷对应颜色的粒子。
- 金苹果：固定 50 分，同样享受 combo 倍率，播专属音效，粒子数量翻倍，顺便把跟着它的光晕一起 kill 掉。
- 炸弹：不扣血，改为在碰撞点生成一颗往上飞的 `Star`，附带一个八方向放射的爆裂特效，播弹飞音效。
- 星星：30 分，享受 combo 倍率。

`ComboDisplay` 类维护连击状态：连续接到水果 combo 数加一，同时把计时器重置到 90 帧（1.5 秒）；超时或接到炸弹就归零。倍率阶梯是 3 连 x1.5、5 连 x2、10 连 x3。暂停期间计时器也会正常倒计，避免暂停刷 combo。

关卡难度通过三个参数控制：一是掉落物的基础下落速度，每关 +0.5；二是生成间隔，从第 1 关的 45 帧逐步缩短到第 10 关的 15 帧；三是第 4 关后每次生成有 30% 概率再多刷一个。金苹果是每 480 帧（约 8 秒）刷一个，不受关卡影响。

## 最高分存档

最高分以 JSON 格式存在根目录的 `high_score.json` 里，结构是 `{"high_score": 数字}`。启动时 `_load_high_score()` 读一次，Game Over 时如果当前分数破了记录，`_save_high_score()` 就写回去。文件不存在或解析失败会回退到 0 分，不会崩。

## 怎么加一种新水果类型

假设要加一个"橙子"，得分 12 分，颜色橙色。主要改两个地方：

第一，在 `sprites/fruit.py` 的 `TYPES` 字典里加一条配置，然后在 `_draw_item()` 的 elif 链里补一段绘制逻辑。下面是伪代码：

```python
# sprites/fruit.py

class FallingItem(pygame.sprite.Sprite):
    TYPES = {
        'apple':  {'color': RED,    'points': 10, 'radius': 20, 'is_bomb': False},
        'banana': {'color': YELLOW, 'points': 15, 'radius': 22, 'is_bomb': False},
        'grape':  {'color': PURPLE, 'points': 20, 'radius': 20, 'is_bomb': False},
        'orange': {'color': ORANGE, 'points': 12, 'radius': 21, 'is_bomb': False},  # 新增
        'bomb':   {'color': DARK_GRAY, 'points': 0, 'radius': 22, 'is_bomb': True},
    }

    def __init__(self, level=1):
        # 同时把 random.choices 的 weights 里也加上橙子的权重，比如 25
        self.item_type = random.choices(
            ['apple', 'banana', 'grape', 'orange', 'bomb'],
            weights=[30, 25, 20, 25, 20 + level * 1],
            k=1
        )[0]
        # ...其余不变

    def _draw_item(self):
        # ...前面不变
        elif self.item_type == 'orange':
            cx, cy = self.radius, self.radius
            pygame.draw.circle(self.image, ORANGE, (cx, cy), self.radius - 3)
            pygame.draw.circle(self.image, (255, 200, 100), (cx - 5, cy - 5), 4)
            pygame.draw.rect(self.image, (100, 180, 50), (cx - 2, cy - self.radius, 4, 5))
        # ...后面不变
```

第二，`config.py` 里确认已经有 `ORANGE` 这个颜色常量（当前版本已经有了，橙水果可以直接用）。

加完之后游戏自动就会按权重随机刷橙子，碰撞分支会走普通水果那条逻辑，combo、粒子、得分倍率全部生效，不需要改别的地方。
