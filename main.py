#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application d'organisation de tournoi de football
Sauvegarde les équipes, matchs et scores dans des fichiers CSV
"""

import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random


# =============================================================================
# MODÈLE - Classes de données
# =============================================================================

@dataclass
class Team:
    """Représente une équipe de football"""
    name: str
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0
    played: int = 0
    won: int = 0
    draw: int = 0
    lost: int = 0
    
    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against
    
    def add_result(self, goals_for: int, goals_against: int, is_win: bool, is_draw: bool):
        """Mise à jour des stats après un match"""
        self.goals_for += goals_for
        self.goals_against += goals_against
        self.played += 1
        
        if is_win:
            self.won += 1
            self.points += 3
        elif is_draw:
            self.draw += 1
            self.points += 1
        else:
            self.lost += 1


@dataclass
class Match:
    """Représente un match entre deux équipes"""
    team1: str
    team2: str
    score1: Optional[int] = None
    score2: Optional[int] = None
    played: bool = False
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    @property
    def is_complete(self) -> bool:
        return self.played and self.score1 is not None and self.score2 is not None
    
    def get_result(self) -> Optional[str]:
        """Retourne le résultat du match"""
        if not self.is_complete or self.score1 is None or self.score2 is None:
            return None
        if self.score1 > self.score2:
            return f"{self.team1} gagne"
        elif self.score2 > self.score1:
            return f"{self.team2} gagne"
        else:
            return "Match nul"


class Tournament:
    """Gère le tournoi complet"""
    
    def __init__(self, name: str = "Mon Tournoi"):
        self.name = name
        self.teams: Dict[str, Team] = {}
        self.matches: List[Match] = []
        self.generated_matches: bool = False
    
    def add_team(self, team_name: str) -> bool:
        """Ajoute une équipe si elle n'existe pas"""
        if team_name.strip() == "":
            return False
        if team_name not in self.teams:
            self.teams[team_name] = Team(team_name)
            self.generated_matches = False
            return True
        return False
    
    def remove_team(self, team_name: str) -> bool:
        """Supprime une équipe"""
        if team_name in self.teams:
            # Supprimer les matchs impliquant cette équipe
            self.matches = [m for m in self.matches 
                          if m.team1 != team_name and m.team2 != team_name]
            del self.teams[team_name]
            self.generated_matches = False
            return True
        return False
    
    def generate_matches(self) -> List[Match]:
        """Génère tous les matchs possibles (aller simple)"""
        team_names = list(self.teams.keys())
        new_matches = []
        
        for i in range(len(team_names)):
            for j in range(i + 1, len(team_names)):
                match = Match(team_names[i], team_names[j])
                new_matches.append(match)
        
        # Mélanger pour un ordre aléatoire
        random.shuffle(new_matches)
        self.matches = new_matches
        self.generated_matches = True
        return new_matches
    
    def record_match_result(self, match: Match, score1: int, score2: int) -> bool:
        """Enregistre le résultat d'un match et met à jour les équipes"""
        if match.team1 not in self.teams or match.team2 not in self.teams:
            return False
        
        match.score1 = score1
        match.score2 = score2
        match.played = True
        match.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Mettre à jour les stats des équipes
        is_win_team1 = score1 > score2
        is_draw = score1 == score2
        
        self.teams[match.team1].add_result(score1, score2, is_win_team1, is_draw)
        self.teams[match.team2].add_result(score2, score1, not is_win_team1 and not is_draw, is_draw)
        
        return True
    
    def get_standings(self) -> List[Team]:
        """Retourne le classement trié"""
        sorted_teams = sorted(self.teams.values(), 
                             key=lambda t: (-t.points, -t.goal_difference, -t.goals_for, t.name))
        return sorted_teams
    
    def get_team(self, name: str) -> Optional[Team]:
        return self.teams.get(name)
    
    def get_unplayed_matches(self) -> List[Match]:
        return [m for m in self.matches if not m.played]
    
    def get_played_matches(self) -> List[Match]:
        return [m for m in self.matches if m.played]


# =============================================================================
# SAUVEGARDE / CHARGEMENT CSV
# =============================================================================

