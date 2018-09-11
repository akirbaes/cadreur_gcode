# Cadreur gcode
Coupe le gcode (pour plotteur) en dehors du cadre donné

La version Processing est juste la version Python mais prenant un paramètre par variable d'environnement à cause des limitations. (À enlever)
La version Python pure est celle à utiliser car elle ne lance pas Processing à chaque fois.
Drag-and-drop un fichier gcode à découper sur le .py ou plusieurs sur le .bat
Modifier les paramètres dans le fichier lui-même

Les points gcode en dehors de la zone cadrée sont enlevés. 
Les lignes en bordure sont coupées (un point est ajouté là où la ligne rejoint la bordure).

Dans le main, le gcode est mis à l'échelle pour qu'il dépasse le cadre. Puis il est découpé, par défaut selon les valeurs définies tout en haut du fichier.

Le format accepté est pour un plotteur G F X Y Z
G0 ou G1 pour les déplacements, le reste est ignoré (copié tel quel)
Z0 ou Z10 sont les seules valuers
X et Y peut être négatif, à virgules, mais pas un float exponentiel (pas géré dans le regex, pourrait l'être).

Le .bat drag-and-drop version processing utilise le jar qui se trouve dans ../jar. Si vous déplacez le dossier, copiez le jar a proximité ou modifiez le .bat!
Ou simplement utilisez la version python pure.

# Visualiseur gcode
Affiche le résultat des déplacement du plotteur du gcode

L'affichage est en processing.
Drag-and-drop un fichier gcode à afficher sur le .bat pour lancer Processing dessus.

On peut voir étape par étape le code en cliquant-glissant la souris dans la zone de dessin (pour glisser le carré en bas).
Flèche gauche/droite peut aussi avancer/reculer d'une étape.
V pour prendre une capture d'écran (une capture est prise par défaut au début). La capture sera à côté du gcode ouvert.
O pour ouvrir un autre fichier. Cepandant, dû aux limitations de Processing verison Python, la fenêtre ne peut pas changer de taille et ne sera pas adaptée à si le gcode a une taille différente. Drag-and-drop sur le .bat pour ouvrir une nouvelle fois le visualiseur est mieux conseillé si travaillant avec des tailles différentes.

Modifier le fichier pyde pour changer l'échelle au chargement etc.

Le .bat drag-and-drop utilise le jar qui se trouve dans ../jar. Si vous déplacez le dossier, copiez le jar a proximité ou modifiez le .bat!

# Générateur d'image
Version allégée du visualiseur qui créé juste une image et quitte

L'affichage est en processing.
Drang-and-drop plusieurs fichiers gcodes sur le .bat pour lancer le générateur pour chaqun.
Les images seront créées près du gcode.

Le .bat drag-and-drop utilise le jar qui se trouve dans ../jar. Si vous déplacez le dossier, copiez le jar a proximité ou modifiez le .bat!
