from dataclasses import dataclass, field
from typing import List
import datetime
import re
from defines import UNKNOWN, DEBT, CRED
import pandas as pd


@dataclass
class SingleRecord:
    """
    Single record parser.
    Gathers record attrs from list of strings (one record section from FileWorker).
    """
    data: List[str] = field(repr=False)
    date_time: datetime.datetime = field(default=None)
    time_operation: str = field(default='', repr=False)
    amount: float = field(default=0.00)
    debt: float = field(default=0.00)
    cred: float = field(default=0.00)
    doc_type: str = field(default='')  # payment document type
    doc_number: str = field(default='')  # payment document id
    ca_name: str = field(default='')  # counterparty description/name
    ca_code: str = field(default='')  # counterparty tax identification number
    ca_bank: str = field(default='')  # counterparty bank code
    ca_acc: str = field(default='')  # counterparty bank account number
    ca_iban: str = field(default='')  # counterparty IBAN
    description: str = field(default='')  # payment description
    direction: int = field(default=0)  # money direction (debt/cred)

    def __post_init__(self):
        self._parse_main_row()
        self.amount = round(self.debt + self.cred, 2)
        self.date_time += pd.to_timedelta(self.time_operation)
        self._set_direction()
        self._set_ca_name()
        self._set_description()
        self._set_ca_bank()

    def _parse_main_row(self):
        row = self.data[0].split('\t')
        self.date_time = pd.to_datetime(row[0], dayfirst=True)
        self.time_operation = row[1]
        self.doc_type = row[2]
        self.doc_number = row[4]
        self.ca_bank = row[6]
        self.ca_acc = row[7].split('.')[0]
        self.ca_iban = row[8]
        self.ca_code = row[9]
        try:
            debt = row[11].strip().replace(',', '.').replace(' ', '')
            if debt == '':
                self.debt = 0.00
            else:
                self.debt = round(float(debt), 2)
        except ValueError:
            self.debt = 0.00
            print(f'Debt error: \norigin-|{row[11]}|\nloaded |{self.debt}|')

        try:
            cred = row[12].strip().replace(',', '.').replace(' ', '')
            if cred == '':
                self.cred = 0.00
            else:
                self.cred = round(float(cred), 2)
        except ValueError:
            self.cred = 0.00
            print(f'Cred error: \norigin-|{row[12]}| \nloaded |{self.cred}|')

    def _set_ca_name(self):
        for ix in range(len(self.data)):
            if self.data[ix].startswith('КОРЕСПОНДЕНТ:'):
                string = self.data[ix]
                string = string.strip().split('\t', maxsplit=1)[1].replace('\t', ' ').strip()
                string = re.sub(' +', ' ', string)
                self.ca_name = string

    def _set_description(self):
        for ix in range(len(self.data)):
            if self.data[ix].startswith('ПРИЗНАЧЕННЯ:'):
                string = self.data[ix]
                string = string.strip().split('\t', maxsplit=1)[1].replace('\t', ' ').strip()
                string = re.sub(' +', ' ', string)
                self.description = string

    def _set_ca_bank(self):
        for ix in range(len(self.data)):
            if self.data[ix].startswith('БАНК:'):
                string = self.data[ix]
                string = string.strip().split('\t', maxsplit=1)[1].replace('\t', ' ').strip()
                string = re.sub(' +', ' ', string)
                self.ca_bank = string

    def _set_direction(self):
        if self.cred == 0.00:
            self.direction = DEBT
        elif self.debt == 0.00:
            self.direction = CRED
        else:
            self.direction = UNKNOWN

    def get_record_lst(self):
        return [self.date_time,
                self.amount,
                self.direction,
                self.debt,
                self.cred,
                self.description,
                self.doc_type,
                self.doc_number,
                self.ca_name,
                self.ca_code,
                self.ca_bank,
                self.ca_acc,
                self.ca_iban]

    def get_amount(self):
        return self.amount
