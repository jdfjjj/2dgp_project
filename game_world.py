LAYER_FLOOR = 0      # 바닥 타일
LAYER_ITEM = 1       # 빛 조각, 열쇠
LAYER_CHAR = 2       # 플레이어, 적 (아래쪽에 있는 것이 앞에 그려지도록 정렬)
LAYER_DARK = 3       # 어둠 (그 위에 빛나는 것들)
LAYER_FX = 4         # 이펙트: 던진 빛, 공격, 탄, 파티클, 숫자

world = [[], [], [], [], []]


def add_object(o, depth=0):
    world[depth].append(o)


def add_objects(ol, depth=0):
    world[depth] += ol


def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return


def objects(depth):
    return world[depth]


def clear():
    for layer in world:
        layer.clear()