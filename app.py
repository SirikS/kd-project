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
    ingredientlist = ['Fish', 'Shellfish', 'Mollusk', 'Scallop', 'Alcohol', 'Liquids', 'Chartreuse', 'Gin', 'Vegetables', 'Spinach', 'Sweets_and_Candy', 'Creme_de_Cacao', 'Dairy', 'Milk_or_Cream', 'Fruit', 'Grape', 'Grapefruit', 'Sauces_and_Dressings', 'Honey', 'Onion', 'Herbs_and_Spices', 'Seed', 'Legume', 'Soy', 'Spreads', 'Peanut_Butter', 'Nut', 'Tree_Nut', 'Almond', 'Garlic', 'Tomatillo', 'Bell_Pepper', 'Brandy', 'Clove', 'Bean', 'Cheese', 'Crustacean', 'Shrimp', 'Meat', 'Chicken', 'Poultry', 'Egg', 'Lemon', 'Rhubarb', 'Cherry', 'Parsnip', 'Sherry', 'Fruit_Juice', 'Lemon_Juice', 'Apricot', 'Citrus', 'Jam_or_Jelly', 'Eggplant', 'Butter', 'Cinnamon', 'Pickles', 'Raisin', 'Lime', 'Cream_Cheese', 'Beef', 'Coriander', 'Radish', 'Veal', 'Wine', 'Sparkling_Wine', 'Apple', 'Lamb', 'Beet', 'Sausage', 'Bourbon', 'Campari', 'Capers', 'Coffee', 'Mint', 'Bacon', 'Pork', 'Carrot', 'Duck', 'Parmesan', 'Parsley', 'Poppy', 'Leek', 'Oily_Fish', 'Tuna', 'Grain_Products', 'Bread', 'Rosemary', 'Cilantro', 'Sardine', 'Chickpea', 'Tomato', 'Hot_Pepper', 'Jalapeno', 'Monterey_Jack', 'Chile_Pepper', 'Chocolate', 'Clam', 'Crab', 'Mussel', 'Scotch', 'Cabbage', 'Collard_Greens', 'Rutabaga', 'Turnip', 'Berry', 'Cranberry', 'Lime_Juice', 'Plum', 'Ham', 'Sweet_Potato', 'Rice', 'Pepper', 'Cucumber', 'Egg_Nog', 'Cognac', 'Watercress', 'Plantain', 'Avocado', 'Paprika', 'Raspberry', 'Semolina', 'Lettuce', 'Sake', 'Cod', 'Whitefish', 'Ginger', 'Tortilla', 'Celery', 'Poblano', 'Lentil', 'Rye', 'Caraway', 'Cumin', 'Date', 'Fig', 'Passion_Fruit', 'Buttermilk', 'Kirsch', 'Whiskey', 'Breadcrumbs', 'Dill', 'Mayonnaise', 'Shallot', 'Sugar_Snap_Pea', 'Hazelnut', 'Currant', 'Beer', 'Blackberry', 'Orange', 'Champagne', 'Kale', 'Pine_Nut', 'Melon', 'Mushroom', 'Orzo', 'Pasta', 'Pastry', 'Squash', 'Basil', 'Corn', 'Brisket', 'Ricotta', 'Pear', 'Pineapple', 'Saffron', 'Vanilla', 'Maple_Syrup', 'Salad_Dressing', 'Lima_Bean', 'Mustard', 'Sesame_Oil', 'Amaretto', 'Anchovy', 'Anise', 'Artichoke', 'Aragula', 'Asparagus', 'Banana', 'Barley', 'Biscuit', 'Blueberry', 'Bran', 'Brie', 'Brine', 'Broccoli', 'Bulgur', 'Wheat', 'Calvados', 'Cantaloupe', 'Cardamom', 'Cashew', 'Cauliflower', 'Caviar', 'Cheddar', 'Chestnut', 'Chili', 'Chive', 'Coconut', 'Couscous', 'Custard', 'Endive', 'Escarole', 'Fennel', 'Feta', 'Fontina', 'Goose', 'Gouda', 'Kumquat', 'Guava', 'Halibut', 'Honeydew', 'Horseradish', 'Hummus', 'Kiwi', 'Lemongrass', 'Lingonberry', 'Lobster', 'Lychee', 'Mango', 'Marscarpone', 'Marshmellow', 'Meatloaf', 'Mozzerella', 'Nectarine', 'Nutmeg', 'Oat', 'Octopus', 'Okra', 'Olive', 'Oregano', 'Oyster', 'Papaya', 'Pea', 'Peach', 'Peanut', 'Pecan', 'Persimmon', 'Pistachio', 'Pomegranate', 'Potato', 'Prune', 'Quail', 'Quince', 'Quinoa', 'Rabbit', 'Radicchio', 'Rum', 'Sage', 'Salmon', 'Salsa', 'Sesame', 'Snapper', 'Sourdough', 'Squid', 'Stock', 'Strawberry', 'Swordfish', 'Tamarind', 'Tangerine', 'Tapioca', 'Tarragon', 'Tea', 'Thyme', 'Tilapia', 'Tofu', 'Trout', 'Venison', 'Vinegar', 'Walnut', 'Wasabi', 'Yogurt', 'Zucchini', 'Green_Bean', 'Blue_Cheese', 'Goat_Cheese', 'Mustard_Greens', 'Brussel_Sprout', 'Broccoli_Rabe', 'Green_Onion', 'Asian_Pear', 'Bok_Choy', 'Apple_Juice', 'Cranberry_Sauce', 'Orange_Juice', 'Iced_Tea', 'Pomegranate_Juice', 'Macadamia_Nut', 'White_Wine', 'Swiss_Cheese', 'Red_Wine', 'Butterscotch_Caramel', 'Ice_Cream', 'Cottage_Cheese', 'Soy_Sauce', 'Sour_Cream', 'Rose', 'Iced_Coffee', 'Whole_Wheat']
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
        data = recommend(ingredientlist, appliancelist)
        return render_template("index.html", data=data)

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
    begin += """?recipe rp:hasTitle ?title.
        OPTIONAL{
            ?recipe rp:hasLink ?link;
                    rp:hasDescription ?description;
                    rp:hasLinkTitle ?linktitle.}
    } ORDER BY DESC(?link)"""


    # fill in your own reposity here
    sparql = SPARQLWrapper("http://localhost:7200/repositories/project")

    # set the right format, and type of request method
    sparql.setReturnFormat(JSON)
    sparql.setMethod(POST)

    # run the query
    sparql.setQuery(begin)
    results = sparql.query()

    # load as pandas dataframe
    processed_results = json.load(results.response)
    cols = processed_results['head']['vars']
    out = []
    for row in processed_results['results']['bindings']:
        item = []
        for c in cols:
            item.append(row.get(c, {}).get('value'))
        out.append(item)
    return pd.DataFrame(out, columns=cols)