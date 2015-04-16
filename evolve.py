import os
import sys
import random
import json
import shutil


#####################################################################
#                       CONSTANTS / PRE
#####################################################################


MAX = 500
MAX_OFFSPRING = 300
GEN_DIR_NAME = "gen"
BUILD_FILE_NAME = "build.es"

with open('baseGrammar', 'r') as f:
    BASE_GRAMMAR = f.read()


#####################################################################
#                       DATA
#####################################################################


categoryDirectoryNames = ["wow", "busy", "simple"]

colors = [["#002136", "#52E8B5", "#5AE5FF", "#54007F", "#C34CFF"],  # aqua analogous
          ["#353D7F", "#52D8E8", "#67FF7D", "#77007F", "#F451FF"],  # blue green analogous
          ["#A981FF", "#67FF7D", "#CC873E", "#70BBFF", "#61717F"],  # triad
          ["#DEFFF8", "#B22448", "#FF678D", "#F7FF1B", "#22FD02"],  # complimentary
          ["#DEF3FF", "#694629", "#574C3C", "#237F2B", "#38CC45"]]  # earthy


primitive_terminals = ["sphere", "line", "mesh", "box"]
flowerShapes = ["sphere", "line", "mesh"]
treeShapes = ["box", "mesh"]
fireworkShapes = ["box", "recursive_rule"]
terminals = ["sphere", "box", "recursive_rule", "mesh", "flower_bud", "star", "quad_terminal", "double_terminal", "taurus", "drop", "pellet", "vine"]


flowerRule = """\n//flowerRule\n\nrule tree w 0.2 {\n{ z 1 ry 6   s 0.99  color color2 hue 1 } flower_bud\n
            { rz 60  } flower_bud\nmesh\n}\n\n"""

scaleValues = ["0.15", "0.3", "0.5", "0.8"]

frontSideRotation = "set rotation [0.81671 0.381619 -0.432846 0.222319 0.484109 0.846295 0.532506 -0.787406 0.310536]"
topRotation = "set rotation [0.996454 -0.120381 -0.333834 0.122804 1.04307 -0.00463998 0.32303 -0.0374218 0.94566]"
pancakeRotation = "set rotation [0.861419 -0.484786 -0.376561 0.481631 0.142758 0.922366 -0.34749 -0.883518 0.314126]"

rotationSettings = [frontSideRotation, topRotation, pancakeRotation]

makeTreesAppear = """1 * { s 0.8 rx 4 ry 10 color random } trees * { h 1 rz 360/trees }
                1 * { x treeRingRadius rz 20} tree"""

# the base is made of rings  with beads, rotated 360/beads,   spaced x distance apart
scaffoldings = ["rings * { s 0.8 rx x_rotation ry y_rotation color random } beads * { h 1 rz 360/beads } 1 * { x 10 rz z_rotation} spawn",
                "rings * { s 0.8 rx x_rotation ry y_rotation color random } beads * { x 20 rz z_rotation} spawn"]

axis_choices = ['x', 'y', 'z']

#####################################################################
#                       HELPER FUNCTIONS
#####################################################################


def print_options():
    print "You must pass one of the following paires of arguments: "
    print "1) 'first' and initial population size                      Ex: python evolve.py first 100"
    print "2) 'crossover' and directory of phenotypes/pngs to breed    Ex: python evolve.py crossover gen/wow"
    print "3) 'mutate and 'gen' directory of genotypes/json to mutate  Ex: python evolve.py mutate gen/wow/gen"


def perform_option(option, param):
    if option == 'first':
        generate_first_generation(int(param))
    elif option == 'crossover':
        generate_nth_generation(os.getcwd() + "/" + param)
    elif option == 'mutate':
        mutate_population(os.getcwd() + "/" + param)
    else:
        print_options()


def generate_genotype_from_file(f_name):
    f_handle = open(f_name)
    return json.loads(f_handle.readline())


def get_genotype_name(d):
    f_name = str(d["maxDepth"])
    for i in range(len(d["colorScheme"])):
        f_name += "-" + str(d["colorScheme"][i][1])
    return f_name


