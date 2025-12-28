from core.helpers import byte, delta

class GameObject:
    """
    Base class for game objects
    It automatically handles static addresses and pointers
    """
    def __init__(self, address):
        self.base_address = address

    def offset(self, offset_val: int, type_func=byte):
        """
        Returns the memory access by adding the offset to the base address
        It works for both static RAM (int) and pointers (MemoryValue)
        """
        # If the base address is a fixed number (e.g., 0x00100)
        if isinstance(self.base_address, int):
            return type_func(self.base_address + offset_val)
        
        # If the base address is a pointer (MemoryValue object)
        # Use the >> operator to create the AddAddress logic.
        return self.base_address >> type_func(offset_val)