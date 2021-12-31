import os
from tqdm import tqdm

from FileWorker import FileWorker
from file_table import print_files_table


if __name__ == "__main__":
    files_in_dir = [x for x in os.listdir() if (x.endswith('.xlsx')) and (not(x.startswith('~$')))]
    print_files_table(files_in_dir)

    for file_path in tqdm(files_in_dir):
        cur_file = FileWorker(file_path)
        df = cur_file.extract_pandas()
        df.to_excel(f"format_{file_path.split('.')[0]}.xlsx", index=False)





