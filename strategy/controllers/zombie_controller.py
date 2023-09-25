from game.character.action.attack_action_type import AttackActionType
from game.game_state import GameState
from game.character.action.move_action import MoveAction
from game.character.action.attack_action import AttackAction
from game.character.action.ability_action import AbilityAction
from strategy.utils import chebyshev_distance
from game.character.character import Character
from game.util.position import Position
from game.character.character_class_type import CharacterClassType
from strategy.utils import *


def decide_move(character: Character, possible_moves: list[MoveAction], game_state: GameState,
                other_moves: list[MoveAction]) -> MoveAction | None:
    zombie_poses: list[Position] = [move.destination for move in other_moves]
    zombie_dirs: list[tuple[int, int]] = [relative_direction(character.position, zombie_pos) for zombie_pos in zombie_poses]
    human_poses: list[Position] = [h.position for h in game_state.characters.values() if not h.is_zombie]
    human_dirs: list[tuple[int, int]] = [relative_direction(character.position, pos) for pos in human_poses]
    # zombie_dirs = relative_dirs_of_at_least_x_number(zombie_dirs, zombie_group_size(human_poses))
    zombie_dirs = relative_dir_comparison(zombie_dirs, human_dirs, 1.75, -3)
    humans: list[Character] = [h for h in game_state.characters.values() if
                               not h.is_zombie and not relative_dir_in_list(
                                   relative_direction(character.position, h.position), zombie_dirs)]
    if len(humans) == 0:
        humans.append([h for h in game_state.characters.values() if not h.is_zombie][-1])

    closest_human_pos = character.position  # default position is zombie's pos
    closest_human_distance = 1984  # large number, map isn't big enough to reach this distance

    for c in humans:
        if c.is_zombie:
            continue  # Fellow zombies are frens :D, ignore them

        distance = max(abs(c.position.x - character.position.x), abs(c.position.y - character.position.y))  # calculate manhattan distance between human and zombie
        if distance < closest_human_distance:  # If distance is closer than current closest, replace it!
            closest_human_pos = c.position
            closest_human_distance = distance
    # Move as close to the human as possible
    move_distance = 1337  # Distance between the move action's destination and the closest human
    move_choice = possible_moves[0]  # The move action the zombie will be taking
    for m in possible_moves:
        distance = max(abs(m.destination.x - closest_human_pos.x), abs(
            m.destination.y - closest_human_pos.y))  # calculate manhattan distance

        # If distance is closer, that's our new choice!
        if distance < move_distance:
            move_distance = distance
            move_choice = m
    # if close_water_in_relative_direction(character.position, 5,
    #                                      relative_direction(character.position, closest_human_pos), game_state):
    #     pos_move_choice = find_next_tile(character.position, closest_human_pos, 5, game_state)
    #     possible_move_choices = [move for move in possible_moves if
    #                              move.destination.x == pos_move_choice.x and move.destination.y == pos_move_choice.y]
    #
    #     if len(possible_move_choices) > 0:
    #         move_choice = possible_move_choices[0]
    return move_choice


def decide_attack(character: Character, possible_attacks: list[AttackAction], game_state: GameState,
                  other_attacks: list[AttackAction]) -> AttackAction | None:
    humans: list[Character] = [h for h in game_state.characters.values() if not h.is_zombie and should_attack(h, [oa for oa in other_attacks if oa.type == AttackActionType.CHARACTER])]
    pos_attacks: list[AttackAction] = [a for a in possible_attacks if [h.id for h in humans].__contains__(a.attacking_id)]
    if len(pos_attacks) == 0:
        pos_attacks = possible_attacks
    best_attack: AttackAction = pos_attacks[0]
    lowest_attack_health = \
    (game_state.characters if best_attack.type == AttackActionType.CHARACTER else game_state.terrains)[best_attack.attacking_id].health
    for attack in pos_attacks:
        health = (game_state.characters if attack.type == AttackActionType.CHARACTER else game_state.terrains)[
            attack.attacking_id].health
        if (lowest_attack_health > health > 0 and (best_attack.type == attack.type)) or (
                best_attack.type == AttackActionType.TERRAIN and attack.type == AttackActionType.CHARACTER):
            best_attack = attack
            lowest_attack_health = health
    return best_attack
