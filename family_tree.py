from sheets_to_dot import sheet_to_data, get_alpha_spouse
import os.path
import subprocess

ortho = False

def wr_line(f, str, num=1):
    f.write('\t'*num)
    f.write(str)
    f.write('\n')

def insert_person(f, name, gender, living):
    shape = " [shape=box]"

    gender_color = ""
    if name in gender['M']:
        gender_color = " [color=blue]"
    else:
        gender_color = " [color=red]"

    color = ""
    if name in living['N']:
        color = " [fillcolor=gray, style=filled]"

    filename = "images/" + name.lower()
    if os.path.isfile(f'{filename}.jpeg'):
        filename = filename + ".jpeg"
    elif os.path.isfile(f'{filename}.png'):
        filename = filename + ".png"
    else:
        filename = ""

    img = ""
    if filename != "":
        img = f' [label=<<TABLE border="0"><TR><TD width="75" height="75" fixedsize="true"><IMG SRC="{filename}" scale="true"/></TD></TR><TR><TD>{name}</TD></TR></TABLE>>]'

    wr_line(f, name + shape + gender_color + color + img, num=2)

    

def insert_spouse_pair(f, pair, gender, living):
    name1, name2 = pair.split('_')

    insert_person(f, name1, gender, living)
    wr_line(f, f'{pair} [shape=point]', num=2)
    insert_person(f, name2, gender, living)

def insert_conn(f, name1, name2):
    if '_' in name1 or '_' in name2:
        wr_line(f, f'{name1} -> {name2}', num=2)
    else:
        wr_line(f, f'{name1} -> {name2} [style = invisible]', num=2)

def insert_order(f, simple_gen):
    complex_gen = []
    for person in simple_gen:
        if '_' in person:
            name1, name2 = person.split('_')
            complex_gen.append(name1)
            complex_gen.append(person)
            complex_gen.append(name2)
        else:
            complex_gen.append(person)

    for i, person in enumerate(complex_gen):
        if i == 0:
            continue
        else:
            first = complex_gen[i-1]
            second = person
            insert_conn(f, first, second)

def get_str_set(spouses):
    spouse_set = set()
    for spouse in spouses:
        spouse_set.add(get_alpha_spouse(spouse, spouses[spouse]))
    
    return spouse_set

def order_tree(children, roots):
    gen_tree = {0: []}
    tmp_children = children
    
    # list all the children of the roots in the next generations
    for root in roots:
        gen_tree[0].append(root)
        if root in children:
            if 1 not in gen_tree:
                gen_tree[1] = []

            gen_tree[1].extend(children[root])
            tmp_children.pop(root)

    depth = 0

    # for all the following generations, add their children to the next generation
    while len(tmp_children) > 0:
        depth += 1
        for person in gen_tree[depth]:
            if person in children:
                if depth+1 not in gen_tree:
                    gen_tree[depth+1] = []

                gen_tree[depth+1].extend(children[person])
                tmp_children.pop(person)

    return gen_tree

def sort_generations(spouses, children, roots):

    # get simplified child list with spouse pairing
    simp_child = {}
    for parent, child_list in children.items():
        simp_child[parent] = []
        for child in child_list:
            if child in spouses:
                simp_child[parent].append(get_alpha_spouse(child, spouses[child]))
            else:
                simp_child[parent].append(child)

    # get simplified root list with spouse pairing
    simp_roots = set()
    for root in roots:
        if root in spouses:
            simp_roots.add(get_alpha_spouse(root, spouses[root]))
        else:
            simp_roots.add(root)

    return order_tree(simp_child, simp_roots)

def insert_generation(f, spouses, gender, living, children, roots):
    generations = sort_generations(spouses, children, roots)
    print(f'generations = {generations}')
 
    for i in range(len(generations)):

        wr_line(f, "{")
        wr_line(f, "rank=same", num=2)

        for person in generations[i]:
            if '_' in person:
                insert_spouse_pair(f, person, gender, living)
            else:
                insert_person(f, person, gender, living)

        wr_line(f, "}")

    for i, generation in generations.items():
        insert_order(f, generation)

def insert_children(f, parents, children):
    wr_line(f, "{")
    for child in children:
        wr_line(f, f'{parents} -> {child}', num=2)
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

def get_family_tree(family):
    people, spouses, children, gender, living, roots = sheet_to_data(family, display=False)

    filename = "output/" + family + ".dot"

    with open(filename, "w") as f:
        f.write('digraph {\n')
        f.write('\tedge [dir = none];\n\n')
        
        if ortho:
            f.write('\tgraph [splines = ortho];\n\n')

        insert_generation(f, spouses, gender, living, children, roots)

        for parent, child_list in children.items():
            if ortho:
                insert_ortho_children(f, parent, child_list)
            else:
                insert_children(f, parent, child_list)

        f.write('}\n')

    command = f'dot -Tpng -O {filename}'
    subprocess.call(command, shell=True)

get_family_tree("bharti")
get_family_tree("bhupendra")
get_family_tree("rajendra")
get_family_tree("usha")