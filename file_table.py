import os
from rich.table import Table
from rich.console import Console


def print_files_table(files: list):
    files_info = []
    for file in files:
        file_name = os.path.basename(file)
        file_size = str(round(os.path.getsize(file) / 1024.0)) + ' Kb'
        file_path = os.path.abspath(file)
        files_info.append([file_name, file_size, file_path])

    table = Table(title='Files loading')
    table.add_column('№')
    table.add_column('File')
    table.add_column('Size', justify='right')
    table.add_column('Path')

    console = Console()
    for pos in range(len(files_info)):
        files_to_print = [str(pos+1), files_info[pos][0], files_info[pos][1], files_info[pos][2]]
        table.add_row(*files_to_print)
    console.print(table, justify='center')
