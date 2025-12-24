from typing import List
from core.condition import Condition

class Achievement:
    def __init__(
        self, 
        title: str, 
        description: str, 
        points: int, 
        id: int = 1, 
        badge: str = "00000"
    ):
        self.id = id
        self.title = title
        self.description = description
        self.points = points
        self.badge = badge
        self.author = "PyCheevos"

        self.core: List[Condition] = []
        self.alts: List[List[Condition]] = []
        self.conditions: List[Condition] = []

    def add_core(self, conditions: List[Condition]):
        if isinstance(conditions, List):
            self.core.extend(conditions)
        else:
            self.core.extend(conditions)
        return self
    
    def add_alt(self, conditions: List[Condition]):
        if isinstance(conditions, list):
            self.alts.append(conditions)
        else:
            self.alts.append([conditions])
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
        core_string = self._render_group(self.core)
        if self.alts:
            alt_strings = (self._render_group(alt) for alt in self.alts)
            full_mem = core_string + "S:" + "S:".join(alt_strings).replace("S:", ":")
            full_mem = core_string + ":" + ":".join(alt_strings)
        else:
            full_mem = core_string
        
        return (
            f'{self.id}:"{full_mem}":{self.title}:{self.description}'
            f'::::{self.author}:{self.points}:::::{self.badge}'
        )