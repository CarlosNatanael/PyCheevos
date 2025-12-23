from typing import List, Union
from core.condition import Condition

class Achievement:
    def __init__(
        self, 
        title: str, 
        description: str, 
        points: int, 
        id: int = 111000001,
        badge: str = "00000"
    ):
        self.id = id
        self.title = title
        self.description = description
        self.points = points
        self.badge = badge
        self.author = "PyCheevos"
        self.conditions: List[Condition] = []

    def add_condition(self, condition: Condition):
        self.conditions.append(condition)
        return self
    
    def add_conditions(self, conditions: list):
        self.conditions.extend(conditions)
        return self

    def render(self) -> str:
        mem_string = "_".join([c.render() for c in self.conditions])
        return (
            f'{self.id}:"{mem_string}":{self.title}:{self.description}:'
            f':::::{self.author}:{self.points}:::::{self.badge}'
        )
    
    def __str__(self):
        return self.render()