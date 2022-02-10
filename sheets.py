import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

def get_sh():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sh = client.open("family")

    return sh

def get_centered_str(cell, max_len):
    cell_len = len(cell)
    left_count = (max_len - cell_len)//2
    right_count = (max_len - cell_len) - left_count
    left_buf = " " + " " * left_count
    right_buf = " " * right_count + " "
    return left_buf + cell + right_buf

def n2a(n):
    a = ""

    while n != 0:
        ch = chr(ord('@')+(n%26))
        if ch == '@':
            ch = 'Z'
            n -= 26

        a = ch + a
        n = (n - n%26) // 26
    
    return a

def get_acell(row, col):
    return n2a(col) + str(row)

def get_cell(acell):
    row = int(re.findall(r'\d+', acell)[0])

    i = 1
    while not acell[:-i].isalpha():
        i += 1

    acol = acell[:-i]

    mult = 1
    col = 0
    while acol > "":
        val = ord(acol[-1]) - ord('@')
        col += val * mult
        mult = mult * 26
        acol = acol[:-1]

    return row, col

############################################################################
#                             - PRINT METHODS -                            #
############################################################################

def print_row(row):
    row_str = ""
    for cell in row:
        row_str += " " + cell + " |"

    return row_str[:-1] + "\n"

def print_col(col):
    max_len = 0
    for cell in col:
        max_len = max(max_len, len(cell))

    col_str = ""

    for cell in col:
        col_str += get_centered_str(cell, max_len) + "\n"

    return col_str

# assumes the top row is header row
def print_table(table, header=True, ruler=False):
    rows = len(table)
    cols = len(table[0])

    max_lens = []

    for i in range(cols):
        max_len = 0
        for row in table:
            max_len = max(max_len, len(row[i]))

        max_lens.append(max_len)

    table_str = ""

    if ruler:
        table_str += " " * 5 + "|"

        for i in range(1, cols+1):
            if max_lens[i-1] == 0:
                table_str += "  |"
            else:
                table_str += get_centered_str(n2a(i), max_lens[i-1]) + "|"

        table_str = table_str[:-1] + "\n"

    for index, row in enumerate(table):
        if ruler:
            table_str += get_centered_str(str(index+1), 3) + "|"

        for i in range(cols):    
            table_str += get_centered_str(row[i], max_lens[i]) + "|"
        
        table_str = table_str[:-1] + "\n"

        if header and row == table[0]:
            if ruler:
                table_str += "-----+"

            for i in range(cols):
                table_str += "-" * (max_lens[i] + 2) + "+"

            table_str = table_str[:-1] + "\n"

    print(table_str)

############################################################################
#                             - READ METHODS -                             #
############################################################################

def get_cell(ws, row, col):
    return ws.cell(row, col).value

def get_row(ws, row):
    return ws.row_values(row)

def get_col(ws, col):
    return ws.col_values(col)

def find_row(ws, text, header=False):
    if ws == None:
        return

    cells = ws.findall(re.compile(text, re.IGNORECASE))

    if cells == None:
        return

    vals = []
    if header:
        vals.append(ws.row_values(1))

    for cell in cells:
        vals.append(ws.row_values(cell.row))
    
    print(print_table(vals, header=header))

def find_col(ws, text):
    if ws == None:
        return

    cells = ws.findall(re.compile(text, re.IGNORECASE))

    if cells == None:
        return

    for cell in cells:
        print(ws.col_values(cell.col))
