from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.character.character import Character
from game.character.character_class_type import CharacterClassType
from game.game_state import GameState
from strategy.strategy import Strategy
import strategy.controllers.normal_controller as normal_controller
import strategy.controllers.medic_controller as medic_controller
import strategy.controllers.builder_controller as builder_controller
import strategy.controllers.traceur_controller as traceur_controller
import strategy.controllers.marksman_controller as marksman_controller
import strategy.controllers.demolitionist_controller as demolitionist_controller


def selection_statement(character_class):
    """
    takes the handlers and returns the correct handler based on the character class
    """
    if character_class == CharacterClassType.NORMAL:
        controller = normal_controller
    elif character_class == CharacterClassType.TRACEUR:
        controller = traceur_controller
    elif character_class == CharacterClassType.MEDIC:
        controller = medic_controller
    elif character_class == CharacterClassType.BUILDER:
        controller = builder_controller
    elif character_class == CharacterClassType.MARKSMAN:
        controller = marksman_controller
    else:
        controller = demolitionist_controller
    return controller


class HumanStrategy(Strategy):
    def decide_character_classes(
            self,
            possible_classes: list[CharacterClassType],
            num_to_pick: int,
            max_per_same_class: int,
    ) -> dict[CharacterClassType, int]:
        return {
            # CharacterClassType.MEDIC: 5,
            # CharacterClassType.BUILDER: 5,
            # CharacterClassType.TRACEUR: 4,
            # CharacterClassType.DEMOLITIONIST: 2

            CharacterClassType.TRACEUR: 5,
            CharacterClassType.DEMOLITIONIST: 5,
            CharacterClassType.MEDIC: 4,
            CharacterClassType.MARKSMAN: 2
        }

    def decide_moves(
            self, possible_moves: dict[str, list[MoveAction]], game_state: GameState
    ) -> list[MoveAction]:
        result: list[MoveAction] = []
        moves: list[MoveAction]
        for character_id, moves in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue
            character: Character = game_state.characters.get(character_id)
            result.append(selection_statement(character.class_type).decide_move(character, possible_moves[character_id],
                                                                                game_state, result))
        result = [action for action in result if action is not None]
        return result

    def decide_attacks(
            self, possible_attacks: dict[str, list[AttackAction]], game_state: GameState
    ) -> list[AttackAction]:
        result: list[AttackAction] = []
        attacks: list[AttackAction]
        for character_id, attacks in possible_attacks.items():
            if len(attacks) == 0:  # No choices... Next!
                continue
            character: Character = game_state.characters.get(character_id)
            result.append(
                selection_statement(character.class_type).decide_attack(character, possible_attacks[character_id],
                                                                        game_state, result))
        result = [action for action in result if action is not None]
        return result

    def decide_abilities(
            self, possible_abilities: dict[str, list[AbilityAction]], game_state: GameState
    ) -> list[AbilityAction]:
        result: list[AbilityAction] = []
        abilities: list[AbilityAction]
        for character_id, abilities in possible_abilities.items():
            if len(abilities) == 0:  # No choices... Next!
                continue
            character: Character = game_state.characters.get(character_id)
            result.append(
                selection_statement(character.class_type).decide_ability(character, possible_abilities[character_id],
                                                                         game_state, result))
        result = [ability for ability in result if ability is not None]
        return result
