import json
from nltk.translate import bleu_score
import random

# getRoomDescriptions reads from the templates.json file
# and returns the information for a specific room type from the file.
# The information includes its room style text description and its template code


def getRoomDescriptions(room):
    # Opening JSON file
    f = open("data/templates.json")

    # returns JSON object as a dictionary
    data = json.load(f)

    room_descriptions = dict()
    # Iterating through the json list
    for i in data[room]:
        # Parse out only the first sentence
        # (The remaining description is not so relevant for now)
        s = i['description'].split('.')[0]
        room_descriptions[s] = i['code']

    # Closing file
    f.close()

    # A dictionary that stores each style with its code template
    return room_descriptions

# getTemplateItems reads from the products.json file
# and returns the items associated with the a specific template code (ie. 'b1' = bedroom style #1)
# Items include products under different categories


def getTemplateItems(code):
    # Opening JSON file
    f = open("data/products.json")

    # returns JSON object as a dictionary
    data = json.load(f)

    # Iterating through the json list
    items = dict()
    # each template contains different categories (ie. 'furniture', 'bed and mattresses', 'home decor')
    for category in data[code]:

        # each category contains a set of products
        products = dict()

        for product in data[code][category]:
            # only store the relevant product information:
            # product name, identifier number, product description and price
            detail_info = list()
            detail_info.append(product['identifier'])  # 'identifier'
            detail_info.append(product['description'])  # 'description'
            detail_info.append(product['price'])  # 'price'
            products[product['name']] = detail_info

        # store all products included in the category
        items[category] = products

    # Closing file
    f.close()

    # a dictionary of items with all suggested categories
    return items

# getMatchScoreList takes the user input and template options
# and computes the match score between input and each template description.
# The function returns a list of scores from highest to the lowest,
# and program can access template code through the same list
def getJaccardSimilarity(text1, text2): 
    
    # Get unique text words
    words1 = set(text1.lower().split()) 
    words2 = set(text2.lower().split())
        
    # Get Jaccard Similarity Score -> Intersection Size / Union Size
    return float(len(words1.intersection(words2))) / len(words1.union(words2))


def getMatchScoreList(input, options):
    match_scores = list()

    # consider each style description in avaialble options for a specified room type
    for style_description in options:
        
        # Method 1
        # # calculates the 1-gram bleu score between input and description
        # score = float(bleu_score.modified_precision(
        #     [input], style_description, n=1))
        
        # Method 2
        # calculates Jaccard Similarity
        score = getJaccardSimilarity(input, style_description)

        # add the (score, template code) tuple to the list
        match_scores.append(tuple((score, options[style_description])))

    # sort from highest to lowest
    match_scores.sort(reverse=True)
    return match_scores


def getItemCategories(room):
    must_have_categories = set()
    room_info = getRoomDescriptions(room)
    for i in room_info:
        code = room_info[i]
        template = getTemplateItems(code)
        curr_categories = template.keys()
        if not must_have_categories:
            must_have_categories = set(curr_categories)
        elif len(curr_categories) > 3:
            must_have_categories = must_have_categories.intersection(
                set(curr_categories))
    return must_have_categories

# getBasicRecommendations takes the match scores list and ouputs 4 recommendations for users.
# Each recommendation contains detailed information of each category and products
# under each category. The format of each product introductions is prodcut description
# followed by product name and identifier number

MAX_NAME_SIZE = 20

def getNameFormatted(name: str) -> str:
    if len(name) > MAX_NAME_SIZE:
        name = "{}...".format(name[:17])
    for i in range(MAX_NAME_SIZE - len(name)):
        name += " "
    return name


def getBasicRecommendations(match_scores):
    print("\tThe following room design options are recommended for you:")
    
    for i in range(4):
        if i >= len(match_scores): break
        items = getTemplateItems(match_scores[i][1])
        print("\n\t[ Here is your option {} ]".format(i+1))
        # each category
        if len(items) == 0:
            match_scores.pop(i)

        for category in items:
            print('\n\tFor ' + category + ', you might consider...')
            # each item
            for item_name in items[category]:
                product_info = items[category][item_name]
                description = product_info[1]
                identifier_number = product_info[0]
                # eliminate ending comma for some product descriptions
                item_name = getNameFormatted(item_name)
                if description[-1] == ',':
                    description = description[:-1]
                print("\t\t>> {}\t\t[{}]:\t{}".format(item_name, identifier_number, description))


def getUniqueDesign(must_have_categories, category_products):
    items = dict()
    for c in must_have_categories:
        items[c] = dict()
        options = category_products[c]
        for i in range(3):
            item_name, item_info = random.choice(list(options.items()))
            items[c][item_name] = item_info
    return items


def getUniqueRecommendations(match_scores):
    # find the must have categories for a specific room type
    must_have_categories = set()
    category_products = dict()
    # learn from top 6 options or all available options if less than 6 available
    n = len(match_scores) if len(match_scores) < 6 else 6
    for i in range(n):
        code = match_scores[i][1]
        # access all items associated with the style
        items = getTemplateItems(code)
        # store items under each category into the dictionary
        for c in items:
            if c in category_products:
                category_products[c].update(items[c])
            else:
                category_products[c] = items[c]
        # get all current categories and update must have categories
        curr_categories = items.keys()
        if not must_have_categories:
            must_have_categories = set(curr_categories)
        else:
            must_have_categories = must_have_categories.intersection(
                set(curr_categories))
    print(must_have_categories)

    # output 4 options
    for i in range(4):
        items = getUniqueDesign(must_have_categories, category_products)
        # each category
        for category in items:
            print('For ' + category + ', you might consider...')
            # each item
            for item_name in items[category]:
                product_info = items[category][item_name]
                description = product_info[1]
                identifier_number = product_info[0]
                # eliminate ending comma for some product descriptions
                if description[-1] == ',':
                    description = description[:-1]
                print(description + ": " + item_name +
                      "(" + identifier_number + ")")

# Testing
# room_type = 'bedroom'
# options = getRoomDescriptions(room_type)
# input = 'small, calming, cozy and sustainable'
# match_scores = getMatchScoreList(input, options)
# # print(match_scores)
# getBasicRecommendations(match_scores)
