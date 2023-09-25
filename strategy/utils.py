from game.character.character import Position
from game.character.character import Character
from typing import Callable
from game.character.action.attack_action import AttackAction
from game.game_state import GameState
from game.terrain.terrain_type import TerrainType


def zombie_group_size(
        human_poses: list[Position]):  # big when human group size is big, 3 when human group size is small
    result = []
    for current in human_poses:
        result.append(max(map(lambda pos: chebyshev_distance(pos, current), human_poses)))
    return 25 if max(result) <= 20 else 3


def human_group_size(
        zombie_poses: list[Position]):  # 4 when zombie group size is big, 6 when zombie group size is small
    result = []
    for current in zombie_poses:
        result.append(max(map(lambda pos: chebyshev_distance(pos, current), zombie_poses)))
    return 4 if max(result) >= 8 else 6


def chebyshev_distance(pos1: Position, pos2: Position) -> int:
    return max([abs(pos1.x - pos2.x), abs(pos1.y - pos2.y)])


def manhattan_distance(pos1: Position, pos2: Position) -> int:
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def relative_direction(start: Position, end: Position) -> tuple[int, int]:
    def clamp(x):
        if x < 0:
            return -1
        if x > 0:
            return 1
        return 0

    return (clamp(end.x - start.x), clamp(end.y - start.y))


def avg_position(poses: list[Position]) -> Position:
    x = round(avg([pose.x for pose in poses]))
    y = round(avg([pose.y for pose in poses]))
    result = Position(x=x, y=y)
    return result


def avg(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def farthest(poses: list[Position], characters: list[Character],
             distance_func: Callable[[Position, Position], int]) -> Position | None:
    poses = [pose for pose in poses if pose is not None]
    if len(poses) == 0:
        return None

    best_pose: Position = poses[0]
    distance = 0
    for pose in poses:
        dist = min(map(lambda character: distance_func(pose, character.position), characters))
        if dist > distance:
            best_pose = pose
            distance = dist
    return best_pose


def closest(poses: list[Position], characters: list[Character],
            distance_func: Callable[[Position, Position], int]) -> Position | None:
    poses: list[Position] = [pose for pose in poses if pose is not None]  # a list of positions that are not None
    if len(poses) == 0:  # returns None if the list is empty
        return None

    best_pose: Position = poses[0]  # start at index 0 for the sake of the iteration below
    distance = 1000  # arbitrary value used to start comparisons.
    for pose in poses:
        dist = avg([distance_func(pose, character.position) for character in characters])
        if dist < distance:
            best_pose = pose
            distance = dist
    return best_pose


def water_within_move_distance(pos: Position, move_speed: int, game_state: GameState) -> bool:
    water_poses: list[Position] = [terrain.position for terrain in game_state.terrains.values() if
                                   terrain.type == TerrainType.RIVER]
    return len([p for p in water_poses if manhattan_distance(p, pos) <= move_speed]) > 0


def close_water_in_relative_direction(pos: Position, move_speed: int, relative_dir: tuple[int, int],
                                      game_state: GameState) -> bool:
    water_poses: list[Position] = [terrain.position for terrain in game_state.terrains.values() if terrain.health == -1]
    close_water = [p for p in water_poses if manhattan_distance(p, pos) <= move_speed]
    relative_dirs = [relative_direction(pos, water) for water in close_water]
    return len([d for d in relative_dirs if relative_dir[0] == d[0] and relative_dir[1] == d[1]]) > 0


def unique_poses(poses: list[Position]) -> list[Position]:
    result = []
    for pos in poses:
        if not pos_in_list(pos, result):
            result.append(pos)
    return result


def adjacent(pos: Position, game_state: GameState) -> list[Position]:
    x = pos.x
    y = pos.y
    result: list[Position] = [Position(x - 1, y - 1), Position(x - 1, y + 1), Position(x + 1, y - 1),
                              Position(x + 1, y + 1)]
    water_poses: list[Position] = [terrain.position for terrain in game_state.terrains.values() if terrain.health == -1]
    return [pos2 for pos2 in result if not pos_in_list(pos2, water_poses)]


def find_next_tile(start_pos: Position, end_pos: Position, move_speed: int, game_state: GameState) -> Position:
    def bfs(visited: list[tuple[Position, int]], current: list[Position], distance: int) -> list[tuple[Position, int]]:
        possible_poses = [adjacent(pos, game_state) for pos in current]
        possible_poses = unique_poses(
            [pos for poses in possible_poses for pos in poses if not pos_in_list(pos, [v[0] for v in visited])])
        visited.extend([(pos, distance) for pos in possible_poses])
        if len(possible_poses) == 0:
            return visited
        return bfs(visited, possible_poses, distance + 1)

    current_pos: Position = start_pos
    for i in range(move_speed):
        weights = bfs([], [end_pos], 0)
        allowed = [Position(x, y) for x in range(100) for y in range(100) if
                   pos_in_list(Position(x, y), adjacent(current_pos, game_state))]
        weights = [pos for pos in weights if pos_in_list(pos[0], allowed)]
        min_weight = min([x[1] for x in weights])
        current_pos = [pos[0] for pos in weights if pos[1] == min_weight][0]
    return current_pos


def pos_in_list(pos: Position, poses: list[Position]) -> bool:
    for p in poses:
        if pos.x == p.x and pos.y == p.y:
            return True
    return False


def relative_dir_in_list(target: tuple[int, int], relative_dirs: list[tuple[int, int]]) -> bool:
    for d in relative_dirs:
        if target[0] == d[0] and target[1] == d[1]:
            return True
    return False


def relative_dirs_of_at_least_x_number(relative_dirs: list[tuple[int, int]], x: int) -> list[tuple[int, int]]:
    counts: dict[tuple[int, int], int] = {}
    for d in relative_dirs:
        counts.setdefault(d, 0)
        counts[d] += 1

    result: list[tuple[int, int]] = []
    for d, count in counts.items():
        if count >= x:
            result.append(d)
    return result


def relative_dir_comparison(rel_dirs: list[tuple[int, int]], rel_dirs_2: list[tuple[int, int]], factor: float = 1,
                            offset: int = 0) -> list[tuple[int, int]]:
    first_counts: dict[tuple[int, int], int] = {}
    for d in rel_dirs:
        first_counts.setdefault(d, 0)
        first_counts[d] += 1

    second_counts: dict[tuple[int, int], int] = {}
    for d in rel_dirs_2:
        second_counts.setdefault(d, 0)
        second_counts[d] += 1

    result: list[tuple[int, int]] = []
    for d, count in first_counts.items():
        if count >= (second_counts.get(d, 0) * factor + offset):
            result.append(d)
    return result


def should_attack(character: Character, other_attacks: list[AttackAction]) -> bool:
    attacks_against_character = [attack for attack in other_attacks if attack.attacking_id == character.id]
    return character.health > len(attacks_against_character)
