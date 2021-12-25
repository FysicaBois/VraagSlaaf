1. Installeer poetry met `pip install --user poetry`
`
1.b voor de plugin support moet je de alpha hebben voor installatie: https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py en `python install-poetry.py --preview`
2. Installeer dependencencies met `poetry install`
  Dit maakt een .lock file dat voor altijd je dependencies vastlegt. Later
  nog updaten kan met `poetry update` (dus niet in je lock file zitten klungelen)
3. Run met `poetry run python main.py`
4. Dependencies toevoegen met `poetry add <libname>`


Je kan ook de PyCharm poetry plugin installeren. Je moet dan de python interpreter
veranderen naar een standaard poetry interpreter

# Accessing the server
1. Download en installeer PuTTY
2. Server IP invullen, laat port op 22 staan
3. Username is root
4. passwoord kopieren, in putty shift + insert dan enter
