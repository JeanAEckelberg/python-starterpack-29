from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.character.character_class_type import CharacterClassType
from game.character.character import Character
from game.game_state import GameState
from strategy.strategy import Strategy
import strategy.controllers.zombie_controller as zombie_controller


class ZombieStrategy(Strategy):
    def decide_character_classes(
        self,
        possible_classes: list[CharacterClassType],
        num_to_pick: int,
        max_per_same_class: int,
    ) -> dict[CharacterClassType, int]:
        """
        This should never be called
        """
        return {}

    def decide_moves(
        self, possible_moves: dict[str, list[MoveAction]], game_state: GameState
    ) -> list[MoveAction]:
        result: list[MoveAction] = []
        for character_id, moves in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue
            character: Character = game_state.characters.get(character_id)
            result.append(zombie_controller.decide_move(character, moves, game_state, result))
        result = [action for action in result if action is not None]
        return result

    def decide_attacks(
        self, possible_attacks: dict[str, list[AttackAction]], game_state: GameState
    ) -> list[AttackAction]:
        result: list[AttackAction] = []
        for character_id, moves in possible_attacks.items():
            if len(moves) == 0:  # No choices... Next!
                continue
            character: Character = game_state.characters.get(character_id)
            result.append(zombie_controller.decide_attack(character, possible_attacks[character_id], game_state, result))
        result = [action for action in result if action is not None]
        return result

    def decide_abilities(
        self, possible_abilities: dict[str, list[AbilityAction]], game_state: GameState
    ) -> list[AbilityAction]:
        '''
        This should never be called
        '''
        return []