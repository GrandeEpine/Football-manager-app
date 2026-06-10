# 🏆 Organisateur de Tournoi de Football

Une application complète pour organiser et gérer des tournois de football avec interface graphique moderne et colorée.

## 🎨 Nouveautés

- **✨ Interface colorée** avec thème sombre élégant
- **🔍 Système de recherche** dans chaque onglet
- **🏆 Système de poules** avec phase de groupes et phase finale
- **1 équipe éliminée par poule** automatiquement à la fin de la phase de groupes

---

## 📋 Fonctionnalités

### 🎯 Gestion des Équipes
- Ajouter/Supprimer/Renommer des équipes
- Réinitialiser toutes les statistiques
- Visualisation des stats (points, matchs, victoires, nuls, défaites, buts)
- **Recherche d'équipes** en temps réel

### 🏆 Système de Poules (NEW!)
- Création automatique de poules de 4 équipes
- Chaque poule joue un round-robin (6 matchs par poule)
- **À la fin de la phase de groupes :**
  - Les 3 meilleures équipes de chaque poule sont **qualifiées** ✅
  - La dernière équipe de chaque poule est **éliminée** ✗
- Passage automatique à la phase finale (knockout)
- Visualisation des groupes avec couleurs distinctes

### ⚽ Gestion des Matchs
- Génération automatique des matchs de groupe
- Génération automatique des matchs de phase finale
- Entrer/modifier les résultats
- Suppression de matchs
- **Recherche de matchs** par équipe, groupe, ou tour

### 📊 Classement
- Classement automatique par groupe
- Classement global
- Affichage du statut (Qualifiée/Éliminée)
- **Recherche d'équipes** dans le classement

### 🥇 Phase Finale (Knockout)
- Génération automatique du tableau final
- Matchs classés par tour (Huitième, Quart, Demi, Finale)
- gestion séparée des matchs de groupe et knockout

### 📈 Statistiques
- Nombre total d'équipes et de matchs
- Matchs joués et à jouer
- Total des buts marqués
- Moyenne de buts par match
- Top 3 des équipes par catégorie (Points, Buts, Différence, Victoires)

### 💾 Sauvegarde CSV
- Sauvegarde automatique dans `data/`
- 5 fichiers CSV :
  - `tournament.csv` - Infos du tournoi
  - `teams.csv` - Équipes et leurs statistiques
  - `matches.csv` - Matchs de groupe
  - `knockout_matches.csv` - Matchs de phase finale
  - `groups.csv` - Poules et leurs équipes
- Chargement automatique au démarrage
- **Si ça crash, relancez et chargez les données !**

---

## 📁 Structure du Projet

```
football/
├── main.py          # Point d'entrée
├── app.py           # Interface graphique (Tkinter)
├── model.py         # Classes (Team, Match, Group, Tournament)
├── saver.py         # Sauvegarde/Chargement CSV
├── colors.py        # Palette de couleurs
├── README.md        # Documentation
└── requirements.txt # Dépendances
```

---

## 🚀 Installation & Utilisation

### Prérequis
- Python 3.8+
- Tkinter (inclus avec Python standard)

### Lancement

```bash
cd football
python3 main.py
```

---

## 🎯 Workflow Typique avec Poules

### 1. Créer un Nouveau Tournoi
- **Fichier → Nouveau Tournoi** (ou laisse le nom par défaut)

### 2. Ajouter des Équipes
- **Onglet "Équipes" → Ajouter** (PSG, OM, Lyon, Monaco, Lille, Bordeaux, etc.)
- Minimum 4 équipes pour créer des poules

### 3. Créer des Poules
- **Onglet "Poules" → Créer Poules (4)**
- L'application crée automatiquement des groupes de 4 équipes
- Chaque équipe est assignée à un groupe (Groupe A, Groupe B, etc.)

### 4. Jouer les Matchs de Groupe
- **Onglet "Matchs"** : Tous les matchs sont générés
- Sélectionnez un match → **Résultat** → Entre les scores
- Les points et stats sont mis à jour automatiquement

### 5. Passer à la Phase Finale
- Une fois tous les matchs de groupe joués (ou manuellement) :
- **Onglet "Poules" → Phase Finale** ou **Menu Poules → Phase Finale**
- L'application :
  - Calcule le classement de chaque groupe
  - **Qualifie les 3 premières** de chaque poule ✅
  - **Élimine la dernière** de chaque poule ✗
  - Génère automatiquement les matchs de phase finale

