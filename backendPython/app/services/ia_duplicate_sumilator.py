import joblib
from pydantic import BaseModel

class DuplicateSimulator(BaseModel):
    segment: str
    @property
    def segment(self):
        return self.segment

    @segment.setter
    def segment(self, value):
        self.segment = value