# Lire les résultats

Les CSV utilisent un point décimal pour les logiciels. Les rendements, fréquences et bornes de rendement sont enregistrés en fractions. Une valeur de 0,10 signifie 10 %. Les corrélations et les ratios de Sharpe restent des nombres sans unité. Les périodes et dénominateurs doivent être comparés avant les résultats.

## historical_summary.csv

Comparaison des règles par durée, sur tous les départs américains complets. Le champ paths donne le nombre de départs. ruin_share mesure l’épuisement du capital. below_budget_share mesure au moins une année sous 30 000 dollars réels.

## historical_paths.csv

Une ligne par règle, durée et année de départ. Cette table permet de retrouver le dénominateur des fréquences et les cas de manque prolongé.

## common_origins.csv

Même comparaison, mais sur les seules années de départ disponibles pour les trois durées. Ce tableau isole mieux l’effet de passer de trente à cinquante ans.

## cohort_1966.csv

Dépenses et solde réel après chaque retrait pour le départ en 1966. Les montants sont des dollars américains du début de 1966.

## international.csv

Portefeuilles domestiques de quarante ans avec départs depuis 1950. Comparer les pays en gardant à l’esprit leurs indices et leurs expériences historiques.

## bootstrap_summary.csv

Dix mille trajectoires par longueur de bloc. shortfall_fraction_mean divise le manque cumulé par le budget minimal cumulé. Ces fréquences décrivent les scénarios reconstruits.

## paired_comparisons.csv

Différence de manque cumulé entre chaque règle et le montant constant sur les mêmes scénarios. monte_carlo_se mesure le bruit numérique lié au nombre de tirages, pas l’incertitude sur le futur.

## fee_sensitivity.csv

Frais de 0 %, 0,2 % et 1 % appliqués aux mêmes départs historiques de quarante ans.

## spending_distribution.csv

Quantiles annuels des dépenses parmi les scénarios de quarante ans, blocs de cinq années. Un quantile calculé à chaque année ne constitue pas nécessairement une trajectoire réalisable.

## coverage.csv

Années disponibles par pays et type d’actif. Le Canada et l’Irlande n’ont pas les rendements requis.

Les figures et les tableaux de l’article proviennent de ces sorties. [Revenir à l’article](../ARTICLE.md).
