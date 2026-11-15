"""게임 전체가 같이 쓰는 객체와 값을 모아 두는 곳
여러 파일이 서로 찾아야 하는 객체(주인공 등)와 게임 상태(빛의 양 등)를 여기에 두고 꺼내 씀"""
import game_settings

player = None
enemies = []
light_t = game_settings.START_LIGHT        # 지금 빛의 양 (2주차부터 시간이 지나면 줄어듦)
ST = dict(game_settings.BASE_STATS)        # 주인공 능력치 (3주차에 강화 카드로 오름)


def light_radius():
    """빛이 많을수록 넓게 보임: 빛 0이면 LIGHT_BASE, 빛 4 이상이면 시야 최대"""
    k = min(1.0, light_t / 4.0)
    return game_settings.LIGHT_BASE + (ST['sight'] - game_settings.LIGHT_BASE) * k
