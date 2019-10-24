# Knowlegde & Data Project

A webpage that gives recommended recipes based on the ingredients you have at home. 
This can also be filtered by the appliances you have. 

To run this program you have to install a couple of modules.
1. `pip install flask`
2. `pip install pandas`
After this the program can be run by typing `flask run` in the terminal. 

The sparql query is automatically sent to 'http://localhost:7200/repositories/project', this can be changed in `app.py`.


# Voor ons zelf:

Clone de pagina: `git clone https://github.com/SirikS/kd-project.git`

Basic stappen om te commiten:
1. `git add "filename"`
2. `git pull`
3. `git commit -m "Message to go with the commit here"`
4. `git push`

Om the checken of je niks bent vergeten kan je `git status` runnen.
Om alle files in een keer te "adden" kan je `git add *` doen.
Als git ergens een error geeft volg dan wat hij zegt en vraag mij anders.

De server is te runnen door eerst eenmalig `pip install flask` te doen. Daarna kan je `flask run` doen terwijl je in de goede path zit in je terminal (dus eindigt met kd-project).
