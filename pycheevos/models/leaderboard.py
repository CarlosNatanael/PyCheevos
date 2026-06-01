from typing import List, Union
from pycheevos.core.condition import Condition
from pycheevos.core.constants import LeaderboardFormat

class Leaderboard:
    def __init__(
        self,
        title: str,
        description: str,
        id: int = 0,
        format: LeaderboardFormat = LeaderboardFormat.SCORE,
        lower_is_better: bool = False
    ):
        self.id = id
        self.title = title
        self.description = description
        self.format = format
        self.lower_is_better = lower_is_better

        self.start: List[List[Condition]] = []
        self.cancel: List[List[Condition]] = []
        self.submit: List[List[Condition]] = []
        self.value: List[List[Condition]] = []

    def _flatten(self, items) -> List[Condition]:
        flat_list = []
        if not isinstance(items, list) and not isinstance(items, tuple):
            items = [items]
            
        for item in items:
            if isinstance(item, list) or isinstance(item, tuple):
                flat_list.extend(self._flatten(item))
            else:
                flat_list.append(item)
        return flat_list

    def _process_args(self, args) -> List[List[Condition]]:
        groups = []
        for arg in args:
            groups.append(self._flatten(arg))
        return groups

    def set_start(self, *conditions):
        self.start = self._process_args(conditions)
        return self

    def set_cancel(self, *conditions):
        self.cancel = self._process_args(conditions)
        return self

    def set_submit(self, *conditions):
        self.submit = self._process_args(conditions)
        return self

    def set_value(self, *conditions):
        self.value = self._process_args(conditions)
        return self

    def _render_group(self, conditions: List[Condition]) -> str:
        return "_".join([c.render() for c in conditions])

    def _render_all_groups(self, groups: List[List[Condition]]) -> str:
        if not groups: return ""
        return "S".join([self._render_group(g) for g in groups])

    def render(self) -> str:
        start = self._render_all_groups(self.start)
        cancel = self._render_all_groups(self.cancel)
        submit = self._render_all_groups(self.submit)
        value = self._render_all_groups(self.value)
        
        lower = "1" if self.lower_is_better else "0"

        return (
            f'L{self.id}:"{start}":"{cancel}":"{submit}":"{value}":'
            f'{self.format.value}:"{self.title}":{self.description}:{lower}'
        )