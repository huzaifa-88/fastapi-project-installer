from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateUserInput:
    email: str
    full_name: str
