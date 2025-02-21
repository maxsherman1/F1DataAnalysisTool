from enum import Enum


class ResourceType(Enum):
    CIRCUITS = {"name": "Circuits", "optional": ["season", "round", "constructors", "drivers", "fastest", "grid", "results", "status"]}
    CONSTRUCTORS = {"name": "Constructors", "optional": ["season", "round", "circuits", "drivers", "fastest", "grid", "results", "status"]}
    CONSTRUCTORSTANDINGS = {"name": "Constructor Standings", "mandatory": ["season"], "optional": ["round", "constructors", "position"]}
    DRIVERS = {"name": "Drivers", "optional": ["season", "round", "circuits", "constructors", "fastest", "grid", "results", "status"]}
    DRIVERSTANDINGS = {"name": "Driver Standings", "mandatory": ["season"], "optional": ["round", "drivers", "position"]}
    LAPS = {"name": "Laps", "mandatory": ["season", "round"], "optional": ["drivers", "constructors", "laps"]}
    PITSTOPS = {"name": "Pit Stops", "mandatory": ["season", "round"], "optional": ["drivers", "laps", "pitstops"]}
    QUALIFYING = {"name": "Qualifying", "optional": ["season", "round", "circuits", "constructors", "drivers", "grid", "fastest", "status"]}
    RACES = {"name": "Races", "optional": ["season", "round", "circuits", "constructors", "drivers", "grid", "status"]}
    RESULTS = {"name": "Results", "optional": ["season", "round", "circuits", "constructors", "drivers", "fastest", "grid", "status"]}
    SEASONS = {"name": "Seasons", "optional": ["season", "circuits", "constructors", "drivers", "grid", "status"]}
    SPRINT = {"name": "Sprint", "optional": ["season", "round"]}
    STATUS = {"name": "Status", "optional": ["status", "season", "round", "circuits", "constructors", "drivers", "results"]}

    @property
    def name_value(self):
        return self.value.get("name", "")

    @property
    def mandatory(self):
        return self.value.get("mandatory", [])

    @property
    def optional(self):
        return self.value.get("optional", [])

    @classmethod
    def has_value(cls, value):
        return value in cls._member_names_

    @classmethod
    def get_all_names(cls):
        return [e.name_value for e in cls]

    @classmethod
    def get_optional(cls, resource_type):
        return cls[resource_type.upper()].optional

    @classmethod
    def get_mandatory(cls, resource_type):
        return cls[resource_type.upper()].mandatory