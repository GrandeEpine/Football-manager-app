#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèle de données pour l'application de tournoi de football
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import random
from colors import Colors


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
    group: Optional[str] = None
    qualified: bool = False
    eliminated: bool = False
    
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
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        self.points = 0
        self.goals_for = 0
        self.goals_against = 0
        self.played = 0
        self.won = 0
        self.draw = 0
        self.lost = 0
        self.qualified = False
        self.eliminated = False


@dataclass
class Match:
    """Représente un match entre deux équipes"""
    team1: str
    team2: str
    score1: Optional[int] = None
    score2: Optional[int] = None
    played: bool = False
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    group: Optional[str] = None
    phase: str = "group"
    round_name: str = ""
    
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
    
    def get_winner(self) -> Optional[str]:
        """Retourne le vainqueur ou None si nul"""
        if not self.is_complete or self.score1 is None or self.score2 is None:
            return None
        if self.score1 > self.score2:
            return self.team1
        elif self.score2 > self.score1:
            return self.team2
        return None


@dataclass
class Group:
    """Représente une poule de tournoi"""
    name: str
    teams: List[str] = field(default_factory=list)
    color: str = ""
    
    def add_team(self, team_name: str):
        if team_name not in self.teams:
            self.teams.append(team_name)
    
    def remove_team(self, team_name: str):
        if team_name in self.teams:
            self.teams.remove(team_name)