def generate_files_from_genotype(d):
    f_name = d["genotypeName"]

    # file for breeding
    f = open(f_name + ".json", 'w')
    f.write(json.dumps(d))
    f.close()

    # file for generating pics
    f = open(f_name + ".es", 'w')
    f.write("//genotype: %s\n" % f_name)
    if "parent1" in d and "parent2" in d:
        f.write("//parent1: %s and parent2: %s\n\n" % (d["parent1"]["genotypeName"], d["parent2"]["genotypeName"]))
    elif "mutantOrigin" in d:
        f.write("//Mutant origin: %s\n\n" % d["mutantOrigin"]["genotypeName"])
    else:
        f.write("//First generation. No parents\n\n")
    f.write("set maxdepth %d\n" % d["maxDepth"])
    f.write("set background %s\n" % d["colorScheme"][0])
    f.write("set colorpool list:")
    color_count = len(d["colorScheme"])
    for i in range(3, color_count):
        f.write(d["colorScheme"][i])
        if i < color_count - 1:
            f.write(",")
    f.write("\n\n")
    f.write("set minsize %f\n\n" % d["minsize"])
    f.write("#define color1 %s\n" % d["colorScheme"][1])
    f.write("#define color2 %s\n" % d["colorScheme"][2])
    f.write("#define color3 %s\n" % d["colorScheme"][3])
    f.write("#define base_rule_weight %s\n" % d["baseRuleWeight"])
    f.write("#define base_rule_shape %s\n" % d["baseRuleShape"])
    f.write("#define recursive_rule_on %s\n" % d["recursiveRuleWeight"])
    f.write("#define recursive_size %s\n" % d["recursiveSize"])
    f.write("#define recursive_offset %s\n" % d["recursiveOffset"])
    f.write("#define trees %d\n" % d["trees"])        
    f.write("#define rings %d\n" % d["rings"])        
    f.write("#define beads %d\n" % d["beads"])        
    f.write("#define x_rotation %d\n" % d["xRotation"])
    f.write("#define y_rotation %d\n" % d["yRotation"])
    f.write("#define z_rotation %d\n" % d["zRotation"])
    f.write("#define treeRingRadius %s\n" % d["treeRingRadius"]) 
    f.write("#define tree_recursion_depth %d\n" % d["treeRecursionDepth"])
    f.write("#define maxFireworkDepth %d\n" % d["maxFireworkDepth"])
    f.write("#define flower_bud_shape %s\n" % d["flowerShape"])   
    f.write("#define tree_shape %s\n" % d["treeShape"])
    f.write("#define star_shape box\n")
    f.write("#define firework_shape %s\n" % d["fireworkShape"])
    f.write(rotationSettings[d["rotationSettingIndex"]] + "\n")
    f.write("\n// Camera settings. Place these before first rule call.\n")
    f.write("set translation [0 0 -20]\n")
    f.write("set pivot [0 0 0]\n")
    f.write("set scale %s\n" % scaleValues[d["scaleIndex"]])
    f.write("\n\n// scaffolding\n")
    f.write(scaffoldings[d["scaffoldingIndex"]] + "\n\n")
    if d["hasTrees"]:
        f.write(makeTreesAppear + "\n")
    f.write(BASE_GRAMMAR)
    f.write(d["productionRule1"])
    if d["secondRuleOn"]:
        f.write(d["productionRule2"])
    if "productionRule3" in d:
        f.write(d["productionRule3"])
    if d["flowerRule"]:
        f.write(flowerRule)
    f.close()
    return f_name


def generate_phrase():
    p = "{ x "
    if random.choice([True, False]):
        p += "-"           #maybe
    p += "recursive_offset y "
    if random.choice([True, False]):
        p += "-"           #maybe
    p += "recursive_offset z recursive_offset s recursive_size } recursive_rule\n"
    return p


def generate_more_random_phrase():
    p = "{ x "
    if random.choice([True, False]):
        p += "-"           #maybe
    p += str(random.uniform(.01, .9)) + " y "    # todo make this breedable
    if random.choice([True, False]):
        p += "-"           #maybe
    p += "%f z %f s recursive_size } recursive_rule\n" % (random.uniform(.01, .9), random.uniform(.01, .9))
    return p


def generate_production_rule(number_of_phrases):
    s = "\n\nrule recursive_rule md 5 {\n"
    for i in range(number_of_phrases):
        s += generate_more_random_phrase()
    s += "{ color random } sphere\n}\n\n"
    return s


