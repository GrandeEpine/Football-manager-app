# Organisateur de Tournoi de Football

Une application complète pour organiser et gérer des tournois de football avec interface graphique.

## Fonctionnalités

### 🎯 Gestion des Équipes
- Ajouter des équipes
- Supprimer des équipes
- Renommer des équipes
- Visualisation des statistiques par équipe (points, matchs joués, victoires, nuls, défaites, buts pour/contre)

### ⚽ Gestion des Matchs
- Génération automatique de tous les matchs possibles (round-robin)
- Entrer les résultats des matchs
- Modifier les résultats existants
- Suppression de matchs
- Affichage des matchs à jouer/joués

### 🏆 Classement
- Classement automatique basé sur les points
- Tri par: points, différence de buts, buts marqués
- Affichage complet du classement

### 📊 Statistiques
- Nombre total d'équipes et de matchs
- Matchs joués et à jouer
- Total des buts marqués
- Moyenne de buts par match
- Top 3 des équipes par différentes statistiques

### 💾 Sauvegarde & Chargement
- Sauvegarde automatique dans le dossier `data/`
- 3 fichiers CSV créés:
  - `teams.csv` - Toutes les équipes et leurs statistiques
  - `matches.csv` - Tous les matchs et leurs résultats
  - `tournament.csv` - Informations du tournoi
- Chargement des données existantes au démarrage
- Création d'un nouveau tournoi à tout moment

## Installation

### Prérequis
- Python 3.6 ou supérieur
- Tkinter (généralement inclus avec Python)

### Étapes

1. Cloner ou télécharger le dépôt
2. Naviguer dans le dossier du projet:
   ```bash
   cd football
   ```

3. Exécuter l'application:
   ```bash
   python3 main.py
   ```

## Utilisation

### Démarrage rapide
1. **Ajouter des équipes**: Allez dans l'onglet "Équipes" et cliquez sur "Ajouter Équipe"
2. **Générer les matchs**: Cliquez sur "Générer Tous les Matchs" dans l'onglet "Matchs"
3. **Entrer les résultats**: Sélectionnez un match et cliquez sur "Entrer Résultat"
4. **Voir le classement**: Allez dans l'onglet "Classement"

### Menu
- **Fichier** → Nouveau Tournoi, Sauvegarder, Charger, Quitter
- **Équipes** → Ajouter Équipe, Générer Matchs
- **Affichage** → Rafraîchir

### raccourcis
- Sauvegardez régulièrement avec **Fichier → Sauvegarder**
- Les données sont automatiquement chargées au démarrage si disponibles

## Structure des Fichiers CSV

### teams.csv
```csv
name,points,goals_for,goals_against,played,won,draw,lost
PSG,9,10,2,3,3,0,0
OM,3,5,7,3,1,0,2
...
```

### matches.csv
```csv
team1,team2,score1,score2,played,date
PSG,OM,3,1,True,2024-01-15 14:30
OM,Lyon,,,False,2024-01-15 14:30
...
```

### tournament.csv
```csv
name,team_count,match_count,generated
Mon Tournoi,4,6,True
```

## Dépendances

Aucune dépendance externe nécessaire ! L'application utilise uniquement les bibliothèques standard de Python:
- `csv` - Pour la gestion des fichiers CSV
- `tkinter` - Pour l'interface graphique
- `datetime` - Pour les dates
- `random` - Pour mélanger les matchs

## Compatibilité

Testé avec:
- Python 3.8+
- Windows, Linux, macOS

## Auteur

Créé avec ❤️ pour les passionnés de football

## Licence

Libre d'utilisation pour un usage personnel ou éducatif.
