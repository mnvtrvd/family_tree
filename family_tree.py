from sheets_to_data import sheet_to_data
import os.path
import subprocess

ortho = False

def wr_line(f, str, num=1):
    f.write('\t'*num)
    f.write(str)
    f.write('\n')

def insert_person(f, person):
    shape = " [shape=box]"

    gender_color = ""
    if person.sex == 'M':
        gender_color = " [color=blue]"
    elif person.sex == 'F':
        gender_color = " [color=red]"
    else:
        gender_color = " [color=black]"

    color = ""
    if person.living == 'N':
        color = " [fillcolor=gray, style=filled]"
    else:
        country = "#ffffff"

        if person.location == "India":
            country = "#ffb080"
        elif person.location == "US":
            country = "#99d6ff"
        elif person.location == "UK":
            country = "#9999ff"
        elif person.location == "Canada":
            country = "#ff8080"
        elif person.location == "Australia":
            country = "#dfbe9f"
        
        color = f' [fillcolor="{country}", style=filled]'


    filename = "images/" + person.full.replace(' ', '_').lower()
    if os.path.isfile(f'{filename}.jpeg'):
        filename = filename + ".jpeg"
    elif os.path.isfile(f'{filename}.png'):
        filename = filename + ".png"
    else:
        filename = ""

    name_label = ""
    img = ""
    if filename != "":
        img = f' [label=<<TABLE border="0"><TR><TD width="75" height="75" fixedsize="true"><IMG SRC="{filename}" scale="true"/></TD></TR><TR><TD>{person.full}</TD></TR></TABLE>>]'
    else:
        name_label = f' [label="{person.full}"]'

    wr_line(f, person.full.replace(' ', '_') + name_label + shape + gender_color + color + img, num=2)
    

def insert_spouse_pair(f, pair):
    wr_line(f, f'{pair} [shape=point]', num=2)

def insert_conn(f, name1, name2):
    if "__" in name1 and "__" in name2:
        wr_line(f, f'{name1} -> {name2} [style = invisible]', num=2)

        _, spouse_name = name1.split("__")
        wr_line(f, f'{name1} -> {spouse_name}', num=2)

    elif "__" in name1 and name2 in name1:
        wr_line(f, f'{name1} -> {name2}', num=2)
    elif "__" in name2 and name1 in name2:
        wr_line(f, f'{name1} -> {name2}', num=2)
    else:
        wr_line(f, f'{name1} -> {name2} [style = invisible]', num=2)

def insert_order(f, generation):
    simple_gen = []
    for person in generation:
        if isinstance(person, tuple):
            simple_gen.append(person[0])
        else:
            simple_gen.append(person.full.replace(' ', '_'))

    for i, person in enumerate(simple_gen):
        if i == 0:
            continue
        else:
            first = simple_gen[i-1]
            second = person
            insert_conn(f, first, second)

def insert_children(f, parents, children):
    wr_line(f, "{")
    for child in children:
        child_id = child.replace(" ", "_")
        wr_line(f, f'{parents} -> {child_id}', num=2)
    wr_line(f, "}")

def insert_ortho_children(f, parents, children):
    if len(children) == 1:
        wr_line(f, "{")
        for child in children:
            wr_line(f, f'{parents} -> {child}', num=2)
        wr_line(f, "}")
    else:
        # create hidden nodes
        wr_line(f, "{")
        wr_line(f, "rank=same", num=2)
        for child in children:
            wr_line(f, f'Child{child} [shape=point]', num=2)
        wr_line(f, "}")

        wr_line(f, "{")

        # place the hidden nodes in the correct order
        for i, child in enumerate(children):
            if i == 0:
                wr_line(f, f'{parents} -> Child{child}', num=2)
            else:
                first = children[i-1]
                second = child
                wr_line(f, f'Child{first} -> Child{second}', num=2)

        # connect hidden node to real node
        for child in children:
            wr_line(f, f'Child{child} -> {child}', num=2)

        wr_line(f, "}")

def insert_generation(f, people, generations):

    for i in range(len(generations)):

        wr_line(f, "{")
        wr_line(f, "rank=same", num=2)

        for person in generations[i]:
            if isinstance(person, tuple):
                insert_spouse_pair(f, person[0])
            else:
                insert_person(f, person)

        wr_line(f, "}")

    for _, generation in generations.items():
        insert_order(f, generation)

###############################################################################

def get_family_tree(root, display=False):
    people, generations = sheet_to_data(root, display)

    filename = "output/" + root.replace(' ', '_').lower() + ".dot"

    with open(filename, "w") as f:
        f.write('digraph {\n')
        f.write('\tedge [dir = none];\n\n')
        
        if ortho:
            f.write('\tgraph [splines = ortho];\n\n')

        insert_generation(f, people, generations)

        for generation in generations:
            for person in generations[generation]:
                if isinstance(person, tuple):
                    parent = person[0]
                    children = person[1]

                    if ortho:
                        insert_ortho_children(f, parent, children)
                    else:
                        insert_children(f, parent, children)

        f.write('}\n')

    command = f'dot -Tpng -O {filename}'
    subprocess.call(command, shell=True)

# todo implement get_lineage(): given a node, it will generate a tree with all their ancestors

get_family_tree("Vishnuprasad Trivedi")
get_family_tree("Fulshankar Adhyaru")
get_family_tree("Chinuprasad Trivedi")
get_family_tree("Jotindra Raval")

get_family_tree("Ambrish Trivedi")
get_family_tree("Rajendra Trivedi")
get_family_tree("Bhupendra Adhyaru")