def generate_expressive_production_rule():
    terminal = terminals[random.randint(0, len(terminals) - 1)]
    terminal2 = terminals[random.randint(0, len(terminals) - 1)]
    axis_char = random.choice(axis_choices)
    s = "\n\nrule expressive_production_rule md 5 {\n"
    s += "%d * { %c %d } %d * { s %d }" % (random.randint(1, 5), axis_char, random.randint(1, 5), random.randint(1, 3), random.randint(1, 2))
    s += " %s { color random } %s\n" % (terminal, terminal)
    if bool(random.getrandbits(1)):
        s += "%d * { %c %d } %d * { s %d }" % (random.randint(1, 5), axis_char, random.randint(1, 5), random.randint(1, 3), random.randint(1, 2))
        s += " %s { color random } %s\n" % (terminal2, terminal2)
    s += "}\n\n"
    s += "expressive_production_rule\n\n"   # call it
    return s


def generate_random_color():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())


def generate_javascript_for_file(fname):
    j_script = """Builder.load("%s.es");""" % fname
    j_script += "\n"
    j_script += "Builder.reset();\n"
    j_script += "Builder.setSize(0,600);\n"
    j_script += "Builder.build();\n"
    j_script += """Builder.renderToFile("%s.png",true);""" % fname
    j_script += "\n\n"
    return j_script


def generate_genotype_files_and_javascript(n):
    j_script = "#javascript\n\n"
    for i in range(n):
        fname = generate_files_from_genotype(generate_genotype_from_scratch())
        j_script += generate_javascript_for_file(fname)
    f = open(BUILD_FILE_NAME, 'w')
    f.write(j_script)
    f.close()


def create_new_sub_directories_and_chdir_into_gen():
    if os.path.isdir(GEN_DIR_NAME):             # checking to see if directory exists in current directory
        shutil.rmtree(GEN_DIR_NAME)             # always wipes earlier generated directory clean
    os.makedirs(GEN_DIR_NAME)
    os.chdir(GEN_DIR_NAME)

    for categoryName in categoryDirectoryNames:
        if os.path.isdir(categoryName):         # checking to see if directory exists in current directory
            shutil.rmtree(categoryName)         # always wipes earlier generated directory clean
        os.makedirs(categoryName)               # create all directories of described names


#####################################################################
#                       FIRST GENERATION
#####################################################################


def generate_first_generation(foremothers_count):
    create_new_sub_directories_and_chdir_into_gen()
    print "\ngenerating first generation of count %d" % foremothers_count
    print "build file location: %s" % os.getcwd()
    generate_genotype_files_and_javascript(foremothers_count)


def generate_genotype_from_scratch():
    d = {
        'maxDepth': random.randint(15, MAX),
        'minsize': random.random(),
        'productionRule1': generate_production_rule(random.randint(3, 7)),
        'productionRule2': generate_production_rule(random.randint(0, 3)),
        'secondRuleOn': random.choice([False] * 5 + [True]),
        'colorScheme': [generate_random_color()] + colors[random.randint(0, len(colors) - 1)],
        'baseRuleWeight': random.choice([1, 10]),
        'baseRuleShape': random.choice(terminals),
        'recursiveRuleWeight': random.randint(0, 5),
        'recursiveSize': random.uniform(0.3, 0.5),
        'recursiveOffset': random.uniform(0.25, 0.5),
        'scaffoldingIndex': random.choice([0] * 9 + [1]),
        'trees': random.randint(1, 70),
        'rings': random.randint(1, 30),
        'beads': random.randint(1, 80),
        'xRotation': random.randint(4, 8),
        'yRotation': random.randint(1, 60),
        'zRotation': random.randint(15, 25),
        'treeRingRadius': random.randint(0, 30),
        'treeRecursionDepth': random.randint(0, 50),
        'flowerShape': flowerShapes[random.randint(0, len(flowerShapes) - 1)],
        'treeShape': treeShapes[random.randint(0, len(treeShapes) - 1)],
        'fireworkShape': fireworkShapes[random.randint(0, len(fireworkShapes) - 1)],
        'flowerRule': bool(random.getrandbits(1)),
        'maxFireworkDepth': random.randint(1, 50),
        'rotationSettingIndex': random.randint(0, len(rotationSettings) - 1),
        'scaleIndex': random.randint(0, len(scaleValues) - 1),
        'hasTrees': random.choice([True, False, False])
    }
    d['genotypeName'] = get_genotype_name(d)
    return d


#####################################################################
#                       CROSSOVER
#####################################################################


