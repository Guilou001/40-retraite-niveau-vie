#set figure.caption(separator: [. ])
#set document(title: "Faire durer son épargne sans trop réduire son niveau de vie", author: "Guillaume Vaudescal")
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.4cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(90))
    #grid(columns: (1fr, auto), align: (left, right),
      [Document de recherche · Version 1.0.1], [#counter(page).display("1 / 1", both: true)])
  ],
)
#set text(font: ("Libertinus Serif", "Times New Roman", "DejaVu Serif"), size: 10.5pt, lang: "fr")
#set par(justify: true, leading: 0.68em, spacing: 1.1em)
#set heading(numbering: none)
#show heading.where(level: 2): it => block(sticky: true, above: 1.6em, below: 0.8em, text(size: 13pt, it))
#show heading.where(level: 3): it => block(above: 1.2em, below: 0.6em, text(size: 11pt, it))
#show raw.where(block: true): it => block(
  fill: luma(246), inset: 8pt, radius: 3pt, width: 100%, text(size: 8.5pt, it))
#show raw.where(block: false): it => text(size: 9pt, fill: rgb("#1a3f66"), it)
#show quote.where(block: true): it => block(
  inset: (left: 10pt), stroke: (left: 1.5pt + luma(180)),
  text(style: "italic", fill: luma(45), it.body))
// la table NE DOIT PAS être enfermée dans un par() : Typst 0.15 la supprime alors
// entièrement, sans erreur. Le réglage se pose donc dans la portée du bloc.
#show table: it => block(breakable: false, above: 1.1em, below: 1.1em,
  [#set par(justify: false); #text(size: 8.8pt, it)])
#show figure: it => block(above: 1.4em, below: 1.4em, it)
#show figure.caption: it => text(size: 8.5pt, fill: luma(70), it)
#show link: it => text(fill: rgb("#0072B2"), it)

#align(center)[
  #set par(justify: false)
  #block(width: 100%)[
    #text(hyphenate: false, size: 18pt, weight: "bold")[Faire durer son épargne sans trop réduire son niveau de vie]
    #v(0.6em)
    #text(size: 10pt, fill: luma(70))[Guillaume Vaudescal · 15 septembre 2026 · #link("https://github.com/Guilou001/40-retraite-niveau-vie")[Guilou001/40-retraite-niveau-vie]]
  ]
]
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + luma(190))
#v(0.8em)

Document de recherche, 15 septembre 2026. Adaptation empirique de Costa, Pakula et Clarke (2021).

== Résumé

L'épuisement du portefeuille est un critère incomplet pour évaluer les retraits à la retraite. Une règle proportionnelle peut conserver un capital positif tout en réduisant fortement les dépenses. Cette étude compare quatre règles sur des trajectoires historiques et sur des scénarios reconstruits par blocs d'années.

Sur 110 départs américains complets de 40 ans, le retrait proportionnel n'épuise aucun portefeuille. Les dépenses passent pourtant sous 75 % du budget initial dans 74,5 % des cas. Le retrait constant épuise le capital dans 19,1 % des cas. L'ajustement limité réduit ces difficultés, sans les supprimer. Les résultats internationaux et simulés empêchent de transformer une réussite historique américaine en garantie générale.

== 1. Pourquoi cette question compte

La phase d'épargne et la phase de retraite ont des problèmes différents. Pendant l'épargne, une baisse peut offrir du temps pour continuer à investir. Pendant la retraite, il faut vendre des actifs pour payer ses dépenses. Une vente après une baisse retire définitivement une partie du capital qui aurait pu participer à la reprise.

Vanguard étudie cette difficulté dans Fuel for the F.I.R.E. Le papier souligne que les retraites anticipées peuvent durer davantage que les trente années souvent utilisées dans les exemples de retrait. Il examine aussi les frais, les anticipations de rendement et la flexibilité des dépenses. La stabilité du niveau de vie fait donc déjà partie de sa réflexion.

Notre question est plus précise. Une règle qui améliore la survie du portefeuille protège-t-elle aussi un budget minimal, et pendant combien d'années ce budget peut-il manquer ? Le projet complète le #link("https://github.com/Guilou001/12-plan-epargne")[projet 12 sur l'épargne] en passant de l'accumulation aux retraits.

