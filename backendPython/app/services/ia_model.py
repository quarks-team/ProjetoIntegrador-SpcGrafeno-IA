import joblib
from pydantic import BaseModel

model = joblib.load('app\\services\\model_score.pkl')
scaler = joblib.load('app\\services\\scaler.pkl')
base_with_names = joblib.load('app\\services\\base_with_names.pkl')

class InputData(BaseModel):
    renegotiation_delay_days : float
    segment_products_count : float
    segment_services_count : float
    ongoing_transactions : float
    voided_transactions : float
    successful_transactions : float
    non_voided_transactions : float
    median_installment_amount : float
    overall_transactions : float

    # Getter and Setter for renegotiation_delay_days
    @property
    def renegotiation_delay_days(self):
        return self._renegotiation_delay_days

    @renegotiation_delay_days.setter
    def renegotiation_delay_days(self, value):
        self._renegotiation_delay_days = value

    # Getter and Setter for segment_products_count
    @property
    def segment_products_count(self):
        return self._segment_products_count

    @segment_products_count.setter
    def segment_products_count(self, value):
        self._segment_products_count = value

    # Getter and Setter for segment_services_count
    @property
    def segment_services_count(self):
        return self._segment_services_count

    @segment_services_count.setter
    def segment_services_count(self, value):
        self._segment_services_count = value

    # Getter and Setter for ongoing_transactions
    @property
    def ongoing_transactions(self):
        return self._ongoing_transactions

    @ongoing_transactions.setter
    def ongoing_transactions(self, value):
        self._ongoing_transactions = value

    # Getter and Setter for voided_transactions
    @property
    def voided_transactions(self):
        return self._voided_transactions

    @voided_transactions.setter
    def voided_transactions(self, value):
        self._voided_transactions = value

    # Getter and Setter for successful_transactions
    @property
    def successful_transactions(self):
        return self._successful_transactions

    @successful_transactions.setter
    def successful_transactions(self, value):
        self._successful_transactions = value

    # Getter and Setter for non_voided_transactions
    @property
    def non_voided_transactions(self):
        return self._non_voided_transactions

    @non_voided_transactions.setter
    def non_voided_transactions(self, value):
        self._non_voided_transactions = value

    # Getter and Setter for median_installment_amount
    @property
    def median_installment_amount(self):
        return self._median_installment_amount

    @median_installment_amount.setter
    def median_installment_amount(self, value):
        self._median_installment_amount = value

    # Getter and Setter for overall_transactions
    @property
    def overall_transactions(self):
        return self._overall_transactions

    @overall_transactions.setter
    def overall_transactions(self, value):
        self._overall_transactions = value