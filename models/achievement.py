from typing import List, Union
from core.condition import Condition

class Achievement:
    def __init__(self, title: str, description: str, points: int, id: int = 1, badge: str = "00000"):
        self.id = id
        self.title = title
        self.description = description
        self.points = points
        self.badge = badge
        self.author = "PyCheevos"
        self.core: List[Condition] = []
        self.alts: List[List[Condition]] = []
        self.conditions: List[Condition] = []

    def _flatten(self, items) -> List[Condition]:
        flat_list = []
        for item in items:
            if isinstance(item, list):
                flat_list.extend(self._flatten(item))
            else:
                flat_list.append(item)
        return flat_list

    def add_core(self, conditions: Union[Condition, List]):
        if not isinstance(conditions, list):
            conditions = [conditions]
        self.core.extend(self._flatten(conditions))
        return self
    
    def add_alt(self, conditions: Union[Condition, List]):
        if not isinstance(conditions, list):
            conditions = [conditions]
        self.alts.append(self._flatten(conditions))
        return self

    def add_condition(self, condition: Condition):
        self.conditions.append(condition)
        return self

    def add_conditions(self, conditions: List[Condition]):
        self.conditions.extend(conditions)
        return self

    def _render_group(self, conditions: List[Condition]) -> str:
        return "_".join([c.render() for c in conditions])

    def render(self) -> str:
        if self.conditions:
            self.core.extend(self.conditions)
            self.conditions = []

        core_string = self._render_group(self.core)
        
        if self.alts:
            alt_strings = [self._render_group(alt) for alt in self.alts]
            full_mem = core_string + "S" + "S".join(alt_strings)
        else:
            full_mem = core_string
        
        return (
            f'{self.id}:"{full_mem}":{self.title}:{self.description}'
            f'::::{self.author}:{self.points}:::::{self.badge}'
        )