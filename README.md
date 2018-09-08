# cadreur_gcode
Coupe le gcode (pour plotteur) en dehors du cadre donné

Le cadreur.py n'est pas bien testé, la version python 2 est mieux testée.
Juste lancer le code python (testé en le lançant via processing).
Le fichier à travailler est écrit en dur (filename)

Les points gcode en dehors de la zone cadrée sont enlevés. 
Les lignes en bordure sont coupées (un point est ajouté là où la ligne rejoint la bordure).

Dans le main, le gcode est mis à l'échelle pour qu'il dépasse le cadre. Puis il est découpé, par défaut selon les valeurs définies tout en haut du fichier.

Le format accepté est pour un plotteur G F X Y Z
G0 ou G1 pour les déplacements, le reste est ignoré (copié tel quel)
Z0 ou Z10 sont les seules valuers
X et Y peut être négatif, à virgules, mais pas un float exponentiel (pas géré dans le regex, pourrait l'être).
