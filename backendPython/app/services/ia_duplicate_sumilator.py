import joblib
from pydantic import BaseModel


model_simulator = joblib.load('app\\services\\rand_search_model.joblib')
scaler_simulator = joblib.load('app\\services\\scaler_simulator.pkl')
class DuplicateSimulator(BaseModel):
    segment: str
    month:int
    quarter:int
    area:list 
    created_date: str
    @property
    def segment(self):
        return self.segment

    @segment.setter
    def segment(self, value):
        self.segment = value