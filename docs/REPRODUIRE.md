# Refaire l’étude

## Installation

Python 3.12 et uv sont nécessaires. Le fichier `uv.lock` fixe les versions réellement utilisées. La bibliothèque commune gv-fintools est liée à un commit précis. Le calcul utilise le processeur et n’exige aucune carte graphique.

```bash
uv sync --locked
uv run rnv fetch
uv run rnv run
uv run rnv publish
uv run rnv verify
uv run pytest
```

Exécuter les commandes depuis la racine du dépôt. `run` reconstruit les tables et l’entrepôt. `publish` recrée les figures, le README, l’article et son PDF. Les textes sources sont dans `docs/templates/`. Une modification directe de l’article serait remplacée au prochain `publish`.

## Deux niveaux de reproduction

Les calculs sont déterministes avec les fichiers du manifeste, la configuration et les versions fixées. Le téléchargement ultérieur du même millésime n’est toutefois pas garanti pour toutes les adresses publiques. Certaines sources remplacent leur fichier à chaque actualisation.

Si une empreinte diffère, `fetch` s’arrête. Il ne remplace pas silencieusement les données de l’étude. Il faut soit retrouver les fichiers correspondant aux empreintes publiées, soit préparer un nouveau manifeste et documenter la nouvelle période. Un téléchargement gratuit ne suffit donc pas à garantir la reproduction exacte dans plusieurs années.

Les données brutes sont conservées localement dans `data/raw/`. Elles ne doivent pas être ajoutées à Git sans vérifier leurs conditions. Les tables publiées permettent déjà de contrôler les résultats annoncés et de suivre leurs dénominateurs.

## Consulter les résultats

Les fichiers CSV sont la sortie de référence. Le [classeur Excel](../results/resultats.xlsx) est une sélection de résultats calculés, préparée pour la lecture. Il ne prétend pas réexécuter les régressions ou simulations lorsque l’on change une cellule. L’onglet Exemple contient en revanche des formules simples qui se recalculent avec les hypothèses modifiées.

L’entrepôt `results/research.duckdb` est reconstruit localement par `run`. Une table SQL correspond à chaque CSV. La [requête d’exemple](../sql/01_resultats.sql) répond à la question principale.

```python
import duckdb

with duckdb.connect("results/research.duckdb", read_only=True) as database:
    result = database.sql("SELECT * FROM historical_summary").df()
print(result.head())
```

Le notebook `notebooks/01_comprendre.ipynb` utilise les fonctions du paquet et les tables existantes. Il ne contient pas une seconde version du moteur scientifique. Il peut être exécuté depuis la racine ou son propre dossier après l’installation.

## Export Excel

Le classeur livré est un instantané de consultation, créé avec `scripts/export_workbook.mjs`. Ce script exige Node.js et le paquet `@oai/artifact-tool` de l’environnement d’édition utilisé. Il ne fait pas partie des dépendances Python requises pour reproduire les calculs, les figures ou le PDF. Les mêmes résultats restent accessibles en CSV sans ce paquet.

## Vérification automatique

`verify` contrôle les empreintes du code et des tables depuis le dernier calcul, puis la correspondance entre l’article Markdown et le PDF. Un changement de code après `run` impose une nouvelle exécution. Le fichier `results/run_manifest.json` contient la provenance du calcul.

La CI exécute le contrôle de style, les tests sans téléchargement et les contrôles de cohérence des artefacts publiés. Elle ne récupère pas les données et ne doit donc pas être confondue avec une nouvelle exécution complète de l’étude.
