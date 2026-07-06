#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestion de la sauvegarde et du chargement des tournois
"""

import csv
import os
from typing import Optional
from model import Tournament, Team, Match, Group


class TournamentSaver:
    """Gère la sauvegarde et le chargement depuis CSV"""
    
    DATA_DIR = "data"
    TEAMS_FILE = os.path.join(DATA_DIR, "teams.csv")
    MATCHES_FILE = os.path.join(DATA_DIR, "matches.csv")
    TOURNAMENT_FILE = os.path.join(DATA_DIR, "tournament.csv")
    GROUPS_FILE = os.path.join(DATA_DIR, "groups.csv")
    KNOCKOUT_FILE = os.path.join(DATA_DIR, "knockout_matches.csv")
    
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
                writer.writerow(['name', 'team_count', 'match_count', 'generated', 'phase', 
                                'teams_per_group', 'teams_to_qualify'])
                writer.writerow([
                    tournament.name,
                    len(tournament.teams),
                    len(tournament.matches) + len(tournament.knockout_matches),
                    tournament.generated_matches,
                    tournament.phase,
                    tournament.teams_per_group,
                    tournament.teams_to_qualify
                ])
            
            # Sauvegarder les équipes
            with open(TournamentSaver.TEAMS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'points', 'goals_for', 'goals_against', 
                                'played', 'won', 'draw', 'lost', 'group', 'qualified', 'eliminated'])
                for team in tournament.teams.values():
                    writer.writerow([
                        team.name, team.points, team.goals_for, team.goals_against,
                        team.played, team.won, team.draw, team.lost,
                        team.group if team.group else '',
                        team.qualified,
                        team.eliminated
                    ])
            
            # Sauvegarder les matchs (groupes)
            with open(TournamentSaver.MATCHES_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['team1', 'team2', 'score1', 'score2', 'played', 'date', 
                                'group', 'phase', 'round_name'])
                for match in tournament.matches:
                    writer.writerow([
                        match.team1, match.team2,
                        match.score1 if match.score1 is not None else '',
                        match.score2 if match.score2 is not None else '',
                        match.played, match.date,
                        match.group if match.group else '',
                        match.phase,
                        match.round_name if match.round_name else ''
                    ])
            
            # Sauvegarder les matchs knockout
            with open(TournamentSaver.KNOCKOUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['team1', 'team2', 'score1', 'score2', 'played', 'date', 
                                'phase', 'round_name'])
                for match in tournament.knockout_matches:
                    writer.writerow([
                        match.team1, match.team2,
                        match.score1 if match.score1 is not None else '',
                        match.score2 if match.score2 is not None else '',
                        match.played, match.date,
                        match.phase,
                        match.round_name if match.round_name else ''
                    ])
            
            # Sauvegarder les groupes
            with open(TournamentSaver.GROUPS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'teams', 'color'])
                for group in tournament.groups:
                    writer.writerow([
                        group.name,
                        ';'.join(group.teams),
                        group.color
                    ])
            
            return True
        except Exception as e:
            print(f"Save error: {e}")
            import traceback
            traceback.print_exc()
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
            
            tournament = Tournament()
            
            # Charger les info du tournoi
            with open(TournamentSaver.TOURNAMENT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) >= 2:
                    row = rows[1]
                    if len(row) > 0:
                        tournament.name = row[0]
                    if len(row) > 3:
                        tournament.generated_matches = row[3].lower() == 'true'
                    if len(row) > 4:
                        tournament.phase = row[4]
                    if len(row) > 5:
                        tournament.teams_per_group = int(row[5]) if row[5] else 4
                    if len(row) > 6:
                        tournament.teams_to_qualify = int(row[6]) if row[6] else 4
            
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
                            lost=int(row[7]) if row[7] else 0,
                            group=row[8] if len(row) > 8 and row[8] else None,
                            qualified=row[9].lower() == 'true' if len(row) > 9 and row[9] else False,
                            eliminated=row[10].lower() == 'true' if len(row) > 10 and row[10] else False
                        )
                        tournament.teams[team.name] = team
            
            # Charger les matchs (groupes)
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
                            date=row[5],
                            group=row[6] if len(row) > 6 and row[6] else None,
                            phase=row[7] if len(row) > 7 and row[7] else "group",
                            round_name=row[8] if len(row) > 8 and row[8] else ""
                        )
                        tournament.matches.append(match)
            
            # Charger les matchs knockout
            if os.path.exists(TournamentSaver.KNOCKOUT_FILE):
                with open(TournamentSaver.KNOCKOUT_FILE, 'r', encoding='utf-8') as f:
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
                                date=row[5],
                                phase=row[6] if len(row) > 6 and row[6] else "knockout",
                                round_name=row[7] if len(row) > 7 and row[7] else ""
                            )
                            tournament.knockout_matches.append(match)
            
            # Charger les groupes
            if os.path.exists(TournamentSaver.GROUPS_FILE):
                with open(TournamentSaver.GROUPS_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    for row in reader:
                        if len(row) >= 2:
                            group = Group(
                                name=row[0],
                                teams=row[1].split(';') if row[1] else [],
                                color=row[2] if len(row) > 2 and row[2] else ""
                            )
                            tournament.groups.append(group)
            
            return tournament
            
        except Exception as e:
            print(f"Load error: {e}")
            import traceback
            traceback.print_exc()
            return None
