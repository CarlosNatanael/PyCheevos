from core.helpers import byte, word, dword

class GameObject:
    def __init__(self, address):
        self.base_address = address

    def offset(self, offset_val: int, type_func=byte):
        if isinstance(self.base_address, int):
            return type_func(self.base_address + offset_val)
        
        return self.base_address >> type_func(offset_val)
    