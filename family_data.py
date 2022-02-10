import sheets

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

def get_family_data(rootname, display=False):
    sh = sheets.get_sh()
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

        sheets.print_table(vals, ruler=False)

    return people, generations
