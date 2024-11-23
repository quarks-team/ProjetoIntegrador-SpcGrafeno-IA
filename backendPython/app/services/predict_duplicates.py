import joblib
from pydantic import BaseModel

active_model = joblib.load('app\\services\\active_predict.joblib')
finished_model = joblib.load('app\\services\\finished_predict.joblib')
canceled_model = joblib.load('app\\services\\canceled_predict.joblib')

class PredictDuplicate(BaseModel):
    day : int
    duplicate_state : str

    def day(self, value):
        self._day = value

    def duplicate_state(self, value):
        self._duplicate_state = value

    def day(self):
        return self.day
    
    def duplicate_state(self):
        return self.duplicate_state

    def predict_duplicates_future(self):
        match self.duplicate_state:
            case 'active':
                next = active_model.make_future_dataframe(periods=self.day, freq='D')
                forecast = active_model.predict(next)
                return forecast
            case 'finished':
                next = finished_model.make_future_dataframe(periods=self.day, freq='D')
                forecast = finished_model.predict(next)
                return forecast
            case 'canceled':
                next = canceled_model.make_future_dataframe(periods=self.day, freq='D')
                forecast = canceled_model.predict(next)
                return forecast
        
            case 'all':
                next = active_model.make_future_dataframe(periods=self.day, freq='D')
                forecast_active = active_model.predict(next)

                next = finished_model.make_future_dataframe(periods=self.day, freq='D')
                forecast_finished = finished_model.predict(next)

                next = canceled_model.make_future_dataframe(periods=self.day, freq='D')
                forecast_canceled = canceled_model.predict(next)

                return {"active":forecast_active, 
                        "finished":forecast_finished,
                        "canceled": forecast_canceled}
            case _:
                return 'Is not a valid quantity of days or duplicate state'