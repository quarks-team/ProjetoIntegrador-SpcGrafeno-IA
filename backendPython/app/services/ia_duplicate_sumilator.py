import joblib
from pydantic import BaseModel


model_simulator = joblib.load('app\\services\\rand_search_model.joblib')
scaler_simulator = joblib.load('app\\services\\scaler_simulator.pkl')

class DuplicateSimulator(BaseModel):
    segment: str
    month:int
    quarter:int
    area:list 
    date: str
    created_date: str
    state: str
    @property
    def segment(self):
        return self.segment

    @segment.setter
    def segment(self, value):
        self.segment = value
    
    @property
    def month(self):
        return self.month

    @month.setter
    def month(self, value):
        self.month = value

    @property
    def quarter(self):
        return self.quarter

    @quarter.setter
    def quarter(self, value):
        self.quarter = value
    
    @property
    def area(self):
        return self.area

    @area.setter
    def area(self, value):
        self.area = value

    @property
    def date(self):
        return self.date

    @date.setter
    def date(self, value):
        self.date = value
    
    @property
    def created_date(self):
        return self.created_date

    @created_date.setter
    def created_date(self, value):
        self.created_date = value
    
    @property
    def state(self):
        return self.state

    @state.setter
    def state(self, value):
        self.state = value