== 2. Ce qui vient du papier et ce qui change

#table(
  columns: 3,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: (left + top, left + top, left + top),
  inset: 5pt,
    [*Élément*],
    [*Papier de Vanguard*],
    [*Cette étude*],
    [Limites de l'ajustement annuel],
    [Plancher de −1,5 % et plafond de +5 % dans l'exemple],
    [Même mécanisme, testé sur les deux cas numériques de la figure 6],
    [Scénarios de rendement],
    [Prévisions du modèle privé VCMM],
    [Rendements historiques et rééchantillonnage de blocs d'années],
    [Risque observé],
    [Pérennité et flexibilité des dépenses],
    [Épuisement, fréquence des réductions, durée et montant du manque],
    [Budget minimal absolu],
    [Ne constitue pas notre spécification principale reprise du papier],
    [Ajout d'un seuil à 75 % des dépenses initiales],
    [Diversification],
    [Hypothèses du papier],
    [Portefeuille domestique 50 % actions et 50 % obligations],
)

Le seuil de 30 000 dollars est un choix d'expérience. Il peut être modifié dans la configuration. Il ne prétend pas décrire le coût de la vie de tous les ménages.

== 3. Données et population étudiée

La base Jordà-Schularick-Taylor, version R6, fournit les rendements annuels totaux des actions et des obligations ainsi que les prix à la consommation. Les rendements totaux incluent les revenus distribués. Le millésime se termine en 2020. Les séries américaines communes utilisées commencent en 1872.

Le programme ne comble aucun rendement manquant. Une trajectoire est retenue seulement si toutes ses années et toutes ses variables sont disponibles. Les fenêtres américaines de 40 ans commencent ainsi entre 1872 et 1981. Elles se chevauchent fortement. Cent dix dates de départ ne représentent donc pas cent dix histoires économiques indépendantes.

L'analyse internationale utilise les départs disponibles depuis 1950 dans 16 pays. Chaque ménage détient les actions et obligations de son propre pays et consomme selon son IPC local. Le Canada et l'Irlande n'ont pas les rendements nécessaires dans cette version de la base. Ils sont exclus explicitement.

== 4. Calculer un retrait sans mélanger les unités

Le capital initial vaut un million. Les montants sont toujours exprimés dans le pouvoir d'achat au début de la retraite. Chaque année, le programme applique d'abord le rendement nominal et les frais, puis retire l'effet de l'inflation.

#raw("Capital réel disponible = capital réel précédent × (1 + rendement nominal)\n                         × (1 − frais annuels) / (1 + inflation)\nCapital réel final = capital réel disponible − dépense réelle payée", block: true, lang: "text")

Avec un capital de 1 000 dollars, un rendement de 10 %, des frais de 1 % et une inflation de 5 %, le disponible vaut 1 037,14 dollars réels. Un retrait réel de 40 dollars laisse 997,14 dollars. Soustraire simplement l'inflation du rendement donnerait un résultat différent.

Le premier retrait vaut 40 000 dollars réels après douze mois, pour les quatre règles. Par la suite, le montant constant maintient cette somme. Le retrait proportionnel demande 4 % du disponible. L'ajustement limité borne cette demande entre 98,5 % et 105 % de la dépense réelle de l'année précédente. Sa variante avec budget minimal demande au moins 30 000 dollars.

Le montant payé est le plus petit de la demande et du disponible. Le capital ne peut pas devenir négatif. Après épuisement, les dépenses payées restent nulles. Le programme distingue une demande non financée d'un budget minimal non atteint.

=== Un contrôle fourni par l'article

Dans la figure 6 de Vanguard, un million devient 960 000 dollars après un premier retrait de 40 000 dollars et un rendement nul. Une hausse de 10 % l'année suivante porte le disponible à 1 056 000 dollars. Les 4 % donneraient 42 240 dollars, mais le plafond limite le retrait à 42 000 dollars.

Avec une baisse de 10 %, le disponible vaut 864 000 dollars. Les 4 % donneraient 34 560 dollars. Le plancher annuel limite la réduction et maintient la dépense demandée à 39 400 dollars. Les deux résultats sont des tests indépendants du programme de simulation.

== 5. Ce que montrent les trajectoires américaines

#table(
  columns: 4,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: (left + top, right + top, right + top, right + top),
  inset: 5pt,
    [*Règle*],
    [*Capital épuisé*],
    [*Au moins un an sous le budget*],
    [*Années sous le budget en moyenne*],
    [Montant constant],
    [19,1 %],
    [19,1 %],
    [1,3],
    [Pourcentage du solde],
    [0,0 %],
    [74,5 %],
    [6,8],
    [Ajustement limité],
    [0,0 %],
    [27,3 %],
    [3,3],
    [Ajustement avec budget minimal],
    [0,0 %],
    [0,0 %],
    [0,0],
)

#figure(image("../results/figures/budget_et_capital.svg", width: 100%), caption: [Deux mesures de difficulté])

Le retrait proportionnel préserve un solde, mais accepte des variations immédiates des dépenses. L'ajustement limité lisse ces variations. Il peut toutefois demander davantage que le portefeuille ne peut durablement financer. Ces deux mécanismes expliquent pourquoi aucune colonne ne suffit seule à choisir une règle.

Le budget minimal réussit sur les trajectoires américaines de 40 ans retenues. Cette observation ne signifie pas que le seuil est garanti. Dans les scénarios de 40 ans reconstruits par blocs de cinq années, son capital s'épuise dans 10,2 % des cas.

=== L'ordre des rendements

Un exemple de deux années suffit à comprendre le risque de séquence. On dispose de 100 dollars et l'on retire 10 dollars à la fin de chaque année. Une baisse de 20 % suivie d'une hausse de 25 % laisse 77,50 dollars. Le même rendement composé, dans l'ordre inverse, laisse 82 dollars. Sans retraits, les deux ordres auraient ramené le capital à 100 dollars.

#figure(image("../results/figures/depart_1966.svg", width: 100%), caption: [Départ en 1966])

La trajectoire de 1966 permet de suivre ce mécanisme année par année. Les courbes de dépenses et de capital doivent être lues ensemble. Les augmentations permises après de bonnes années peuvent aussi rendre la dépense future plus difficile à maintenir.

== 6. Comparer les durées sur les mêmes départs

Les fenêtres de 30 ans sont plus nombreuses que celles de 50 ans. Comparer leurs moyennes brutes mélange l'effet de la durée et celui des dates de départ. Le tableau suivant utilise exactement les mêmes départs pour les trois horizons.

#table(
  columns: 4,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: (left + top, right + top, right + top, right + top),
  inset: 5pt,
    [*Durée*],
    [*Montant constant*],
    [*Ajustement limité*],
    [*Avec budget minimal*],
    [30 ans],
    [6,0 %],
    [0,0 %],
    [0,0 %],
    [40 ans],
    [20,0 %],
    [0,0 %],
    [0,0 %],
    [50 ans],
    [32,0 %],
    [4,0 %],
    [10,0 %],
)

Les cellules donnent la part des trajectoires où le capital s'épuise. Ce contrôle évite d'attribuer entièrement à la durée une différence qui viendrait des cohortes disponibles. Les statistiques sur toutes les fenêtres restent publiées dans les tables de résultats.

== 7. Ce que changent les pays et les scénarios

#figure(image("../results/figures/comparaison_pays.svg", width: 100%), caption: [Comparaison internationale])

Chaque cellule indique la part des départs où les dépenses passent au moins une année sous le seuil choisi. Ce sont des portefeuilles domestiques, pas une comparaison de fonds mondiaux accessibles aujourd'hui. Les différences de rendement et d'inflation rendent les expériences américaines insuffisantes pour représenter tous les pays.

Les scénarios reconstruits tirent des blocs contigus de trois, cinq ou dix années américaines. Rendements et inflation restent associés. Chaque règle reçoit les mêmes trajectoires, ce qui rend la comparaison appariée. Dix mille trajectoires sont calculées pour chaque longueur de bloc.

#table(
  columns: 4,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: (left + top, right + top, right + top, right + top),
  inset: 5pt,
    [*Règle*],
    [*Capital épuisé*],
    [*Sous le budget*],
    [*Manque moyen au budget*],
    [Montant constant],
    [14,7 %],
    [14,5 %],
    [3,6 %],
    [Pourcentage du solde],
    [0,0 %],
    [44,1 %],
    [3,1 %],
    [Ajustement limité],
    [9,4 %],
    [20,9 %],
    [2,4 %],
    [Ajustement avec budget minimal],
    [10,2 %],
    [10,1 %],
    [2,2 %],
)