def generate_genotype_from_parents(parent1, parent2):
    smaller_color_scheme_length = min(len(parent1["colorScheme"]), len(parent2["colorScheme"]))
    i = random.randint(0, smaller_color_scheme_length - 1)
    production_rule_candidates = [parent1["productionRule2"], parent1["productionRule3"], parent2["productionRule1"], parent2["productionRule2"], parent2["productionRule3"]]
    d = {
        'maxDepth':  int((parent1["maxDepth"] + parent2["maxDepth"]) / 2),
        'minsize': (parent1["minsize"] + parent2["minsize"]) / 2,
        'productionRule1': parent1["productionRule1"],
        'productionRule2': production_rule_candidates.pop(random.randint(0, 2)),
        'productionRule3': production_rule_candidates.pop(random.randint(0, 1)),
        'secondRuleOn': parent1['secondRuleOn'] and parent2['secondRuleOn'],
        'colorScheme': parent1["colorScheme"][:i] + [parent2["colorScheme"][i]] + parent1["colorScheme"][i:],
        'baseRuleWeight': parent1["baseRuleWeight"],
        'baseRuleShape': parent1["baseRuleShape"],
        'recursiveRuleWeight': random.choice([parent1["recursiveRuleWeight"], parent2["recursiveRuleWeight"]]),
        'recursiveSize': (parent1["recursiveSize"] + parent2["recursiveSize"])/2,
        'recursiveOffset': (parent1["recursiveOffset"] + parent2["recursiveOffset"])/2,
        'scaffoldingIndex': random.choice([parent1["scaffoldingIndex"], parent2["scaffoldingIndex"]]),
        'trees': (int((parent1["trees"] + parent2["trees"])/2))+1,
        'rings': int((parent1["rings"] + parent2["rings"])/2),
        'beads': parent1["beads"],
        'xRotation': parent2["xRotation"],
        'yRotation': parent2["yRotation"],
        'zRotation': parent2["zRotation"],
        'treeRingRadius': int((parent1["treeRingRadius"] + parent2["treeRingRadius"])/2),
        'treeRecursionDepth': int((parent1["treeRecursionDepth"] + parent2["treeRecursionDepth"])/2),
        'flowerShape': random.choice([parent1["flowerShape"], parent2["flowerShape"]]),
        'treeShape': random.choice([parent1["treeShape"], parent2["treeShape"]]),
        'fireworkShape': random.choice([parent1["fireworkShape"], parent2["fireworkShape"]]),
        'flowerRule': parent1["flowerRule"] or parent2["flowerRule"],
        'maxFireworkDepth': random.choice([parent1["maxFireworkDepth"], parent2["maxFireworkDepth"]]),
        'rotationSettingIndex': parent1["rotationSettingIndex"],
        'scaleIndex': parent1["scaleIndex"],
        'hasTrees': parent1["hasTrees"] and parent2["hasTrees"],
        'parent1': parent1,
        'parent2': parent2
    }
    d['genotypeName'] = get_genotype_name(d)
    return d


def generate_nth_generation(foremothers_phenotype_path):
    print "crossing over   ", foremothers_phenotype_path

    # first get all foremothers DNA
    foremothers_names = []
    for f in os.listdir(foremothers_phenotype_path):    # ex. grabbing all pngs from wow directory
        if f.endswith(".png"):
            foremothers_names.append(f[:-4])            # removed file extension

    if not foremothers_names:
        print "Sorry, there are no chosen breeders in that directory."
        print "Put the pngs in that directory and then try again."
        return

    os.chdir(foremothers_phenotype_path)
    os.chdir("..")                                      # goes up a directory to 'gen' to get genotypes
    foremothers = []
    for f in os.listdir('.'):
        if f.endswith(".json"):
            if f[:-5] in foremothers_names:
                foremothers.append(generate_genotype_from_file(f))

    # then create offspring directory where all generated content will go
    os.chdir(foremothers_phenotype_path)
    create_new_sub_directories_and_chdir_into_gen()     # create place for next generation and chosen ones

    foremothers_count = len(foremothers)
    while int((foremothers_count**2)/2) > MAX_OFFSPRING:
        foremothers_count -= 1

    # shuffle deck, then go through all set of parents in order, until desired count is reached.
    j_script = "#javascript\n\n"
    random.shuffle(foremothers)
    for i in range(foremothers_count):
        for j in range(i + 1, foremothers_count):
            fname = generate_files_from_genotype(generate_genotype_from_parents(foremothers[i], foremothers[j]))
            j_script += generate_javascript_for_file(fname)
    f = open(BUILD_FILE_NAME, 'w')
    f.write(j_script)
    f.close()
    print "offspring are in %s" % os.getcwd()


