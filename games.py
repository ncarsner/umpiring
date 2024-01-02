from dataclasses import dataclass
from datetime import datetime


games = [
    ["2/28", "ccua_hs", "y", 1, "p"],
    ["3/11", "ccua_hs", "y", 2, "p"],
    ["3/23", "ll_minors", "y", 1, "v"],
    ["3/23", "ll_minors", "y", 1, "v"],
]

@dataclass
class Game:
    date: datetime.today().date()
    division: None == str
    assignor: None == str
    site: None == str
    mileage: None == float
    not_volunteer: True
    has_been_paid: False