Le manque moyen au budget additionne les dépenses manquantes, puis divise par le budget minimal cumulé sur les quarante années. Une baisse d'un dollar n'a ainsi pas le même poids qu'une longue période sans revenu.

#figure(image("../results/figures/sensibilite_blocs.svg", width: 100%), caption: [Sensibilité au rééchantillonnage])

Les fréquences varient avec les blocs. Une longue crise peut être fragmentée par des blocs courts. À l'inverse, des blocs longs laissent moins de morceaux historiques différents. Le bootstrap ne transforme pas l'histoire américaine en modèle certain du futur. L'erreur de Monte-Carlo publiée mesure seulement le bruit lié au nombre de tirages.

Une dernière table teste des frais annuels de 0 %, 0,2 % et 1 % sur les mêmes départs historiques. Elle isole les frais de la sélection des périodes.

== 8. Limites et portée

La base privilégie des marchés ayant survécu et disposant d'archives longues. Les indices ne reproduisent pas les frais ni les possibilités d'investissement de toutes les époques. La fiscalité, les pensions publiques, les dépenses de santé et la durée de vie individuelle ne sont pas modélisées.

L'analyse n'est pas une calibration pour un ménage canadien. Un prolongement canadien demanderait des rendements nationaux, une fiscalité et des pensions correctement datés. Le budget minimal pourrait alors refléter des dépenses essentielles documentées.

