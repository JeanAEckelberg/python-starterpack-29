from strategy.random_strategy import RandomStrategy
from strategy.simple_human_strategy import SimpleHumanStrategy
from strategy.simple_zombie_strategy import SimpleZombieStrategy
from strategy.strategy import Strategy
from strategy.human_strategy import HumanStrategy
from strategy.zombie_strategy import ZombieStrategy


def choose_strategy(is_zombie: bool) -> Strategy:
    # Modify what is returned here to select the strategy your bot will use
    # NOTE: You can use "is_zombie" to use two different strategies for humans and zombies (RECOMMENDED!)
    #
    # For example:
    if is_zombie:
        return ZombieStrategy()
    else:
        return HumanStrategy()

    # return RandomStrategy()
