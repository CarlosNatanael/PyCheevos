from typing import List, Union
from pycheevos.core.condition import Condition
from pycheevos.core.constants import AchievementType

class Achievement:
    def __init__(self, title: str, description: str, points: int, id: int = 0, badge: str = "", type: Union[AchievementType, str] = AchievementType.STANDARD):
        self.id = id
        self.title = title
        self.description = description
        self.points = points
        self.badge = badge

        if isinstance(type, AchievementType):
            self.type = type.value
        else:
            self.type = type

        self.author = "PyCheevos"
        self.core: List[Condition] = []
        self.alts: List[List[Condition]] = []
        self.conditions: List[Condition] = []

    def _flatten(self, items) -> List[Condition]:
        flat_list = []

        if not isinstance(items, list):
            items = [items]
        for item in items:
            if isinstance(item, list):
                flat_list.extend(self._flatten(item))
            else:
                flat_list.append(item)
        return flat_list
    
    def add_core(self, conditions: Union[Condition, List]):
        self.core.extend(self._flatten(conditions))
        return self
    
    def add_alt(self, conditions: Union[Condition, List]):
        self.alts.append(self._flatten(conditions))
        return self

    def add_condition(self, condition: Condition):
        self.conditions.append(condition)
        return self

    def add_conditions(self, conditions: List[Condition]):
        self.conditions.extend(self._flatten(conditions))
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
            
        safe_title = self.title.replace('"', '\\"')
        safe_desc = self.description.replace('"', '\\"')
        badge_str = f"{self.badge}" if self.badge and self.badge != "00000" else ""
        
        return (
            f'{self.id}:"{full_mem}":"{safe_title}":"{safe_desc}"'
            f':::{self.type}:{self.author}:{self.points}:::::{badge_str}'
        )