# Vraagslaaf QRH

## Intro
Dit document is gescreven als een soort startup-guide voor het installeren van de VraagSlaaf broncode en een snelcursus
in de architectuur van de bot. Afhangend van hoe goed je al kan coderen kan deze guide overlopen van een kwartier tot
een week tijd in beslag nemen. Neem a.u.b. voldoende tijd en stel vragen waar nodig.

Prerequisites: Het is vanzelfsprekend dat je wat Python kennis nodig hebt, maar voor de rest zijn er geen eisen.


## First things first

De Vraagslaaf heeft heel wat architectuur behind the scenes die je nodig hebt om zelfs maar het programma te runnen,
die hieronder uitgelegd worden.

### CLI (command line interface)

**Dingen die je zou moeten weten voor verder te gaan**
- weten wat een terminal is, een terminal kunnen opendoen in zowel normale als adminstrator modus.
- weten wat environment variables zijn, meer specifiek wat het PATH variabele is en hoe het te vinden.
- weten hoe je kan navigeren in een terminal met commands als `dir` en `cd`.


### git.

[git](https://git-scm.com/) is de meest gebruikte VCS ter wereld. Een VCS (kort voor Version Control System), is een
programma dat het mogelijk maakt om veranderingen in de source code voor een project bij te houden, en eventueel terug
te gaan naar vorige iteraties indien nodig. Het is handig om systematisch aan projecten te werken en fouten ongedaan te
maken. Het heeft ook tools om samen met anderen te werken zoals branching. Gekoppeld met een online service als
[Github](https://github.com/) is het een onmisbare tool voor het coderen.

Als je al met git kan werken, goed! Als je dat nog niet kan is het de moeite om een youtube tutorial te kijken en je te
 familiarizeren met de workflow, aangezien in het in nagenoeg alle grote projecten gebruikt wordt (en je niks aan de
Vraagslaaf code zal kunnen toevoegen zonder git.)

**Dingen die je zou moeten weten voor verder te gaan**
- weten wat git is en het bijhorende jargon (bv. Wat is een *repo*?)
- de git commands `git add, git commit, git pull, git push`
- weten wat branching is (dit hoeft niet in detail te zijn, het gebeurt niet veel dat branches gemaakt worden)
- weten wat Github is, een Github account hebben


### poetry
[Poetry](https://python-poetry.org/) is een python utility die het bijhouden van python packages vereenvoudigt. (Als je
het nog niet wist, een python package is een stuk code van derden dat je in jouw project kan gebruiken met een import
statement, deze packages moeten echter gedownload worden voor ze gebruikt kunnen worden met utilities als 
[pip](https://pypi.org/project/pip/)). Ook zorgt poetry het gemakkelijk compilen en releasen van projecten en houdt poetry
automatisch een virtual python environment bij. In een groot project als de Vraagslaaf is zo'n utility zeer handig.

Met poetry werken is eenvoudig. Kijk opnieuw een youtube tutorial of lees kort de documentatie (die in orde is) om kennis te maken 
met het programma.

**Dingen die je zou moeten weten voor verder te gaan**
- weten wat poetry is.
- weten wat een virtual python environment is.
- de poetry commands `poetry add, poetry update, poetry install, poetry env`

## Installatie 

Installatie vereist Python 3.9+, git, en poetry. Persoonlijk gebruik ik Pycharm maar natuurlijk werken andere tools (vscode)
ook. Als je PyCharm gebruikt, kan ik je de Poetry plugin voor PyCharm aanraden.

1. Clone de code van de github repo
2. Download met `poetry update` de dependencies, er zal normaal gezien automatisch een python environment gecreëerd worden. 
   (alternatief voor PyCharm: switch de Python interpreter naar een Poetry interpreter en dit zal automatisch gebeuren)
3. Vraag een env folder aan Anton voor de secrets.
4. Runnen zou zo simpel moeten zijn als `poetry run server` of `poetry run bot`


## De code
### discord.py
