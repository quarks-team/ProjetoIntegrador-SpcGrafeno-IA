import joblib
from pydantic import BaseModel

model = joblib.load('app\\services\\model_score.pkl')
scaler = joblib.load('app\\services\\scaler.pkl')
base_with_names = joblib.load('app\\services\\base_with_names.pkl')

class InputData(BaseModel):
    renegotiation_delay_days : float
    segment_products_count : int
    segment_services_count : int
    ongoing_transactions : int
    voided_transactions : int
    successful_transactions : int
    non_voided_transactions : int
    median_installment_amount : float
    overall_transactions : int