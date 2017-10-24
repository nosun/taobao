import csv

def write_dict_to_csv(data_, filename, mode='a'):
    data_new = [(k, v) for k, v in data_.items()]
    write_list_to_csv(data_new, filename, mode)


def write_list_to_csv(data_, filename, mode='a'):
    filename = filename if filename.endswith(".csv") else filename + '.csv'
    with open(filename, mode, newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(data_)


def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
    return lines
