from inspect import getmembers, isfunction
from types import ModuleType

class Plugin:
    def __init__(self, mod: ModuleType, is_active=True):
        self.mod_name = mod.__name__
        self.methods = [
            x for x in getmembers(mod) if isfunction(x[1])
        ]
        self.is_active = is_active
    
    def __repr__(self) -> str:
        return f"Plugin: {self.mod_name}, " \
               f"{len(self.methods)} method(s), " \
               f"Is Active: {self.is_active}"
    
    def check_endpoint_active(self, endpoint_name: str) -> bool:
        if endpoint_name in [
                    x[1].__name__
                    for x in self.methods
                ]:
            return self.is_active
        return True