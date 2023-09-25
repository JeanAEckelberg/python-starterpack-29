from game.game_state import GameState
from game.character.action.move_action import MoveAction
from game.character.action.attack_action import AttackAction
from game.character.action.ability_action import AbilityAction
from game.character.character_class_type import CharacterClassType
from game.character.action.attack_action import AttackAction
from game.character.action.attack_action_type import AttackActionType
from strategy.utils import *


def decide_move(character: Character, possible_moves: list[MoveAction], game_state: GameState, other_moves: list[MoveAction]) -> MoveAction | None:
    zombies: list[Character] = [c for c in game_state.characters.values() if
                                c.is_zombie]  # filtering out for just zombie
    human_poses: list[Position] = [move.destination for move in other_moves]
    dirs: list[tuple[int, int]] = [relative_direction(character.position, human_pos) for human_pos in human_poses]
    dirs.extend(
        [relative_direction(character.position, c.position) for c in game_state.characters.values() if not c.is_zombie])
    dirs = relative_dirs_of_at_least_x_number(dirs, human_group_size([zombie.position for zombie in zombies]))
    dirs.extend(
        [relative_direction(character.position, c.position) for c in game_state.characters.values() if c.is_zombie])
    poses: list[Position] = [p.destination for p in possible_moves if
                             not relative_dir_in_list(relative_direction(character.position, p.destination), dirs)]
    if len(poses) == 0:
        poses = [m.destination for m in possible_moves]

    pos = farthest(poses, zombies, manhattan_distance)
    if pos is None:
        return None
    to_return = [m for m in possible_moves if pos == m.destination]
    if to_return is not None:
        to_return = to_return[0]
    return to_return


def decide_attack(character: Character, possible_attacks: list[AttackAction], game_state: GameState, other_attacks: list[AttackAction]) -> AttackAction | None:
    zombies: list[Character] = []
    target: Character
    for target in game_state.characters.values():
        if target.class_type == CharacterClassType.ZOMBIE:
            zombies.append(target)

    if len(zombies) == 0:
        return None

    best_attack: AttackAction = possible_attacks[0]
    lowest_attack_health = \
    (game_state.characters if best_attack.type == AttackActionType.CHARACTER else game_state.terrains)[
        best_attack.attacking_id].health
    for attack in possible_attacks:
        health = (game_state.characters if attack.type == AttackActionType.CHARACTER else game_state.terrains)[
            attack.attacking_id].health
        if attack.type == AttackActionType.CHARACTER and any(
                [a.attacking_id == attack.attacking_id for a in other_attacks]):
            continue
        if attack.type == AttackActionType.TERRAIN:
            avg_pos = avg_position([z.position for z in zombies])
            zombie_dir = relative_direction(character.position, avg_pos)
            attack_dir = relative_direction(character.position, game_state.terrains[attack.attacking_id].position)
            if attack_dir[0] == zombie_dir[0] and attack_dir[1] == zombie_dir[1]:
                continue
        if (health < lowest_attack_health and best_attack.type == attack.type) or (
                best_attack.type == AttackActionType.TERRAIN and attack.type == AttackActionType.CHARACTER):
            best_attack = attack
            lowest_attack_health = health
    return best_attack


def decide_ability(character: Character, possible_abilities: list[AbilityAction], game_state: GameState, other_actions: list[AbilityAction]) -> AbilityAction | None:
    return possible_abilities[0]