Le résultat utile est méthodologique. Une étude de retraite doit publier ce que la personne consomme, en plus du solde de son portefeuille. La règle gagnante dépend ensuite de la gravité que l'on attribue à une réduction des dépenses, à une longue période de manque et à l'épuisement final.

== 9. Reproduction et contrôles

Le #link("docs/PROTOCOLE.md")[protocole] précède le premier calcul complet mais n'est pas un préenregistrement externe. Les #link("docs/DONNEES.md")[sources], leurs empreintes et les paramètres sont séparés du code. Les tests vérifient les exemples de Vanguard, l'inflation, les frais, l'ordre des rendements, les années manquantes et le plafonnement des retraits.

Les tables CSV alimentent les figures, le classeur et le texte. Le PDF est compilé depuis cet article. Le #link("docs/VERIFICATION.md")[journal de vérification] détaille les contrôles effectivement réalisés.

== English extended summary

This study evaluates retirement withdrawals with two separate outcomes, portfolio depletion and consumption below an explicit minimum budget. The initial portfolio is one million currency units, annual initial spending is 40,000, and the minimum real budget is 30,000. Four rules are compared on historical stock, government bond and inflation observations from JST R6.

The proportional rule avoids depletion in the observed US forty-year cohorts, but spending falls below the minimum in 74,5% of them. Constant real spending depletes the portfolio in 19,1% of cohorts. These are overlapping historical observations, not independent trials or forecasts. Dynamic spending limits improve some outcomes while creating a different trade-off between flexibility and depletion risk.

The study reproduces the numerical ceiling and floor examples in Vanguard's figure 6. It does not replicate VCMM probabilities. Public historical block resampling replaces proprietary capital-market forecasts. International domestic portfolios, common-origin horizon comparisons and fee sensitivities assess how dependent the findings are on US history and implementation choices.

== Références

Costa, P., Pakula, D. et Clarke, A. (2021). #link("https://www.vanguardmexico.com/content/dam/intl/americas/documents/mexico/en/fuel-for-the-fire.pdf")[Fuel for the F.I.R.E.]. Vanguard Research.

Jordà, Ò., Knoll, K., Kuvshinov, D., Schularick, M. et Taylor, A. M. (2019). #link("https://doi.org/10.1093/qje/qjz012")[The Rate of Return on Everything, 1870–2015]. Quarterly Journal of Economics, 134(3), 1225–1298. Données actualisées dans #link("https://www.macrohistory.net/database/")[JST R6].
