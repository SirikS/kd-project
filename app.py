import os

# for making the recommendations
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import json
import pandas as pd

# for running flask
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
    Redirects to the fake index page.
    """
    return redirect(url_for("not_index"))

@app.route("/index", methods=["GET", "POST"])
def not_index():
    """
    Select ingredients and applicances.
    Afterwards calculates the new recipes.
    """
    ingredientlist = ['Shellfish', 'Alcohol', 'Spinach', 'Creme_de_Cacao', 'Milk_or_Cream', 'Grape', 'Grapefruit', 'Honey', 'Onion', 'Seed', 'Legume', 'Peanut_Butter', 'Tree_Nut', 'Almond', 'Garlic', 'Tomatillo', 'Bell_Pepper', 'Clove', 'Cheese', 'Poultry', 'Egg', 'Lemon', 'Rhubarb', 'Cherry', 'Parsnip', 'Fruit_Juice', 'Apricot', 'Citrus', 'Jam_or_Jelly', 'Eggplant', 'Butter', 'Cinnamon', 'Pickles', 'Raisin', 'Lime', 'Beef', 'Coriander', 'Radish', 'Apple', 'Lamb', 'Beet', 'Sausage', 'Capers', 'Coffee', 'Mint', 'Pork', 'Carrot', 'Parsley', 'Poppy', 'Leek', 'Oily_Fish', 'Bread', 'Rosemary', 'Cilantro', 'Tomato', 'Hot_Pepper', 'Chocolate', 'Cabbage', 'Collard_Greens', 'Turnip', 'Berry', 'Plum', 'Sweet_Potato', 'Rice', 'Pepper', 'Cucumber', 'Watercress', 'Plantain', 'Avocado', 'Paprika', 'Semolina', 'Lettuce', 'Whitefish', 'Ginger', 'Tortilla', 'Celery', 'Rye', 'Caraway', 'Cumin', 'Date', 'Fig', 'Passion_Fruit', 'Dill', 'Mayonnaise', 'Hazelnut', 'Currant', 'Orange', 'Kale', 'Pine_Nut', 'Melon', 'Mushroom', 'Pasta', 'Pastry', 'Squash', 'Basil', 'Corn', 'Pear', 'Pineapple', 'Saffron', 'Vanilla', 'Maple_Syrup', 'Salad_Dressing', 'Mustard', 'Sesame_Oil', 'Anise', 'Artichoke', 'Aragula', 'Asparagus', 'Banana', 'Barley', 'Biscuit', 'Bran', 'Brine', 'Broccoli', 'Wheat', 'Cantaloupe', 'Cardamom', 'Cashew', 'Cauliflower', 'Caviar', 'Chestnut', 'Chive', 'Coconut', 'Custard', 'Endive', 'Escarole', 'Fennel', 'Kumquat', 'Guava', 'Horseradish', 'Hummus', 'Kiwi', 'Lemongrass', 'Lychee', 'Mango', 'Marshmellow', 'Meatloaf', 'Nectarine', 'Nutmeg', 'Oat', 'Okra', 'Olive', 'Oregano', 'Papaya', 'Peach', 'Peanut', 'Pecan', 'Persimmon', 'Pistachio', 'Pomegranate', 'Potato', 'Prune', 'Quince', 'Quinoa', 'Rabbit', 'Radicchio', 'Sage', 'Salsa', 'Sesame', 'Stock', 'Tamarind', 'Tangerine', 'Tapioca', 'Tarragon', 'Tea', 'Thyme', 'Tofu', 'Venison', 'Vinegar', 'Walnut', 'Wasabi', 'Yogurt', 'Zucchini', 'Mustard_Greens', 'Brussel_Sprout', 'Broccoli_Rabe', 'Bok_Choy', 'Cranberry_Sauce', 'Macadamia_Nut', 'Butterscotch_Caramel', 'Ice_Cream', 'Soy_Sauce', 'Sour_Cream']
    appliancelist = ['oven', 'pasta_maker', 'mixer', 'food_processor', 'stove', 'grill', 'deep-fryer', 'blender', 'freezer', 'pressure_cooker','juicer', 'microwave', 'smoker', 'ice_cream_machine', 'slow_cooker', 'coffee_grinder']

    if request.method == "POST":

        # remove the ingredients/appliances from the list
        dictionary = request.form.values()
        for lijst in dictionary:
            if lijst in appliancelist:
                appliancelist.remove(lijst)
            if lijst in ingredientlist:
                ingredientlist.remove(lijst)

        # make the recommendations, and return these
        if recommend(ingredientlist, appliancelist):
            return render_template("results.html")

    # make the user fill in the form
    return render_template("index.html")

def recommend(ingredienten, nietappliance):
    """
    Makes a SPARQL query based on ingredients, and returns a dataframe of the recipes
    """

    # make the query
    begin = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rp: <http://www.groepsproject.com/recipes/>
SELECT DISTINCT ?title ?link ?linktitle ?description
WHERE {
    ?recipe rdf:type rp:Recipe.
    """
    # remove the recipes with other ingredients
    for ingredient in range(len(ingredienten)):
        begin += """FILTER NOT EXISTS {?recipe rp:hasIngredient ?ingredient%i.
    ?ingredient%i rdf:type rp:%s}
    """ % (ingredient, ingredient, ingredienten[ingredient])

    # remove the recipes for which you don't have the appliance
    for appliance in nietappliance:
        begin += """FILTER NOT EXISTS {?recipe rp:needsAppliance rp:%s}
    """ % appliance

    # get the recipes data
    begin += """?recipe rp:hasTitle ?title;
        rp:hasLink ?link;
        rp:hasDescription ?description;
        rp:hasLinkTitle ?linktitle.
} ORDER BY DESC(?link)"""

    # display the query in terminal
    print(begin)

    # fill in your own reposity here
    sparql = SPARQLWrapper("http://localhost:7200/repositories/project")

    # set the right format, and type of request method
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)

    # run the query
    sparql.setQuery(begin)
    results = sparql.query()

    # set max colwidth off
    pd.set_option('display.max_colwidth', -1)

    # load as pandas dataframe
    processed_results = json.load(results.response)
    cols = processed_results['head']['vars']
    out = []
    for row in processed_results['results']['bindings']:
        item = []
        for c in cols:
            item.append(row.get(c, {}).get('value'))
        out.append(item)
    pd.DataFrame(out, columns=cols).to_html("templates/test.html")
    with open("templates/test.html", "r") as f1, open("templates/results.html", "w") as f2:
        f2.write("""<head>
    <link href= {{ url_for('static', filename = 'css-custom.css') }} rel="stylesheet">
</head>
""")
        for line in f1:
            f2.write(line)
    os.remove("templates/test.html")
    return True