class Tournament:
    """Gère le tournoi complet"""
    
    GROUP_COLORS = [Colors.GROUP_A, Colors.GROUP_B, Colors.GROUP_C, Colors.GROUP_D, 
                   Colors.GROUP_E, Colors.GROUP_F, Colors.GROUP_G, Colors.GROUP_H]
    
    def __init__(self, name: str = "Mon Tournoi"):
        self.name = name
        self.teams: Dict[str, Team] = {}
        self.matches: List[Match] = []
        self.groups: List[Group] = []
        self.generated_matches: bool = False
        self.phase: str = "group"
        self.teams_per_group: int = 4
        self.teams_to_qualify: int = 3
        self.knockout_matches: List[Match] = []
    
    def add_team(self, team_name: str, group: Optional[str] = None) -> bool:
        """Ajoute une équipe si elle n'existe pas"""
        if team_name.strip() == "":
            return False
        if team_name not in self.teams:
            self.teams[team_name] = Team(team_name, group=group)
            self.generated_matches = False
            return True
        return False
    
    def remove_team(self, team_name: str) -> bool:
        """Supprime une équipe"""
        if team_name in self.teams:
            self.matches = [m for m in self.matches 
                          if m.team1 != team_name and m.team2 != team_name]
            self.knockout_matches = [m for m in self.knockout_matches
                                   if m.team1 != team_name and m.team2 != team_name]
            
            for group in self.groups:
                group.remove_team(team_name)
            
            del self.teams[team_name]
            self.generated_matches = False
            return True
        return False
    
    def create_groups(self, teams_per_group: int = 4) -> List[Group]:
        """Crée des groupes de N équipes chacun"""
        self.teams_per_group = teams_per_group
        self.groups = []
        
        team_names = list(self.teams.keys())
        random.shuffle(team_names)
        
        for i in range(0, len(team_names), teams_per_group):
            group_teams = team_names[i:i + teams_per_group]
            group_name = chr(65 + len(self.groups))
            group_color = self.GROUP_COLORS[len(self.groups) % len(self.GROUP_COLORS)]
            
            group = Group(name=f"Groupe {group_name}", teams=group_teams, color=group_color)
            self.groups.append(group)
            
            for team_name in group_teams:
                self.teams[team_name].group = group.name
        
        return self.groups
    
    def clear_groups(self):
        """Supprime tous les groupes"""
        self.groups = []
        for team in self.teams.values():
            team.group = None
            team.qualified = False
            team.eliminated = False
    
    def create_empty_groups(self, num_groups: int) -> List[Group]:
        """Crée des groupes vides"""
        self.groups = []
        for i in range(num_groups):
            group_name = chr(65 + i)
            group_color = self.GROUP_COLORS[i % len(self.GROUP_COLORS)]
            group = Group(name=f"Group {group_name}", teams=[], color=group_color)
            self.groups.append(group)
        return self.groups
    
    def assign_team_to_group(self, team_name: str, group_name: Optional[str]):
        """Assigne une équipe à un groupe"""
        if team_name not in self.teams:
            return False
        
        # Remove from previous group
        for group in self.groups:
            if team_name in group.teams:
                group.teams.remove(team_name)
                break
        
        # Add to new group or remove from all groups
        if group_name:
            for group in self.groups:
                if group.name == group_name:
                    if team_name not in group.teams:
                        group.teams.append(team_name)
                    break
            self.teams[team_name].group = group_name
        else:
            self.teams[team_name].group = None
        
        return True
    
    def generate_group_matches(self) -> List[Match]:
        """Génère les matchs pour chaque groupe"""
        if not self.groups:
            return []
        
        self.matches = []
        
        for group in self.groups:
            team_names = group.teams
            for i in range(len(team_names)):
                for j in range(i + 1, len(team_names)):
                    match = Match(
                        team1=team_names[i],
                        team2=team_names[j],
                        group=group.name,
                        phase="group",
                        round_name=f"Phase de groupes - {group.name}"
                    )
                    self.matches.append(match)
        
        self.generated_matches = True
        return self.matches
    
    def advance_from_groups(self, teams_to_qualify: int = 3) -> List[str]:
        """Fait avancer les meilleures équipes de chaque groupe"""
        self.teams_to_qualify = teams_to_qualify
        qualified_teams = []
        
        for team in self.teams.values():
            team.qualified = False
            team.eliminated = False
        
        for group in self.groups:
            group_standings = self.get_group_standings(group.name)
            
            for i, team in enumerate(group_standings):
                if i < teams_to_qualify:
                    team.qualified = True
                    qualified_teams.append(team.name)
                else:
                    team.eliminated = True
        
        return qualified_teams
    
    def generate_knockout_matches(self):
        """Génère les matchs de la phase finale"""
        qualified_teams = [t.name for t in self.teams.values() if t.qualified]
        
        if len(qualified_teams) < 2:
            return []
        
        self.knockout_matches = []
        random.shuffle(qualified_teams)
        
        for i in range(0, len(qualified_teams), 2):
            if i + 1 < len(qualified_teams):
                if len(qualified_teams) == 2:
                    round_name = "Finale"
                elif len(qualified_teams) == 4:
                    round_name = "Demi-finale"
                elif len(qualified_teams) <= 8:
                    round_name = "Quart de finale"
                else:
                    round_name = "Huitième de finale"
                
                match = Match(
                    team1=qualified_teams[i],
                    team2=qualified_teams[i + 1],
                    group=None,
                    phase="knockout",
                    round_name=round_name
                )
                self.knockout_matches.append(match)
        
        return self.knockout_matches
    
    def get_all_matches(self) -> List[Match]:
        """Retourne tous les matchs"""
        return self.matches + self.knockout_matches
    
    def generate_matches(self) -> List[Match]:
        """Génère tous les matchs possibles (mode classique)"""
        team_names = list(self.teams.keys())
        new_matches = []
        self.matches = []
        
        for i in range(len(team_names)):
            for j in range(i + 1, len(team_names)):
                match = Match(team_names[i], team_names[j], phase="group")
                new_matches.append(match)
        
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
        
        is_win_team1 = score1 > score2
        is_draw = score1 == score2
        
        self.teams[match.team1].add_result(score1, score2, is_win_team1, is_draw)
        self.teams[match.team2].add_result(score2, score1, not is_win_team1 and not is_draw, is_draw)
        
        return True
    
    def get_standings(self) -> List[Team]:
        """Retourne le classement trié (toutes équipes)"""
        sorted_teams = sorted(
            self.teams.values(), 
            key=lambda t: (-t.points, -t.goal_difference, -t.goals_for, t.name)
        )
        return sorted_teams
    
    def get_group_standings(self, group_name: str) -> List[Team]:
        """Retourne le classement des équipes d'un groupe"""
        group_teams = [t for t in self.teams.values() if t.group == group_name]
        sorted_teams = sorted(
            group_teams,
            key=lambda t: (-t.points, -t.goal_difference, -t.goals_for, t.name)
        )
        return sorted_teams
    
    def get_group(self, group_name: str) -> Optional[Group]:
        for group in self.groups:
            if group.name == group_name:
                return group
        return None
    
    def get_team(self, name: str) -> Optional[Team]:
        return self.teams.get(name)
    
    def get_unplayed_matches(self) -> List[Match]:
        return [m for m in self.get_all_matches() if not m.played]
    
    def get_played_matches(self) -> List[Match]:
        return [m for m in self.get_all_matches() if m.played]
    
    def get_group_matches(self, group_name: str) -> List[Match]:
        return [m for m in self.matches if m.group == group_name]
    
    def get_knockout_matches_by_round(self, round_name: str) -> List[Match]:
        return [m for m in self.knockout_matches if m.round_name == round_name]
