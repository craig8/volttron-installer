class ProgramRegistry:
    _registry = {}

    @classmethod
    def register(cls, program_tile, key):
        cls._registry[key] = program_tile

    @classmethod
    def get_program_tile(cls, key):
        return cls._registry.get(key)

    @classmethod
    def update_activity(cls, key, activity):
        program_tile = cls.get_program_tile(key)
        if program_tile:
            program_tile.activity = activity
            program_tile.update_program_tile_ui()
