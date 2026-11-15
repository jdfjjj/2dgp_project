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
    """적에게 피해. 체력이 0이 되면 처치, 아니면 밀려남"""
    e.hp -= dmg
    effects.burst(e.x, e.y + 8, 'px_lav', 8)
    if e.hp <= 0:
        kill(e)
    else:
        e.knock(nx, ny)


def kill(e):
    """적 처치: 게임 월드와 적 목록에서 빼고 조각으로 흩어짐"""
    if e in enemies:
        enemies.remove(e)
        game_world.remove_object(e)
        effects.burst(e.x, e.y + 8, 'px_lav', 14, 160)
        effects.burst(e.x, e.y + 8, 'px_white', 6, 120)


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


def pick_light(pk):
    """빛 조각 줍기: 빛이 차고, 조각이 흩어지며 +7 이 떠오름"""
    if pk in pickups:
        pickups.remove(pk)
        game_world.remove_object(pk)
        add_light(game_settings.SHARD_LIGHT)
        effects.burst(pk.x, pk.y, 'px_gold', 10, 100)
        effects.text(pk.x, pk.y + 24, '+%d' % game_settings.SHARD_LIGHT, 'y')
