"""게임 전체가 같이 쓰는 객체와 값, 그리고 게임 규칙(공격, 피해, 처치)을 모아 두는 곳
여러 파일이 서로 찾아야 하는 객체(주인공, 적 등)와 게임 상태(빛의 양 등)를 여기에 두고 꺼내 씀"""
import math

import game_settings
import game_world
import level
import effects
import items

player = None
enemies = []
orbs = []
pickups = []
dead_t = 0.0                               # 쓰러진 뒤 게임 오버까지 남은 시간
play_time = 0.0                            # 이번 판 플레이 시간
light_t = game_settings.START_LIGHT        # 지금 빛의 양 (2주차부터 시간이 지나면 줄어듦)
ST = dict(game_settings.BASE_STATS)        # 주인공 능력치 (3주차에 강화 카드로 오름)


def light_radius():
    """빛이 많을수록 넓게 보임: 빛 0이면 LIGHT_BASE, 빛 4 이상이면 시야 최대"""
    k = min(1.0, light_t / 4.0)
    return game_settings.LIGHT_BASE + (ST['sight'] - game_settings.LIGHT_BASE) * k


def update_light(dt):
    """시간이 지나면 빛이 조금씩 줄어듦"""
    global light_t
    light_t = max(0.0, light_t - game_settings.LIGHT_DECAY * dt)


def add_light(v):
    """빛을 채움 (최대 빛을 넘지 않게)"""
    global light_t
    light_t = min(ST['light_cap'], light_t + v)


def player_attack():
    """부채꼴 공격: 사거리 안, 각도 안, 벽에 가리지 않은 적에게 피해"""
    p = player
    ang = math.atan2(p.fy, p.fx)
    half = math.radians(ST['arc']) / 2
    effects.slash(p.x, p.y, ang, ST['reach'], ST['arc'])
    for e in enemies[:]:
        dx, dy = e.x - p.x, e.y - p.y
        d = math.hypot(dx, dy)
        if d > ST['reach'] + e.r:
            continue
        diff = abs((math.atan2(dy, dx) - ang + math.pi) % math.tau - math.pi)   # 바라보는 방향과의 각도 차이
        if d > e.r and diff > half:
            continue
        if not level.can_see(p.x, p.y, e.x, e.y):
            continue
        hit_enemy(e, ST['dmg'], dx / max(d, 1), dy / max(d, 1))


def hit_enemy(e, dmg, nx, ny):
    """적에게 피해. 큰 그림자는 갑옷이 벗겨졌을 때만 통함. 체력이 0이 되면 처치"""
    if e.armor and e.expose_t <= 0:
        effects.burst(e.x, e.y + 16, 'px_white', 6, 80)     # 갑옷에 막힘
        e.knock(nx, ny)
        return
    e.hp -= dmg
    effects.burst(e.x, e.y + 8, 'px_lav', 8)
    if e.hp <= 0:
        kill(e)
    else:
        e.knock(nx, ny)


def kill(e):
    """적 처치: 조각으로 흩어지고, 빛 도둑이 들고 있던 빛은 바닥에 떨어지고, 빛이 1 참"""
    if e in enemies:
        enemies.remove(e)
        game_world.remove_object(e)
        effects.burst(e.x, e.y + 8, 'px_lav', 14, 160)
        effects.burst(e.x, e.y + 8, 'px_white', 6, 120)
        if e.carry > 0:
            drop_light(e.x, e.y, e.carry)
        add_light(game_settings.KILL_LIGHT)


def player_throw():
    """빛 던지기: 빛을 써서, 손에서 바라보는 방향으로 빛 구슬을 날림"""
    global light_t
    p = player
    light_t -= ST['throw_cost']
    hx, hy = p.hand()
    o = items.Orb(hx, hy, p.fx, p.fy)
    orbs.append(o)
    game_world.add_object(o, game_world.LAYER_FX)


def remove_orb(o):
    if o in orbs:
        orbs.remove(o)
        game_world.remove_object(o)


def orb_hit(e):
    """빛 구슬에 맞은 적은 잠깐 기절"""
    e.stun(game_settings.STUN_TIME)
    effects.burst(e.x, e.y + 8, 'px_gold', 8)


def drop_light(x, y, value):
    """바닥에 빛 조각을 떨어뜨림 (빛 도둑이 훔쳐 간 빛 등). 어둠 아래 레이어라 빛이 닿아야 보임"""
    pk = items.Pickup(x, y, value)
    pickups.append(pk)
    game_world.add_object(pk, game_world.LAYER_ITEM)


def pick_light(pk):
    """빛 조각 줍기: 빛이 차고, 조각이 금빛으로 흩어짐"""
    if pk in pickups:
        pickups.remove(pk)
        game_world.remove_object(pk)
        add_light(pk.value)
        effects.burst(pk.x, pk.y, 'px_gold', 10, 100)


def hurt_player(sx, sy, dmg=1):
    """주인공 피격: 하트가 줄고, 맞은 반대쪽으로 밀려나고, 잠깐 무적. 하트가 0이면 쓰러짐"""
    global dead_t
    p = player
    if p.invuln > 0 or p.hearts <= 0:
        return
    p.hearts -= dmg
    p.invuln, p.hurt_t = game_settings.INVULN_TIME, game_settings.HURT_TIME
    dx, dy = p.x - sx, p.y - sy
    d = max(1.0, math.hypot(dx, dy))
    p.kx, p.ky = dx / d * game_settings.PLAYER_KNOCK, dy / d * game_settings.PLAYER_KNOCK
    effects.burst(p.x, p.y + 20, 'px_red', 10, 120)
    effects.text(p.x, p.y + 70, '-%d' % dmg, 'r')
    if p.hearts <= 0:
        p.hurt_t, p.view = 99.0, 'side'            # 쓰러진 모습 유지
        dead_t = game_settings.DEATH_DELAY


def steal_light(e):
    """빛 도둑: 하트 대신 빛을 훔쳐서 달아남"""
    global light_t
    p = player
    amount = min(game_settings.THIEF_STEAL, light_t)
    if amount <= 0:
        return
    light_t -= amount
    e.steal(amount)
    p.invuln = 0.6                                 # 연달아 뺏기지 않게 잠깐 무적
    effects.burst(p.x, p.y + 20, 'px_gold', 10, 120)
    effects.text(p.x, p.y + 70, '-%d' % math.ceil(amount), 'y')


def check_contacts():
    """적과 몸이 닿으면: 빛 도둑은 빛을 훔치고, 나머지는 피격
    (맞고 밀려나거나 기절한 적, 빛을 이미 든 빛 도둑은 공격하지 않음)"""
    p = player
    for e in enemies:
        if e.hit_t > 0 or e.stun_t > 0:
            continue
        if math.hypot(e.x - p.x, e.y - p.y) >= e.r + p.r:
            continue
        if e.kind == 'thief':
            if e.carry <= 0 and p.invuln <= 0:
                steal_light(e)
        else:
            hurt_player(e.x, e.y)


def slam(e):
    """큰 그림자의 내려찍기: 빨간 원 안에 있으면 하트 2개"""
    effects.burst(e.x, e.y, 'px_red', 16, 180)
    p = player
    if math.hypot(p.x - e.x, p.y - e.y) < game_settings.SLAM_RADIUS:
        hurt_player(e.x, e.y, game_settings.SLAM_DMG)
