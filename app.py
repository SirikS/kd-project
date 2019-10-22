import os

# nodig voor recommendations
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import pandas as pd

# nodig om te runnen
from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import mkdtemp

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Renders the select ingredients screen
    """
    # if request.method == "POST":
    #     # ga aanbevelingen maken
    #     results = recommend(False, False)
    #     # redirect naar de resultaten
    #     return render_template("results.html", results)
    return redirect(url_for("not_index"))

@app.route("/index", methods=["GET", "POST"])
def not_index():

    ingredientlist = ['almond', 'amaretto', 'anchovy', 'anise', 'apple', 'apple juice', 'apricot', 'artichoke', 'arugula', 'asian pear', 'asparagus', 'avocado', 'bacon', 'banana', 'barley', 'basil', 'bean', 'beef', 'beef rib', 'beef shank', 'beef tenderloin', 'beer', 'beet', 'bell pepper', 'berry', 'biscuit', 'blackberry', 'blue cheese', 'blueberry', 'bok choy', 'bourbon', 'bran', 'brandy', 'bread', 'breadcrumbs', 'brie', 'brine', 'brisket', 'broccoli', 'broccoli rabe', 'brown rice', 'brussel sprout', 'bulgur', 'butter', 'buttermilk', 'butternut squash', 'butterscotch/caramel', 'cabbage', 'calvados', 'campari', 'cantaloupe', 'capers', 'caraway', 'cardamom', 'carrot', 'cashew', 'cauliflower', 'caviar', 'celery', 'champagne', 'chartreuse', 'cheddar', 'cheese', 'cherry', 'chestnut', 'chicken', 'chickpea', 'chile', 'chile pepper', 'chili', 'chive', 'chocolate', 'cilantro', 'cinnamon', 'citrus', 'clam', 'clove', 'coconut', 'cod', 'coffee', 'cognac/armagnac', 'collard greens', 'coriander', 'corn', 'cornmeal', 'cottage cheese', 'couscous', 'crab', 'cranberry', 'cranberry sauce', 'cream cheese', 'créme de cacao', 'cr��me de cacao', 'cucumber', 'cumin', 'currant', 'curry', 'custard', 'date', 'dill', 'duck', 'egg', 'egg nog', 'eggplant', 'endive', 'escarole', 'fennel', 'feta', 'fig', 'fontina', 'garlic', 'gin', 'ginger', 'goat cheese', 'goose', 'gouda', 'granola', 'grape', 'grapefruit', 'green bean', 'green onion/scallion', 'ground beef', 'ground lamb', 'guava', 'halibut', 'ham', 'hazelnut', 'honey', 'honeydew', 'horseradish', 'hot pepper', 'hummus', 'ice cream', 'iced coffee', 'iced tea', 'jalapeño', 'jam or jelly', 'kale', 'kirsch', 'kiwi', 'kumquat',  'lamb', 'lamb chop', 'lamb shank', 'leek', 'legume', 'lemon', 'lemon juice', 'lemongrass', 'lentil', 'lettuce', 'lima bean', 'lime', 'lime juice', 'lingonberry', 'lobster', 'lychee', 'macadamia nut', 'mandoline', 'mango', 'maple syrup', 'marscarpone', 'marshmallow', 'mayonnaise', 'meatloaf', 'melon', 'milk/cream', 'mint', 'monterey jack', 'mozzarella', 'mushroom', 'mussel', 'mustard', 'mustard greens', 'nectarine', 'nutmeg', 'oat', 'oatmeal', 'octopus', 'okra', 'olive', 'omelet', 'onion', 'orange', 'orange juice', 'oregano', 'orzo', 'oyster', 'papaya', 'paprika', 'parmesan', 'parsley', 'parsnip', 'passion fruit', 'pastry', 'pea', 'peach', 'peanut', 'peanut butter', 'pear', 'pecan', 'pepper', 'persimmon', 'pickles', 'pine nut', 'pineapple', 'pistachio', 'plantain', 'plum', 'poblano', 'pomegranate', 'pomegranate juice', 'poppy', 'pork', 'pork chop', 'pork rib', 'pork tenderloin', 'potato', 'poultry', 'poultry sausage', 'prosciutto', 'prune', 'pumpkin', 'purim', 'quail', 'quince', 'quinoa', 'rabbit', 'rack of lamb', 'radicchio', 'radish', 'raisin', 'raspberry', 'raw', 'red wine', 'rhubarb', 'rice', 'ricotta', 'rosemary', 'rosé', 'rum', 'rutabaga', 'rye', 'saffron', 'sage', 'sake', 'salad dressing', 'salmon', 'salsa', 'sardine', 'sausage', 'sauté', 'scallop', 'scotch', 'seed', 'semolina', 'sesame', 'sesame oil', 'shallot', 'shellfish', 'sherry', 'shrimp', 'snapper', 'sour cream', 'sourdough', 'soy', 'soy sauce', 'sparkling wine', 'spinach', 'squash', 'squid', 'steak', 'steam', 'stock', 'strawberry', 'sugar snap pea', 'sweet potato/yam', 'swiss cheese', 'swordfish', 'tamarind', 'tangerine', 'tapioca', 'tarragon', 'tea', 'thyme', 'tilapia', 'tofu', 'tomatillo', 'tomato', 'tortillas', 'tree nut', 'trout', 'tuna', 'turnip', 'vanilla', 'veal', 'venison', 'vinegar', 'walnut', 'wasabi', 'watercress', 'watermelon', 'whiskey', 'white wine', 'whole wheat', 'wild rice', 'yellow squash', 'yogurt', 'zucchini', 'turkey']
    appliancelist = ['backyard bbq', 'bake', 'blender', 'boil', 'braise', 'broil', 'coffee grinder', 'deep-fry', 'double boiler', 'food processor', 'epi loves the microwave', 'frozen dessert' , 'freeze/chill', 'freezer food', 'fry', 'grill', 'grill/barbecue', 'ice cream', 'ice cream machine', 'juicer', 'microwave', 'mixer', 'one-pot meal', 'pan-fry', 'pasta maker', 'poach', 'pressure cooker', 'ramekin', 'simmer', 'sorbet',  'soup/stew', 'stir-fry ', 'slow cooker', 'smoker', 'wok']

    """
    """
    if request.method == "POST":
        print(request.form)
        # ga aanbevelingen maken
        results = recommend(False, False)
        # redirect naar de resultaten
        return render_template("results.html", results)
    return render_template("index.html")

@app.route("/results")
def result():
    """
    Renders the login/register screen
    """
    # kan alleen via index, daar vullen ze alles in
    return render_template("results.html")

def recommend(ingredienten, nietappliance):
    begin = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rp: <http://www.groepsproject.com/recipes/>

    # Example query, one ingredient: Chicken, carrot
    # 				 Appliance excluced: oven
    # With the website rp:Chicken rp:Carrot and rp:oven should be changed to 
    # variables with values the user has given.

    SELECT DISTINCT ?title ?link ?linktitle ?description
    WHERE {
        
        # Only get items that are recipes.
        ?recipe rdf:type rp:Recipe.

        # GET THE RECIPES WITH THE RIGHT INGREDIENTS
        # First give that the recipe should have the ingredient
        """
    if not ingredienten:
        ingredienten = ['Chicken', 'Carrot']
    for ingredient in range(len(ingredienten)):
        begin += """FILTER NOT EXISTS {?recipe rp:hasIngredient ?ingredient%i.
        ?ingredient%i rdf:type rp:%s.}
        """.format(ingredient, ingredient, ingredienten[ingredient])

    if not nietappliance:
        nietappliance= ["oven"]
    for appliance in nietappliance:
        begin += """FILTER NOT EXISTS {?recipe rp:needsAppliance rp:%s}
        """ % appliance
    begin += """?recipe rp:hasTitle ?title.
        
        # Not all recipes have a link, decription and linkTitle
        OPTIONAL{
            ?recipe rp:hasLink ?link;
                    rp:hasDescription ?description;
                    rp:hasLinkTitle ?linktitle.
        }

    # Recipes with links should have priority
    } ORDER BY DESC(?link)"""
    print(begin)

    # vul hier je eigen repository naam in
    sparql = SPARQLWrapper("http://localhost:7200/repositories/project")
    sparql.setQuery(begin)

    sparql.setReturnFormat(JSON)
    results = sparql.query()

    processed_results = json.load(results.response)
    cols = processed_results['head']['vars']

    out = []
    for row in processed_results['results']['bindings']:
        item = []
        for c in cols:
            item.append(row.get(c, {}).get('value'))
        out.append(item)
    results = pd.DataFrame(out, columns=cols)
    return results