### 6. Jouer la Phase Finale
- **Onglet "Phase Finale"** : Matchs knockout générés
- Jouez les matchs comme d'habitude
- Le gagnant de la finale est le champion ! 🏆

---

## 🎨 Interface Graphique

### Onglets Disponibles

| Onglet | Description |
|--------|-------------|
| **Équipes** | Gestion des équipes avec recherche |
| **Poules** | Visualisation des groupes et génération phase finale |
| **Matchs** | Liste de tous les matchs (groupes + knockout) avec recherche |
| **Classement** | Classement par groupe ou global avec statut |
| **Phase Finale** | Matchs de knockout avec recherche |
| **Statistiques** | Stats générales et top 3 |

### Menu

```
Fichier    → Nouveau Tournoi, Sauvegarder, Charger, Quitter
Équipes    → Ajouter Équipe, Générer Matchs
Poules     → Créer Poules (4), Phase Finale
Affichage  → Rafraîchir
```

---

## 📊 Exemple de Système de Poules

### Avec 8 équipes :
```
Groupe A: PSG, OM, Lyon, Monaco
Groupe B: Lille, Bordeaux, Nantes, Rennes
```

### Phase de Groupes :
- Chaque équipe joue contre les 3 autres de son groupe
- 6 matchs par groupe (12 matchs au total)
- Classement par groupe :
  - 1er : 9-12 pts → **Qualifié**
  - 2e : 6-9 pts → **Qualifié**
  - 3e : 3-6 pts → **Qualifié**
  - 4e : 0-3 pts → **Éliminé** ✗

### Phase Finale :
- 6 équipes qualifiées (3 par groupe)
- Matchs générés aléatoirement
- Tours : Demi-finale → Finale (ou plus selon le nombre)

---

## 💡 Astuces

### Raccourcis
- **Recherche** : Commencez à taper dans le champ de recherche pour filtrer
- **Sauvegarde** : Fichier → Sauvegarder (ou Ctrl+S à implémenter)
- **Chargement** : Les données sont chargées automatiquement au démarrage

### Gestion des Erreurs
- Si l'app crash : **relancez `python3 main.py`**
- Les données sont dans le dossier `data/`
- **Fichier → Charger** pour restaurer

### Personnalisation
- **Couleurs** : Modifiez `colors.py` pour changer le thème
- **Nombre de qualifiés** : Changez `teams_to_qualify` dans le code (défaut: 3)
- **Taille des poules** : Utilisez différentes tailles avec `create_groups(n)`

---

## 🎯 Exemple de Fichiers CSV

### data/groups.csv
```csv
name,teams,color
Groupe A,PSG;OM;Lyon;Monaco,#e74c3c
Groupe B,Lille;Bordeaux;Nantes;Rennes,#3498db
```

### data/teams.csv
```csv
name,points,goals_for,goals_against,played,won,draw,lost,group,qualified,eliminated
PSG,9,10,2,3,3,0,0,Groupe A,True,False
OM,6,5,4,3,2,0,1,Groupe A,True,False
Lyon,3,2,5,3,1,0,2,Groupe A,True,False
Monaco,0,1,8,3,0,0,3,Groupe A,False,True
```

---

## 🔧 Dépendances

Aucune dépendance externe ! Bibliothèques Python standard utilisées :
- `tkinter` - Interface graphique
- `csv` - Gestion des fichiers CSV
- `datetime` - Dates et heures
- `random` - Mélange aléatoire
- `typing` - Types annotations

---

## 🐛 Problèmes Connus & Solutions

### Problème : Les couleurs ne s'affichent pas
**Solution** : Vérifiez que Tkinter est installé. Sur certaines distributions Linux :
```bash
sudo apt-get install python3-tk
```

### Problème : L'interface est trop grande
**Solution** : Redimensionnez la fenêtre manuellement ou modifiez la taille par défaut dans `app.py`

---

## 📝 Historique des Versions

### v2.0 (Nouveau !)
- ✅ Interface colorée avec thème sombre
- ✅ Système de recherche dans tous les onglets
- ✅ Système de poules avec phase de groupes
- ✅ Phase finale (knockout) automatique
- ✅ Élimination de 1 équipe par poule

### v1.0
- Gestion basique des équipes et matchs
- Sauvegarde/Chargement CSV
- Classement automatique

---

## 🎉 Auteur

Créé avec ❤️ pour les passionnés de football

**Prêt à organiser ton tournoi ?** 🚀
Lance `python3 main.py` et amuse-toi bien ! ⚽
