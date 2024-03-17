from dataclasses import dataclass


@dataclass
class Aircraft:
    """Aircraft class to store a single aircraft's details.
    """
    registration: str
    aircraft_id: int
    model: str
    max_range: int
    avg_speed: int
    turnaround_time: int
    capacity: dict

    def __str__(self):
        return f"{self.registration} {self.model}"
