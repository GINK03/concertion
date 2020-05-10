
from dataclasses import dataclass
from typing import NewType
from typing import List
from typing import Optional
@dataclass
class SignateRecord:
    title: str
    prize: str
    url: str
    limit_date: Optional[str]
    remaining_date: Optional[str]

SignateRecords = NewType("SignateRecords", List[SignateRecord])
