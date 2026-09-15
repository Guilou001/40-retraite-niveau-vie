# Faire durer son épargne sans trop réduire son niveau de vie

Une personne retraitée doit choisir combien retirer chaque année. Retirer moins après une baisse des marchés peut préserver son capital. Encore faut-il que le montant restant suffise pour vivre.

**Sur {{paths}} départs historiques américains de 40 ans, retirer 4 % du solde chaque année évite l'épuisement du capital. Mais les dépenses passent sous le budget minimal dans {{percentage_shortfall}} % des cas.** Le montant constant épuise le capital dans {{fixed_ruin}} % des cas. Ces observations décrivent des trajectoires passées qui se chevauchent.

![Épuisement du capital et baisse des dépenses](results/figures/budget_et_capital.png)

La barre bleue répond à la question « reste-t-il de l'argent ? ». La barre orange répond à la question « le ménage peut-il maintenir son budget minimal ? ». Les deux réponses peuvent être très différentes.

## Un exemple avant les résultats

Supposons une épargne d'un million de dollars et des dépenses initiales de 40 000 dollars par an. Le budget minimal choisi pour l'étude est de 30 000 dollars, en pouvoir d'achat constant. Cela représente une réduction de 25 % par rapport au budget de départ.

Après une forte baisse des marchés, retirer 4 % d'un solde de 500 000 dollars ne donne plus que 20 000 dollars. Le compte reste positif. Le ménage doit pourtant renoncer à la moitié de ses dépenses initiales.

## Ce que nous comparons

Les actifs contiennent 50 % d'actions et 50 % d'obligations américaines. Ils sont rééquilibrés chaque année. Le premier retrait intervient après douze mois. Les frais annuels valent 0,2 %.

| Règle | Comment le retrait est décidé |
| --- | --- |
| Montant constant | Maintenir chaque année le pouvoir d'achat des 40 000 dollars initiaux |
| Pourcentage du solde | Retirer 4 % de la valeur disponible, à partir de la deuxième année |
| Ajustement limité | Recalculer les 4 %, mais limiter la variation réelle annuelle entre −1,5 % et +5 % |
| Avec budget minimal | Appliquer l'ajustement limité, en demandant au moins 30 000 dollars réels |

Le budget minimal est une demande, pas une garantie. Le programme ne peut jamais retirer davantage que le solde disponible.

## Les résultats historiques sur 40 ans

{{historical_table}}

Les montants sont corrigés de l'inflation. Une année sous le budget suffit à entrer dans la troisième colonne. La dernière colonne tient aussi compte de la durée du manque. La règle avec budget minimal réussit sur ces trajectoires américaines, mais elle échoue dans d'autres pays et dans certains scénarios reconstruits.

![Dépenses et capital pour un départ en 1966](results/figures/depart_1966.png)

Le graphique supérieur montre ce que la personne peut dépenser. Le graphique inférieur montre ce qui reste sur son compte. La date de 1966 est un exemple fixé dans le protocole, sans recherche de la pire trajectoire.

## Le lien avec Vanguard

L'étude prolonge [Fuel for the F.I.R.E.](https://www.vanguardmexico.com/content/dam/intl/americas/documents/mexico/en/fuel-for-the-fire.pdf), de Costa, Pakula et Clarke, publié par Vanguard en 2021. Le papier souligne les risques d'une retraite longue et examine les retraits variables.

Les limites de retrait de sa figure 6 sont reproduites dans les tests. Ses probabilités reposent toutefois sur un modèle de prévision privé, VCMM. Notre étude utilise l'histoire publique de JST et des blocs d'années rééchantillonnés. **Elle ne reproduit pas les probabilités de Vanguard.**

## Lire, vérifier et reproduire

- [Article complet et résumé anglais](ARTICLE.md), également en [PDF](rapport/rapport.pdf)
- [Protocole fixé avant le calcul complet](docs/PROTOCOLE.md)
- [Notions expliquées avec des exemples](docs/COMPRENDRE.md)
- [Sources, unités et conditions de réutilisation](docs/DONNEES.md)
- [Vérifications et limites de reproduction](docs/VERIFICATION.md)
- [Classeur des résultats](results/resultats.xlsx) et [parcours Python](notebooks/01_comprendre.ipynb)

```bash
uv sync --locked
uv run rnv fetch
uv run rnv run
uv run rnv publish
uv run pytest
```

Les téléchargements sont gratuits. Les empreintes des fichiers empêchent de remplacer silencieusement le millésime étudié par une mise à jour. Le [guide de reproduction](docs/REPRODUIRE.md) explique ce point et les requêtes SQL.

## Ce que cette étude ne permet pas de conclure

Les pays ont des histoires différentes. Le Canada n'a pas de série de rendements dans ce millésime JST et n'est pas simulé comme s'il en avait une. Les portefeuilles sont domestiques, sans fiscalité, pension publique ni risque individuel de longévité. Une fréquence passée ou simulée ne constitue pas une probabilité garantie pour une retraite future.

[![Tests automatiques](https://github.com/Guilou001/40-retraite-niveau-vie/actions/workflows/ci.yml/badge.svg)](https://github.com/Guilou001/40-retraite-niveau-vie/actions/workflows/ci.yml)

## English summary

This study separates portfolio depletion from inadequate spending. It compares four annual withdrawal rules using public historical stock, bond and inflation data. It reproduces Vanguard's numerical spending example, not its proprietary forecast probabilities. Historical cohorts, paired block scenarios and international checks expose the trade-off between preserving capital and preserving consumption.
