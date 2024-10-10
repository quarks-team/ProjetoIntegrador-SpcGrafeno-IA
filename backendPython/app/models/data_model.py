# app/models/data_model.py

from pydantic import BaseModel

class DataModel(BaseModel):
    dia: str
    saldo_dia_ant: int
    entrada: int
    total_acumulado: int
    saida: int
    saida_acumulada: int
    resultado: int

    def to_tuple(self):
        return (self.dia, self.saldo_dia_ant, self.entrada,
                self.total_acumulado, self.saida,
                self.saida_acumulada, self.resultado)
