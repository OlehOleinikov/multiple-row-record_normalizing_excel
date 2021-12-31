import pandas as pd
import xlrd

from RecordsWalker import SingleRecord
from defines import UNKNOWN, DEBT, CRED


class FileWorker:
    """
    - Parse file data
    - Gather acc owner info
    - Clean tech and rudiment rows
    - Divide rows to record-data parts
    """
    def __init__(self, path):
        self.path = path
        self.data = None
        self.owner_name = None
        self.owner_id_number = None
        self.owner_iban = None
        self.owner_account = None
        self.currency = None
        self._load_file_data()
        self._title_owner_info()
        self._clean_head_text()

        self.records_positions = self._get_records_borders()
        self.records_instances = []
        self._covert_all_records()

        self.records_array_data = []
        self._gather_records_lst()
        self.df = pd.DataFrame()

    def _load_file_data(self):
        """
        Loads file contents as list of strings (row-by-row).
        Updates an data attribute.
        """
        xlrd.xlsx.ensure_elementtree_imported(False, None)
        xlrd.xlsx.Element_has_iter = True

        all_data = []
        excel = xlrd.open_workbook(self.path)
        sheet_0 = excel.sheet_by_index(0)  # load single sheet
        for row_num in range(sheet_0.nrows):
            line_lst = [str(x) for x in sheet_0.row_values(row_num)]
            all_data.append('\t'.join(line_lst))
        self.data = all_data

    def _clean_head_text(self):
        """
        Removes rows before records real data.
        Updates an instance data attribute.
        """
        for pos in range(len(self.data[:15])):
            if self.data[pos].startswith('Дата'):
                self.data = self.data[pos:]
                break

    def _title_owner_info(self):
        """
        Gathers account owner info. Based on the relative position of the attributes in the text.
        Updates instance attributes:

        - owner's name
        - owner's tax identification number
        - owner's IBAN
        - owner's account number
        - account currency
        """
        for pos in range(len(self.data)):
            if self.data[pos].startswith('Назва'):
                string = self.data[pos].split('\t')[2]
                string = string.strip()
                self.owner_name = string
                break
        for pos in range(len(self.data)):
            if self.data[pos].startswith('Рахунок'):
                string = self.data[pos].split('\t')
                self.owner_account = string[2].split('.')[0]
                self.currency = string[2].split('.')[1]
                self.owner_id_number = string[5].split(' ', maxsplit=1)[-1]
                break
        for pos in range(len(self.data)):
            if self.data[pos].startswith('IBAN'):
                self.owner_iban = (self.data[pos].strip()).split('\t')[2]
                break

    def _get_records_borders(self):
        """Gathers positions of each record. Based on date type value present."""
        border_signs = []
        for ix in range(len(self.data)):
            try:
                string = self.data[ix].split('\t')[0]
                date = pd.to_datetime(string, dayfirst=True, errors="raise")
            except ValueError:
                date = None
            if date:
                border_signs.append(ix)
        return border_signs

    def _covert_all_records(self):
        """Create list of records instances"""
        for pos in range(len(self.records_positions) - 1):
            current_rec = SingleRecord(self.data[self.records_positions[pos]:self.records_positions[pos + 1]])
            self.records_instances.append(current_rec)

    def _gather_records_lst(self):
        """Gather data from each record instances for dataframe creation"""
        for rec in self.records_instances:
            self.records_array_data.append(rec.get_record_lst())

    def extract_pandas(self):
        columns = ["date_time",
                   "amount",
                   "direction",
                   "debt",
                   "cred",
                   "description",
                   "doc_type",
                   "doc_number",
                   "ca_name",
                   "ca_code",
                   "ca_bank",
                   "ca_acc",
                   "ca_iban"]
        self.df = pd.DataFrame(data=self.records_array_data, columns=columns)
        self.df['owner_name'] = self.owner_name
        self.df['owner_id_number'] = self.owner_id_number
        self.df['owner_iban'] = self.owner_iban
        self.df['owner_account'] = self.owner_account
        self.df['currency'] = self.currency
        direction_dict = {UNKNOWN: 'unknown',
                          DEBT: 'debit',
                          CRED: 'credit'}
        self.df['direction'] = self.df['direction'].map(direction_dict)
        return self.df
