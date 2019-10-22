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
    if request.method == "POST":
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
        begin += """?recipe rp:hasIngredient ?ingredient{}.
        # State which category the ingredient belongs to 
        ?ingredient{} rdf:type rp:{}.
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