#####################################################################
#                       MUTATION
#####################################################################

def mutate_population(genotype_path):
    if genotype_path[-1:] == '/':
        genotype_path = genotype_path[:-1]
    if genotype_path[-3:] != 'gen':
        print "You did not provide a valid 'gen' directory"
        return
    try:
        os.chdir(genotype_path)
    except:
        print "The directory you specified does not exist"
        return
    print "mutating        ", genotype_path
    population = []
    for f in os.listdir('.'):
        if f.endswith(".json"):
            population.append(mutate_genotype(generate_genotype_from_file(f)))
    create_new_sub_directories_and_chdir_into_gen()
    j_script = "#javascript\n\n"
    for mutated_genotype in population:
        fname = generate_files_from_genotype(mutated_genotype)
        j_script += generate_javascript_for_file(fname)
    f = open(BUILD_FILE_NAME, 'w')
    f.write(j_script)
    f.close()
    print "mutants are in  ", os.getcwd()


def mutate_genotype(genotype):
    production_rule1_phrase_count = genotype['productionRule1'].count("rule") - 1

    color_gene = genotype['colorScheme']
    random.shuffle(color_gene)
    mutated_color_gene = [generate_random_color()] + color_gene[:-1]

    d = {
        'maxDepth':  abs(genotype['maxDepth'] + random.choice([-1, 1])),
        'minsize': abs(genotype['minsize'] + random.choice([-0.01, 0.01])),
        'productionRule1': generate_production_rule(production_rule1_phrase_count),
        'productionRule2': genotype['productionRule1'],
        'productionRule3': generate_expressive_production_rule(),
        'secondRuleOn': random.choice([False] * 5 + [True] + [genotype['secondRuleOn']]),
        'colorScheme': mutated_color_gene,
        'baseRuleWeight': abs(genotype['baseRuleWeight'] + random.choice([-2, 2])),
        'baseRuleShape': random.choice(terminals + [genotype['baseRuleShape']] * 5),
        'recursiveRuleWeight': abs(genotype['recursiveRuleWeight'] + random.choice([-2, 2])),
        'recursiveSize': abs(genotype['recursiveSize'] + random.choice([-0.01, 0.01])),
        'recursiveOffset': abs(genotype['recursiveSize'] + random.choice([-0.01, 0.01])),
        'scaffoldingIndex': genotype['scaffoldingIndex'],
        'trees': max(1, abs(genotype['trees'] + random.choice([-1, 1]))),
        'rings': max(1, abs(genotype['rings'] + random.choice([-1, 1]))),
        'beads': max(1, abs(genotype['beads'] + random.choice([-3, 3]))),
        'xRotation': abs(genotype['xRotation'] + random.choice([-1, 1])),
        'yRotation': abs(genotype['yRotation'] + random.choice([-2, 2])),
        'zRotation': abs(genotype['zRotation'] + random.choice([-3, 3])),
        'treeRingRadius': abs(genotype['treeRingRadius'] + random.choice([-1, 1])),
        'treeRecursionDepth': abs(genotype['treeRecursionDepth'] + random.choice([-1, 1])),
        'flowerShape': random.choice(flowerShapes + [genotype['flowerShape']] * 5),
        'treeShape': random.choice(treeShapes + [genotype['treeShape']] * 5),
        'fireworkShape': random.choice(fireworkShapes + [genotype['fireworkShape']] * 5),
        'flowerRule': random.choice([False, True] + [genotype['flowerRule']] * 5),
        'maxFireworkDepth': abs(genotype['treeRecursionDepth'] + random.choice([-3, 3])),
        'rotationSettingIndex': genotype["rotationSettingIndex"],
        'scaleIndex': genotype["scaleIndex"],
        'hasTrees': random.choice([False, True] + [genotype['hasTrees']] * 5),
        'mutantOrigin': genotype
    }
    d['genotypeName'] = get_genotype_name(d)
    return d


#####################################################################
#                       MAIN
#####################################################################
testing = False
l = len(sys.argv)
if l == 1:
    testing = True

if testing:
    option = 'first'
    param = '15'
    perform_option(option, param)
else:
    args = sys.argv
    if l == 3:
        option = args[1]
        param = args[2]
        perform_option(option, param)
    else:
        print_options()

