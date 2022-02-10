import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

class Person:
    
    def __init__(self, first, last, full, father, mother, spouse, sex, living, location, birthyear, deathyear):
        self.first = first
        self.last = last
        self.full = full
        self.father = father
        self.mother = mother
        self.spouse = spouse
        self.sex = sex
        self.living = living
        self.location = location
        self.birthyear = birthyear
        self.deathyear = deathyear

        self.spouses = {}

    def __repr__(self): 
        return f'{self.first}, {self.last}, {self.full}, {self.father}, {self.mother}, {self.spouse}, {self.sex}, {self.living}, {self.location}, {self.birthyear}, {self.deathyear}, {self.spouses}\n'

    def add_spouse(self, spouse):
        if (spouse != "-") and (spouse not in self.spouses):
            self.spouses[spouse] = []

    def add_child(self, parent2, child):
        if child not in self.spouses[parent2]:
            self.spouses[parent2].append(child)
    
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

############################################################################
#                             - TREE METHODS -                             #
############################################################################

def get_alpha_spouse(name1, name2, separator="_"):
    if separator != "_":
        pair = [name1.replace(' ', '_'), name2.replace(' ', '_')]
    else:
        pair = [name1, name2]

    pair.sort()
    return pair[0] + separator + pair[1]

def insert_spouse(people, generations, person, depth, spouse_name, index):
    spouse = people[spouse_name]
    if spouse not in generations[depth]:
        generations[depth].insert(generations[depth].index(person)+index, spouse)

        joint = get_alpha_spouse(person.full, spouse.full, "__")
        joint_children = person.spouses[spouse.full]
        tup = (joint, joint_children)
        generations[depth].insert(generations[depth].index(person)+index, tup)

def sheet_to_data(rootname, display=False):
    sh = get_sh()
    ws = sh.worksheet("family")

    vals = ws.get_all_values()
    rows = len(vals)
    cols = len(vals[0])

    people = {}

    # loop over all the rows in the google sheet
    for i in range(1, rows):
        row = vals[i]

        # fetch data
        first = row[0]
        last = row[1]
        full = row[2]
        father = row[3]
        mother = row[4]
        spouse = row[5]
        sex = row[6]
        life = row[7]
        location = row[8]
        birth = row[9]
        death = row[10]

        individual = Person(first, last, full, father, mother, spouse, sex, life, location, birth, death)

        people[full] = individual

    if people[rootname] == None:
        print("that root does not exist...")
        exit()

    generations = {0: []}
    root = people[rootname]
    generations[0].append(root)

    for name, person in people.items():
        if person.spouse != "-":
            people[person.spouse].add_spouse(name)
            people[name].add_spouse(person.spouse)

    for name, person in people.items():
        if person.father != "-" and person.mother != "-":
            people[person.father].add_child(person.mother, name)
            people[person.mother].add_child(person.father, name)

    depth = 0
    while len(generations[depth]) != 0:

        myrange = list(range(len(generations[depth])))
        myrange.reverse()

        for i in myrange:

            person = generations[depth][i]

            # insert all the spouses in tree
            if len(person.spouses) == 0:
                continue
            else:
                if len(person.spouses) == 1:
                    for spouse_name in person.spouses:
                        insert_spouse(people, generations, person, depth, spouse_name, 1)
                else:
                    last = None

                    for spouse_name in person.spouses:
                        if last != None:
                            insert_spouse(people, generations, person, depth, last, 0)
                        
                        last = spouse_name

                    insert_spouse(people, generations, person, depth, last, 1)

        depth += 1
        generations[depth] = []

        for person in generations[depth-1]:
            if isinstance(person, tuple):
                continue

            for spouse in person.spouses:
                for child_name in person.spouses[spouse]:
                    child = people[child_name]
                    if child not in generations[depth]:
                        generations[depth].append(child)

    generations.pop(depth)
        
    if display:
        print(f'people = {people}')
        print(f'generations = {generations}')

        print_table(vals, ruler=False)

    return people, generations