class TournamentSaver:
    """Gère la sauvegarde et le chargement depuis CSV"""
    
    DATA_DIR = "data"
    TEAMS_FILE = os.path.join(DATA_DIR, "teams.csv")
    MATCHES_FILE = os.path.join(DATA_DIR, "matches.csv")
    TOURNAMENT_FILE = os.path.join(DATA_DIR, "tournament.csv")
    
    @staticmethod
    def ensure_data_dir():
        """Crée le dossier data s'il n'existe pas"""
        if not os.path.exists(TournamentSaver.DATA_DIR):
            os.makedirs(TournamentSaver.DATA_DIR)
    
    @staticmethod
    def save_tournament(tournament: Tournament) -> bool:
        """Sauvegarde le tournoi dans des fichiers CSV"""
        try:
            TournamentSaver.ensure_data_dir()
            
            # Sauvegarder les info du tournoi
            with open(TournamentSaver.TOURNAMENT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'team_count', 'match_count', 'generated'])
                writer.writerow([
                    tournament.name,
                    len(tournament.teams),
                    len(tournament.matches),
                    tournament.generated_matches
                ])
            
            # Sauvegarder les équipes
            with open(TournamentSaver.TEAMS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'points', 'goals_for', 'goals_against', 
                                'played', 'won', 'draw', 'lost'])
                for team in tournament.teams.values():
                    writer.writerow([
                        team.name, team.points, team.goals_for, team.goals_against,
                        team.played, team.won, team.draw, team.lost
                    ])
            
            # Sauvegarder les matchs
            with open(TournamentSaver.MATCHES_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['team1', 'team2', 'score1', 'score2', 'played', 'date'])
                for match in tournament.matches:
                    writer.writerow([
                        match.team1, match.team2,
                        match.score1 if match.score1 is not None else '',
                        match.score2 if match.score2 is not None else '',
                        match.played, match.date
                    ])
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    @staticmethod
    def load_tournament() -> Optional[Tournament]:
        """Charge un tournoi depuis les fichiers CSV"""
        try:
            # Vérifier si les fichiers existent
            if not (os.path.exists(TournamentSaver.TOURNAMENT_FILE) and 
                   os.path.exists(TournamentSaver.TEAMS_FILE) and 
                   os.path.exists(TournamentSaver.MATCHES_FILE)):
                return None
            
            tournament = None
            
            # Charger les info du tournoi
            with open(TournamentSaver.TOURNAMENT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) >= 2:
                    name, team_count, match_count, generated = rows[1]
                    tournament = Tournament(name)
                    tournament.generated_matches = generated.lower() == 'true'
            
            if tournament is None:
                tournament = Tournament()
            
            # Charger les équipes
            with open(TournamentSaver.TEAMS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 8:
                        team = Team(
                            name=row[0],
                            points=int(row[1]) if row[1] else 0,
                            goals_for=int(row[2]) if row[2] else 0,
                            goals_against=int(row[3]) if row[3] else 0,
                            played=int(row[4]) if row[4] else 0,
                            won=int(row[5]) if row[5] else 0,
                            draw=int(row[6]) if row[6] else 0,
                            lost=int(row[7]) if row[7] else 0
                        )
                        tournament.teams[team.name] = team
            
            # Charger les matchs
            with open(TournamentSaver.MATCHES_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 6:
                        match = Match(
                            team1=row[0],
                            team2=row[1],
                            score1=int(row[2]) if row[2] else None,
                            score2=int(row[3]) if row[3] else None,
                            played=row[4].lower() == 'true',
                            date=row[5]
                        )
                        tournament.matches.append(match)
            
            return tournament
            
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return None


# =============================================================================
# INTERFACE GRAPHIQUE
# =============================================================================

class TournamentApp:
    """Interface graphique principale"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.tournament = Tournament()
        self.current_match_index = 0
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.root.title("Organisateur de Tournoi de Football")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Treeview', font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Équipes
        self.setup_teams_tab()
        
        # Onglet Matchs
        self.setup_matches_tab()
        
        # Onglet Classement
        self.setup_standings_tab()
        
        # Onglet Statistiques
        self.setup_stats_tab()
        
        # Menu
        self.setup_menu()
        
        # Barre d'état
        self.status_bar = ttk.Label(self.root, text="Prêt", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def setup_menu(self):
        """Configuration du menu"""
        menubar = tk.Menu(self.root)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouveau Tournoi", command=self.new_tournament)
        file_menu.add_command(label="Sauvegarder", command=self.save_data)
        file_menu.add_command(label="Charger", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Équipes
        team_menu = tk.Menu(menubar, tearoff=0)
        team_menu.add_command(label="Ajouter Équipe", command=self.add_team_dialog)
        team_menu.add_command(label="Générer Matchs", command=self.generate_matches)
        menubar.add_cascade(label="Équipes", menu=team_menu)
        
        # Menu Affichage
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Rafraîchir", command=self.refresh_all)
        menubar.add_cascade(label="Affichage", menu=view_menu)
        
        self.root.config(menu=menubar)
    
    def setup_teams_tab(self):
        """Onglet pour gérer les équipes"""
        teams_frame = ttk.Frame(self.notebook)
        self.notebook.add(teams_frame, text="Équipes")
        
        # Frame pour les boutons
        button_frame = ttk.Frame(teams_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Ajouter Équipe", command=self.add_team_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.remove_selected_team).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Renommer", command=self.rename_team_dialog).pack(side=tk.LEFT, padx=5)
        
        # Treeview pour afficher les équipes
        columns = ('name', 'points', 'played', 'won', 'draw', 'lost', 'gf', 'ga', 'gd')
        self.teams_tree = ttk.Treeview(teams_frame, columns=columns, show='headings', selectmode='browse')
        
        # Configuration des colonnes
        column_titles = {
            'name': 'Équipe',
            'points': 'Pts',
            'played': 'J',
            'won': 'G',
            'draw': 'N',
            'lost': 'P',
            'gf': 'BP',
            'ga': 'BC',
            'gd': '+/-'
        }
        
        for col in columns:
            self.teams_tree.heading(col, text=column_titles[col], anchor=tk.CENTER)
            self.teams_tree.column(col, anchor=tk.CENTER, width=80)
        
        self.teams_tree.column('name', anchor=tk.W, width=200)
        
        self.teams_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(teams_frame, orient=tk.VERTICAL, command=self.teams_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teams_tree.configure(yscrollcommand=scrollbar.set)
    
    def setup_matches_tab(self):
        """Onglet pour gérer les matchs"""
        matches_frame = ttk.Frame(self.notebook)
        self.notebook.add(matches_frame, text="Matchs")
        
        # Frame pour les boutons
        button_frame = ttk.Frame(matches_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Générer Tous les Matchs", command=self.generate_matches).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Entrer Résultat", command=self.enter_result_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer Match", command=self.remove_selected_match).pack(side=tk.LEFT, padx=5)
        
        # Treeview pour les matchs
        columns = ('team1', 'team2', 'score', 'played', 'date', 'result')
        self.matches_tree = ttk.Treeview(matches_frame, columns=columns, show='headings', selectmode='browse')
        
        column_titles = {
            'team1': 'Équipe 1',
            'team2': 'Équipe 2',
            'score': 'Score',
            'played': 'Joué',
            'date': 'Date',
            'result': 'Résultat'
        }
        
        for col in columns:
            self.matches_tree.heading(col, text=column_titles[col], anchor=tk.CENTER)
            self.matches_tree.column(col, anchor=tk.CENTER, width=100)
        
        self.matches_tree.column('team1', anchor=tk.W, width=150)
        self.matches_tree.column('team2', anchor=tk.W, width=150)
        self.matches_tree.column('date', width=150)
        self.matches_tree.column('result', width=150)
        
        self.matches_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(matches_frame, orient=tk.VERTICAL, command=self.matches_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.matches_tree.configure(yscrollcommand=scrollbar.set)
        
        # Info
        info_frame = ttk.Frame(matches_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.matches_info = ttk.Label(info_frame, text="Matchs à jouer: 0 | Matchs joués: 0")
        self.matches_info.pack(side=tk.LEFT)
    
    def setup_standings_tab(self):
        """Onglet pour afficher le classement"""
        standings_frame = ttk.Frame(self.notebook)
        self.notebook.add(standings_frame, text="Classement")
        
        # Treeview pour le classement
        columns = ('rank', 'team', 'points', 'played', 'won', 'draw', 'lost', 'gf', 'ga', 'gd')
        self.standings_tree = ttk.Treeview(standings_frame, columns=columns, show='headings')
        
        column_titles = {
            'rank': 'Rang',
            'team': 'Équipe',
            'points': 'Pts',
            'played': 'J',
            'won': 'G',
            'draw': 'N',
            'lost': 'P',
            'gf': 'BP',
            'ga': 'BC',
            'gd': '+/-'
        }
        
        for col in columns:
            self.standings_tree.heading(col, text=column_titles[col], anchor=tk.CENTER)
            self.standings_tree.column(col, anchor=tk.CENTER, width=60)
        
        self.standings_tree.column('team', anchor=tk.W, width=200)
        
        self.standings_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(standings_frame, orient=tk.VERTICAL, command=self.standings_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.standings_tree.configure(yscrollcommand=scrollbar.set)
    
    def setup_stats_tab(self):
        """Onglet pour les statistiques"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistiques")
        
        # Frame pour les stats générales
        general_stats = ttk.LabelFrame(stats_frame, text="Statistiques Générales", padding=20)
        general_stats.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_labels = {}
        stats_texts = [
            ("total_teams", "Nombre d'équipes: "),
            ("total_matches", "Total des matchs: "),
            ("played_matches", "Matchs joués: "),
            ("unplayed_matches", "Matchs à jouer: "),
            ("total_goals", "Buts marqués au total: "),
            ("avg_goals", "Moyenne de buts par match: "),
        ]
        
        for key, text in stats_texts:
            row_frame = ttk.Frame(general_stats)
            row_frame.pack(fill=tk.X, pady=5)
            ttk.Label(row_frame, text=text, width=25, anchor=tk.W).pack(side=tk.LEFT)
            self.stats_labels[key] = ttk.Label(row_frame, text="0", font=('Arial', 10, 'bold'))
            self.stats_labels[key].pack(side=tk.LEFT)
        
        # Meilleurs buteurs (à venir)
        top_frame = ttk.LabelFrame(stats_frame, text="Meilleures Équipes", padding=20)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.top_tree = ttk.Treeview(top_frame, columns=('team', 'stat', 'value'), show='headings')
        self.top_tree.heading('team', text='Équipe')
        self.top_tree.heading('stat', text='Statistique')
        self.top_tree.heading('value', text='Valeur')
        
        self.top_tree.column('team', width=150)
        self.top_tree.column('stat', width=150)
        self.top_tree.column('value', width=100)
        
        self.top_tree.pack(fill=tk.BOTH, expand=True)
    
    # =========================================================================
    # FONCTIONS POUR LES ÉQUIPES
    # =========================================================================
    
    def add_team_dialog(self):
        """Ouvre une boîte de dialogue pour ajouter une équipe"""
        team_name = simpledialog.askstring("Ajouter Équipe", "Nom de l'équipe:")
        if team_name and team_name.strip():
            team_name = team_name.strip()
            if self.tournament.add_team(team_name):
                self.update_teams_tree()
                self.update_standings_tree()
                self.update_stats()
                self.update_matches_tree()
                self.status_bar.config(text=f"Équipe '{team_name}' ajoutée")
            else:
                messagebox.showerror("Erreur", f"L'équipe '{team_name}' existe déjà!")
    
    def remove_selected_team(self):
        """Supprime l'équipe sélectionnée"""
        selected = self.teams_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Aucune équipe sélectionnée!")
            return
        
        item = self.teams_tree.item(selected[0])
        team_name = item['values'][0]
        
        confirm = messagebox.askyesno("Confirmer", f"Supprimer l'équipe '{team_name}'?")
        if confirm:
            if self.tournament.remove_team(team_name):
                self.update_teams_tree()
                self.update_standings_tree()
                self.update_matches_tree()
                self.update_stats()
                self.status_bar.config(text=f"Équipe '{team_name}' supprimée")
    
    def rename_team_dialog(self):
        """Renomme l'équipe sélectionnée"""
        selected = self.teams_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Aucune équipe sélectionnée!")
            return
        
        item = self.teams_tree.item(selected[0])
        old_name = item['values'][0]
        
        new_name = simpledialog.askstring("Renommer", f"Nouveau nom pour '{old_name}':")
        if new_name and new_name.strip() and new_name != old_name:
            new_name = new_name.strip()
            if new_name in self.tournament.teams:
                messagebox.showerror("Erreur", f"L'équipe '{new_name}' existe déjà!")
                return
            
            # Créer une nouvelle équipe avec les stats de l'ancienne
            old_team = self.tournament.teams[old_name]
            new_team = Team(
                name=new_name,
                points=old_team.points,
                goals_for=old_team.goals_for,
                goals_against=old_team.goals_against,
                played=old_team.played,
                won=old_team.won,
                draw=old_team.draw,
                lost=old_team.lost
            )
            
            # Ajouter la nouvelle équipe
            self.tournament.teams[new_name] = new_team
            
            # Mettre à jour les matchs
            for match in self.tournament.matches:
                if match.team1 == old_name:
                    match.team1 = new_name
                if match.team2 == old_name:
                    match.team2 = new_name
            
            # Supprimer l'ancienne
            del self.tournament.teams[old_name]
            
            self.update_teams_tree()
            self.update_standings_tree()
            self.update_matches_tree()
            self.status_bar.config(text=f"Équipe renommée en '{new_name}'")
    
    def update_teams_tree(self):
        """Met à jour l'affichage des équipes"""
        for item in self.teams_tree.get_children():
            self.teams_tree.delete(item)
        
        for team in sorted(self.tournament.teams.values(), key=lambda t: t.name):
            self.teams_tree.insert('', 'end', values=(
                team.name,
                team.points,
                team.played,
                team.won,
                team.draw,
                team.lost,
                team.goals_for,
                team.goals_against,
                team.goal_difference
            ))
    
    # =========================================================================
    # FONCTIONS POUR LES MATCHS
    # =========================================================================
    
    def generate_matches(self):
        """Génère tous les matchs possibles"""
        if len(self.tournament.teams) < 2:
            messagebox.showwarning("Attention", "Il faut au moins 2 équipes pour générer des matchs!")
            return
        
        confirm = messagebox.askyesno(
            "Confirmer",
            f"Générer {len(self.tournament.teams) * (len(self.tournament.teams) - 1) // 2} matchs?"
        )
        if confirm:
            self.tournament.generate_matches()
            self.update_matches_tree()
            self.update_stats()
            self.status_bar.config(text=f"{len(self.tournament.matches)} matchs générés")
    
    def enter_result_dialog(self):
        """Ouvre une boîte de dialogue pour entrer le résultat d'un match"""
        selected = self.matches_tree.selection()
        if not selected:
            # Si aucun match sélectionné, prendre le premier non joué
            unplayed = self.tournament.get_unplayed_matches()
            if unplayed:
                match = unplayed[0]
            else:
                messagebox.showinfo("Info", "Tous les matchs ont été joués!")
                return
        else:
            item = self.matches_tree.item(selected[0])
            values = item['values']
            # Trouver le match correspondant
            match = None
            for m in self.tournament.matches:
                if (m.team1 == values[0] and m.team2 == values[1]) or \
                   (m.team1 == values[1] and m.team2 == values[0]):
                    match = m
                    break
            
            if match is None:
                messagebox.showerror("Erreur", "Match introuvable!")
                return
        
        if match.played:
            confirm = messagebox.askyesno(
                "Modifier",
                f"Ce match a déjà été joué. Voulez-vous modifier le résultat?"
            )
            if not confirm:
                return
        
        # Créer une boîte de dialogue personnalisée
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Résultat: {match.team1} vs {match.team2}")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"{match.team1} vs {match.team2}", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text=f"{match.team1}:").grid(row=1, column=0, sticky=tk.E, pady=5)
        score1_var = tk.StringVar(value=str(match.score1) if match.score1 is not None else "0")
        score1_entry = ttk.Entry(frame, textvariable=score1_var, width=5)
        score1_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text=f"{match.team2}:").grid(row=2, column=0, sticky=tk.E, pady=5)
        score2_var = tk.StringVar(value=str(match.score2) if match.score2 is not None else "0")
        score2_entry = ttk.Entry(frame, textvariable=score2_var, width=5)
        score2_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        def save_result():
            try:
                score1 = int(score1_var.get())
                score2 = int(score2_var.get())
                
                if score1 < 0 or score2 < 0:
                    messagebox.showerror("Erreur", "Les scores doivent être positifs!")
                    return
                
                self.tournament.record_match_result(match, score1, score2)
                self.update_matches_tree()
                self.update_teams_tree()
                self.update_standings_tree()
                self.update_stats()
                self.status_bar.config(text=f"Résultat enregistré: {match.team1} {score1}-{score2} {match.team2}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des nombres valides!")
        
        ttk.Button(button_frame, text="Enregistrer", command=save_result).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        dialog.resizable(False, False)
        score1_entry.focus_set()
    
    def remove_selected_match(self):
        """Supprime le match sélectionné"""
        selected = self.matches_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Aucun match sélectionné!")
            return
        
        item = self.matches_tree.item(selected[0])
        values = item['values']
        
        # Trouver le match
        match_to_remove = None
        for i, m in enumerate(self.tournament.matches):
            if (m.team1 == values[0] and m.team2 == values[1]) or \
               (m.team1 == values[1] and m.team2 == values[0]):
                match_to_remove = m
                self.current_match_index = i
                break
        
        if match_to_remove:
            confirm = messagebox.askyesno(
                "Confirmer",
                f"Supprimer le match {match_to_remove.team1} vs {match_to_remove.team2}?"
            )
            if confirm:
                if match_to_remove is None:
                    messagebox.showerror("Erreur", "Match introuvable!")
                    return

                # Si le match a été joué, annuler les stats
                if match_to_remove.played and match_to_remove.score1 is not None and match_to_remove.score2 is not None:
                    # Retirer les points
                    team1 = self.tournament.get_team(match_to_remove.team1)
                    team2 = self.tournament.get_team(match_to_remove.team2)
                    
                    if team1 and team2:
                        # Annuler le match
                        team1.points -= 3 if match_to_remove.score1 > match_to_remove.score2 else (1 if match_to_remove.score1 == match_to_remove.score2 else 0)
                        team2.points -= 3 if match_to_remove.score2 > match_to_remove.score1 else (1 if match_to_remove.score1 == match_to_remove.score2 else 0)
                        
                        team1.goals_for -= match_to_remove.score1
                        team1.goals_against -= match_to_remove.score2
                        team1.played -= 1
                        
                        team2.goals_for -= match_to_remove.score2
                        team2.goals_against -= match_to_remove.score1
                        team2.played -= 1
                        
                        if match_to_remove.score1 > match_to_remove.score2:
                            team1.won -= 1
                            team2.lost -= 1
                        elif match_to_remove.score2 > match_to_remove.score1:
                            team2.won -= 1
                            team1.lost -= 1
                        else:
                            team1.draw -= 1
                            team2.draw -= 1
                
                self.tournament.matches.remove(match_to_remove)
                self.update_matches_tree()
                self.update_teams_tree()
                self.update_standings_tree()
                self.update_stats()
                self.status_bar.config(text=f"Match supprimé")
    
    def update_matches_tree(self):
        """Met à jour l'affichage des matchs"""
        for item in self.matches_tree.get_children():
            self.matches_tree.delete(item)
        
        for match in sorted(self.tournament.matches, key=lambda m: (not m.played, m.date)):
            score = f"{match.score1}-{match.score2}" if match.is_complete else "-"
            played = "Oui" if match.played else "Non"
            result = match.get_result() or "À jouer"
            
            self.matches_tree.insert('', 'end', values=(
                match.team1,
                match.team2,
                score,
                played,
                match.date,
                result
            ))
        
        # Mettre à jour l'info
        unplayed = len(self.tournament.get_unplayed_matches())
        played = len(self.tournament.get_played_matches())
        self.matches_info.config(text=f"Matchs à jouer: {unplayed} | Matchs joués: {played}")
    
    # =========================================================================
    # FONCTIONS POUR LE CLASSEMENT
    # =========================================================================
    
    def update_standings_tree(self):
        """Met à jour l'affichage du classement"""
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)
        
        standings = self.tournament.get_standings()
        
        for rank, team in enumerate(standings, 1):
            self.standings_tree.insert('', 'end', values=(
                rank,
                team.name,
                team.points,
                team.played,
                team.won,
                team.draw,
                team.lost,
                team.goals_for,
                team.goals_against,
                team.goal_difference
            ))
    
    # =========================================================================
    # FONCTIONS POUR LES STATISTIQUES
    # =========================================================================
    
    def update_stats(self):
        """Met à jour les statistiques"""
        # Stats générales
        self.stats_labels['total_teams'].config(text=str(len(self.tournament.teams)))
        self.stats_labels['total_matches'].config(text=str(len(self.tournament.matches)))
        self.stats_labels['played_matches'].config(text=str(len(self.tournament.get_played_matches())))
        self.stats_labels['unplayed_matches'].config(text=str(len(self.tournament.get_unplayed_matches())))
        
        # Calculer les buts totaux
        total_goals = sum(
            (m.score1 or 0) + (m.score2 or 0) 
            for m in self.tournament.matches 
            if m.played
        )
        self.stats_labels['total_goals'].config(text=str(total_goals))
        
        # Moyenne de buts
        played_matches = len(self.tournament.get_played_matches())
        avg_goals = total_goals / played_matches if played_matches > 0 else 0
        self.stats_labels['avg_goals'].config(text=f"{avg_goals:.2f}")
        
        # Meilleurs statistiques
        self.update_top_stats()
    
    def update_top_stats(self):
        """Met à jour le tableau des meilleures équipes"""
        for item in self.top_tree.get_children():
            self.top_tree.delete(item)
        
        if not self.tournament.teams:
            return
        
        # Trier par différentes statistiques
        teams_sorted = self.tournament.get_standings()
        
        stats_to_show = [
            ("Points", lambda t: t.points),
            ("Buts marqués", lambda t: t.goals_for),
            ("Buts encaissés", lambda t: t.goals_against),
            ("Différence", lambda t: t.goal_difference),
            ("Victoires", lambda t: t.won),
        ]
        
        for stat_name, stat_func in stats_to_show:
            # Prendre le top 3
            sorted_by_stat = sorted(teams_sorted, key=stat_func, reverse=True)
            for i, team in enumerate(sorted_by_stat[:3]):
                value = stat_func(team)
                self.top_tree.insert('', 'end', values=(team.name, f"{stat_name} (#{i+1})", str(value)))
    
    # =========================================================================
    # FONCTIONS POUR LA SAUVEGARDE/CHARGEMENT
    # =========================================================================
    
    def save_data(self):
        """Sauvegarde les données dans des fichiers CSV"""
        if TournamentSaver.save_tournament(self.tournament):
            self.status_bar.config(text="Données sauvegardées avec succès!")
            messagebox.showinfo("Succès", "Tournoi sauvegardé dans le dossier 'data/'")
        else:
            self.status_bar.config(text="Erreur lors de la sauvegarde")
            messagebox.showerror("Erreur", "Échec de la sauvegarde")
    
    def load_data(self):
        """Charge les données depuis les fichiers CSV"""
        tournament = TournamentSaver.load_tournament()
        if tournament:
            self.tournament = tournament
            self.refresh_all()
            self.status_bar.config(text="Données chargées avec succès!")
            messagebox.showinfo("Succès", "Tournoi chargé depuis le dossier 'data/'")
        else:
            self.status_bar.config(text="Aucune sauvegarde trouvée")
    
    def new_tournament(self):
        """Crée un nouveau tournoi"""
        name = simpledialog.askstring("Nouveau Tournoi", "Nom du tournoi:")
        if name:
            self.tournament = Tournament(name)
            self.refresh_all()
            self.status_bar.config(text=f"Nouveau tournoi '{name}' créé")
    
    def refresh_all(self):
        """Rafraîchit tous les affichages"""
        self.update_teams_tree()
        self.update_matches_tree()
        self.update_standings_tree()
        self.update_stats()


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    root = tk.Tk()
    app = TournamentApp(root)
    root.mainloop()


if __name__ == "__main__":
    print("Bienvenue dans l'Organisateur de Tournoi de Football!")
    print("L'interface graphique va s'ouvrir...")
    main()
