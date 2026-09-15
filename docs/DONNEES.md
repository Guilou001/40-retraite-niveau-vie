# Données, provenance et unités

Les fichiers ont été téléchargés le 15 septembre 2026. Chaque source utilisée est décrite ci-dessous. Le [manifeste machine](../config/data_manifest.json) conserve son adresse et son empreinte SHA-256.

## Jordà-Schularick-Taylor, version R6

Fichier local `jst.dta`. [Téléchargement public](https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.dta?t=1720600177).

Données annuelles jusqu’en 2020, rendements en fractions, IPC en niveau et PIB réel par habitant. Licence CC BY-NC-SA 4.0 de la base. Les résultats qui en adaptent les données conservent cette restriction.

Empreinte du millésime utilisé

```text
b0ebb74a8d1b5b1bc9033fc46a6dcc578736afff8ce1e1086b7840f2649e79b3
```

## Ce que le dépôt redistribue

Le dépôt publie le code, les tableaux analytiques, les figures et la documentation. Les fichiers bruts ne sont pas placés dans Git. Les fichiers intermédiaires détaillés qui recopient des observations de fournisseurs restent locaux. Leurs empreintes permettent de vérifier le calcul sans assimiler accès public et autorisation générale de redistribution.

La licence MIT porte sur le code original. La rédaction originale est proposée sous CC BY 4.0. Les données tierces, les articles cités et les figures ou tables qui adaptent des données sous conditions conservent leurs droits propres. Les résultats issus de JST restent soumis à CC BY-NC-SA 4.0. Cette distinction ne confère aucune licence supplémentaire sur les indices des autres fournisseurs.

## Du fichier source au résultat

`fetch` contrôle les empreintes. `run` vérifie la couverture, applique les unités, calcule les résultats et monte l’entrepôt DuckDB. `publish` lit les résultats pour recréer les figures et insérer les nombres dans les modèles de texte. Les fichiers bruts et les paramètres restent séparés du code.

Les périodes, les observations exclues et les substitutions sont expliquées dans le [protocole](PROTOCOLE.md) et dans l’article. Une absence de donnée n’est jamais remplacée par zéro.
