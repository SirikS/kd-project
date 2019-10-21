from SPARQLWrapper import SPARQLWrapper, JSON
import json
import pandas as pd

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
ingredienten = ['Chicken', 'Carrot']
for ingredient in range(len(ingredienten)):
    begin += """?recipe rp:hasIngredient ?ingredient{}.
    # State which category the ingredient belongs to 
    ?ingredient{} rdf:type rp:{}.
    """.format(ingredient, ingredient, ingredienten[ingredient])

nietappliance = ["oven"]
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
hoi = pd.DataFrame(out, columns=cols)
print(hoi.head())