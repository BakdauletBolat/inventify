import dataclasses


@dataclasses.dataclass
class Credit:
    id: int
    name: str

    d


credit = Credit(id=1, name=2)

print(dataclasses.asdict(credit))
