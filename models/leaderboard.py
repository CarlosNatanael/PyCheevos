from typing import List, Union
from core.condition import Condition
from core.constants import LeaderboardFormat

class Leaderboard:
    def __init__(
        self,
        title: str,
        description: str,
        id: int = 11100001,
        format: LeaderboardFormat = LeaderboardFormat.SCORE,
        lower_is_better: bool = False
    ):
        self.id = id
        self.title = title
        self.description = description
        self.format = format
        self.lower_is_better = lower_is_better

        self.start: List[Condition] = []
        self.cancel: List[Condition] = []
        self.submit: List[Condition] = []
        self.value: List[Condition] = []

    def _flatten(self, items) -> List[Condition]:
        flat_list = []
        for item in items:
            if isinstance(item, list):
                flat_list.extend(self._flatten(item))
            else:
                flat_list.append(item)
        return flat_list
    
    def set_start(self, conditions: Union[Condition, List]):
        if not isinstance(conditions, list):
            print()