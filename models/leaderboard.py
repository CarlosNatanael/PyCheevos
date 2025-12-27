from typing import List, Union
from core.condition import Condition
from core.constants import LeaderboardFormat

class Leaderboard:
    def __init__(
        self,
        title: str,
        description: str,
        id: int = 111000001,
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
        if not isinstance(conditions, list): conditions = [conditions]
        self.start = self._flatten(conditions)
        return self

    def set_cancel(self, conditions: Union[Condition, List]):
        if not isinstance(conditions, list): conditions = [conditions]
        self.cancel = self._flatten(conditions)
        return self

    def set_submit(self, conditions: Union[Condition, List]):
        if not isinstance(conditions, list): conditions = [conditions]
        self.submit = self._flatten(conditions)
        return self

    def set_value(self, conditions: Union[Condition, List]):
        if not isinstance(conditions, list): conditions = [conditions]
        self.value = self._flatten(conditions)
        return self

    def _render_group(self, conditions: List[Condition]) -> str:
        return "_".join([c.render() for c in conditions])

    def render(self) -> str:
        start = self._render_group(self.start)
        cancel = self._render_group(self.cancel)
        submit = self._render_group(self.submit)
        value = self._render_group(self.value)
        
        lower = "1" if self.lower_is_better else "0"

        return (
            f'L{self.id}:"{start}":"{cancel}":"{submit}":"{value}":'
            f'{self.format.value}:{self.title}:{self.description}:{lower}'
        )