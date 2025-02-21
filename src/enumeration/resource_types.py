from enum import Enum

class ResourceType(Enum):
    CIRCUITS = {"optional": ["season", "round", "constructors", "drivers", "fastest", "grid", "results", "status"]}
    CONSTRUCTORS = {"optional": ["season", "round", "circuits", "drivers", "fastest", "grid", "results", "status"]}
    CONSTRUCTORSTANDINGS = {"mandatory": ["season"], "optional": ["round", "constructors", "position"]}
    DRIVERS = {"optional": ["season", "round", "circuits", "constructors", "fastest", "grid", "results", "status"]}
    DRIVERSTANDINGS = {"mandatory": ["season"], "optional": ["round", "drivers", "position"]}
    LAPS = {"mandatory": ["season", "round"], "optional": ["drivers", "constructors", "laps"]}
    PITSTOPS = {"mandatory": ["season", "round"], "optional": ["drivers", "laps", "pitstops"]}
    QUALIFYING = {"optional": ["season", "round", "circuits", "constructors", "drivers", "grid", "fastest", "status"]}
    RACES = {"optional": ["season", "round", "circuits", "constructors", "drivers", "grid", "status"]}
    RESULTS = {"optional": ["season", "round", "circuits", "constructors", "drivers", "fastest", "grid", "status"]}
    SEASONS = {"optional": ["season", "circuits", "constructors", "drivers", "grid", "status"]}
    SPRINT = {"optional": ["season", "round"]}
    STATUS = {"optional": ["status", "season", "round", "circuits", "constructors", "drivers", "results"]}

    @property
    def mandatory(self):
        return self.value.get("mandatory", [])

    @property
    def optional(self):
        return self.value.get("optional", [])

    @classmethod
    def has_value(cls, value):
        return value in cls._member_names_

class ResourceHandler:
    def __init__(self, resource_type):
        if not ResourceType.has_value(resource_type.upper()):
            raise ValueError(f"Invalid resource type: {resource_type}. Must be one of {[e.name.lower() for e in ResourceType]}")

        self.resource_type = ResourceType[resource_type.upper()]

    def get_filters(self):
        return {
            "mandatory": self.resource_type.mandatory,
            "optional": self.resource_type.optional
        }