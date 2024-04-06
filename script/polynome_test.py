import math
import matplotlib.pyplot as plt

def parabole(x1, x2, y1, y2):
  """
  Calcule les coefficients de la parabole et la fonction pour l'ordonnée.

  Args:
    x1: Racine 1.
    x2: Racine 2.
    y1: Ordonnée de la racine 1.
    y2: Ordonnée de la racine 2.

  Returns:
    Dictionnaire contenant les coefficients a, b et la fonction pour calculer l'ordonnée.
  """

  a = (y2 - y1) / ((x2 - x1)**2)
  b = 2 * a * ((x1 + x2) / 2)

  def f(x):
    return a * (x - (x1 + x2) / 2)**2 + y1

  return {"a": a, "b": b, "f": f}

def simuler_trajectoire(x1, x2, y1, y2, pas):
  """
  Simule la trajectoire d'un projectile en mouvement parabolique.

  Args:
    x1: Racine 1.
    x2: Racine 2.
    y1: Ordonnée de la racine 1.
    y2: Ordonnée de la racine 2.
    pas: Incrémentation de l'abscisse.

  Returns:
    Liste de points représentant la trajectoire.
  """

  trajectoire = []
  for x in range(x1, x2 + 1, pas):
    y = parabole(x1, x2, y1, y2)["f"](x)
    trajectoire.append((x, y))

  # Return the calculated trajectory
  return trajectoire

def afficher_courbe(x, y):
  """
  Affiche la courbe avec Matplotlib.

  Args:
    x: Liste des valeurs d'abscisse.
    y: Liste des valeurs d'ordonnée.
  """

  plt.plot(x, y)
  plt.xlabel("x")
  plt.ylabel("y")
  plt.show()

# Définir les paramètres
x1 = 0  # Position de la tourelle (racine 1)
y1 = 0  # Position Y de la tourelle (inversion de l'axe Y)
x2 = 100  # Position X de la cible
y2 = 50  # Position Y de la cible (inversion de l'axe Y)
hauteur_max = 100  # Hauteur maximale de la trajectoire (pour l'inversion de l'axe Y)
pas = 1  # Incrémentation de l'abscisse

trajectoire = simuler_trajectoire(x1, x2, y1, y2, pas)

# Solution 1: Boucle pour extraire les X
x_trajectoire = []
for point in trajectoire:
  x_trajectoire.append(point[0])

y_trajectoire_inversee = [hauteur_max - int(y) for y in trajectoire]

# Solution 2: List comprehension pour les X (plus concise)
# x_trajectoire = [point[0] for point in trajectoire]
# y_trajectoire_inversee = [hauteur_max - int(y) for y in trajectoire]
# Décommentez ces lignes et commentez la boucle ci-dessus si vous préférez la solution 2

afficher_courbe(x_trajectoire, y_trajectoire_inversee)
