#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Football Tournament Organizer - Graphical User Interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from model import Tournament, Team, Match, Group
from saver import TournamentSaver
from colors import Colors
from typing import List, Dict, Optional, Tuple
import random


class TournamentApp:
    """Main graphical interface"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.tournament = Tournament()
        self.search_vars: Dict = {}

        self.setup_ui()
        self.load_data()

    # =========================================================================
    # UI SETUP
    # =========================================================================

    def setup_ui(self):
        """Setup user interface"""
        self.root.title("Football Tournament Organizer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=Colors.BG_DARK)

        # Main frame
        main_frame = tk.Frame(self.root, bg=Colors.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Setup tabs
        self.setup_teams_tab()
        self.setup_groups_tab()
        self.setup_matches_tab()
        self.setup_standings_tab()
        self.setup_knockout_tab()
        self.setup_stats_tab()

        # Menu
        self.setup_menu()

        # Status bar
        self.status_bar = tk.Label(
            main_frame, text="Ready", relief=tk.SUNKEN,
            bg=Colors.BG_LIGHT, fg=Colors.FG_TEXT, anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Configure styles
        self.configure_styles()

    def configure_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass

        style.configure('TFrame', background=Colors.BG_DARK)
        style.configure('TLabel', background=Colors.BG_DARK, 
                       foreground=Colors.FG_TEXT, font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('Treeview', font=('Arial', 10), 
                       background=Colors.BG_CARD, foreground=Colors.FG_TEXT, 
                       fieldbackground=Colors.BG_CARD)
        style.configure('Treeview.Heading', font=('Arial', 11, 'bold'), 
                       background=Colors.PRIMARY, foreground=Colors.FG_HEADING)
        style.map('Treeview', background=[('selected', Colors.SELECTED)])
        style.configure('TNotebook', background=Colors.BG_DARK)
        style.configure('TNotebook.Tab', background=Colors.BG_LIGHT, 
                       foreground=Colors.FG_TEXT, font=('Arial', 10))
        style.map('TNotebook.Tab', background=[('selected', Colors.PRIMARY)])

    def get_btn_style(self):
        return {
            'bg': Colors.BTN_BG, 'fg': Colors.BTN_FG, 
            'activebackground': Colors.BTN_HOVER, 'activeforeground': Colors.FG_TEXT,
            'bd': 0, 'relief': tk.FLAT, 'padx': 10, 'pady': 5
        }

    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root, bg=Colors.BG_DARK, fg=Colors.FG_TEXT,
                         activebackground=Colors.BG_LIGHT, 
                         activeforeground=Colors.FG_TEXT)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        file_menu.add_command(label="New Tournament", command=self.new_tournament)
        file_menu.add_command(label="Save", command=self.save_data)
        file_menu.add_command(label="Load", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Team menu
        team_menu = tk.Menu(menubar, tearoff=0, bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        team_menu.add_command(label="Add Team", command=self.add_team_dialog)
        team_menu.add_command(label="Generate Matches", command=self.generate_classic_matches)
        menubar.add_cascade(label="Teams", menu=team_menu)

        # Group menu
        group_menu = tk.Menu(menubar, tearoff=0, bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        group_menu.add_command(label="Create Groups (4)", command=self.create_groups_4)
        group_menu.add_command(label="Manual Groups", command=self.create_groups_manual)
        group_menu.add_command(label="Generate Knockout", command=self.generate_knockout_stage)
        menubar.add_cascade(label="Groups", menu=group_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        view_menu.add_command(label="Refresh", command=self.update_all)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

    def create_search_frame(self, parent_frame, tree, filter_func, placeholder="Search..."):
        """Create search frame"""
        search_frame = tk.Frame(parent_frame, bg=Colors.BG_DARK)
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        search_entry.insert(0, placeholder)
        search_entry.bind('<FocusIn>', 
            lambda e: search_entry.delete(0, 'end') if search_entry.get() == placeholder else None)
        search_entry.bind('<FocusOut>', 
            lambda e: search_entry.insert(0, placeholder) if not search_entry.get() else None)
        search_entry.bind('<KeyRelease>', lambda e: filter_func(search_var.get()))

        tk.Button(
            search_frame, text="\u00d7", 
            command=lambda: (search_var.set(""), filter_func("")),
            bg=Colors.DANGER, fg=Colors.FG_TEXT, bd=0, width=2, 
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)

        self.search_vars[id(tree)] = search_var
        return search_frame

    def configure_treeview_tags(self, tree):
        """Configure treeview tag colors"""
        tree.tag_configure('even', background=Colors.BG_CARD)
        tree.tag_configure('odd', background=Colors.BG_LIGHT)
        tree.tag_configure('win', foreground=Colors.WIN)
        tree.tag_configure('lose', foreground=Colors.LOSE)
        tree.tag_configure('draw', foreground=Colors.DRAW)
        tree.tag_configure('qualified', background=Colors.SUCCESS)
        tree.tag_configure('eliminated', background=Colors.DANGER)

    def get_match_tags(self, match: Match) -> Tuple[str, ...]:
        """Get tags for a match"""
        tags = []
        hash_val = hash(f"{match.team1}{match.team2}")
        tags.append('even' if hash_val % 2 == 0 else 'odd')

        if match.played and match.score1 is not None and match.score2 is not None:
            if match.score1 > match.score2:
                tags.append('win')
            elif match.score1 < match.score2:
                tags.append('lose')
            else:
                tags.append('draw')

        return tuple(tags)

    # =========================================================================
    # TABS SETUP
    # =========================================================================

    def setup_teams_tab(self):
        """Setup Teams tab"""
        frame = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(frame, text="Teams")

        # Buttons
        btn_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Add", command=self.add_team_dialog, 
                 **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove", command=self.remove_selected_team, 
                 **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Rename", command=self.rename_team_dialog, 
                 **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reset Stats", command=self.reset_all_stats, 
                 **self.get_btn_style()).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ('name', 'points', 'played', 'won', 'draw', 'lost', 'gf', 'ga', 'gd', 'group')
        self.teams_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col, title in zip(columns, ['Team', 'Pts', 'Pld', 'W', 'D', 'L', 'F', 'A', 'GD', 'Group']):
            self.teams_tree.heading(col, text=title, anchor=tk.CENTER)
            self.teams_tree.column(col, anchor=tk.CENTER, width=60)
        self.teams_tree.column('name', anchor=tk.W, width=150)
        self.teams_tree.column('group', anchor=tk.W, width=80)
        self.teams_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.configure_treeview_tags(self.teams_tree)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.teams_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teams_tree.configure(yscrollcommand=scrollbar.set)

        # Search
        self.create_search_frame(frame, self.teams_tree, self.filter_teams_tree, "Search team...")

    def setup_groups_tab(self):
        """Setup Groups tab"""
        frame = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(frame, text="Groups")

        btn_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Create Groups (4)", 
                 command=self.create_groups_4, **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Manual Groups", 
                 command=self.create_groups_manual, **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear Groups", 
                 command=self.clear_groups, **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Generate Knockout", 
                 command=self.generate_knockout_stage, **self.get_btn_style()).pack(side=tk.LEFT, padx=5)

        self.groups_container = tk.Frame(frame, bg=Colors.BG_DARK)
        self.groups_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.groups_frames = {}

    def setup_matches_tab(self):
        """Setup Matches tab"""
        frame = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(frame, text="Matches")

        btn_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Generate Matches", 
                 command=self.generate_classic_matches, **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Enter Result", 
                 command=self.enter_result_dialog, **self.get_btn_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove", 
                 command=self.remove_selected_match, **self.get_btn_style()).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ('team1', 'team2', 'score', 'played', 'date', 'result', 'group', 'phase')
        self.matches_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col, title in zip(columns, ['Team 1', 'Team 2', 'Score', 'Played', 'Date', 'Result', 'Group', 'Phase']):
            self.matches_tree.heading(col, text=title, anchor=tk.CENTER)
            self.matches_tree.column(col, anchor=tk.CENTER, width=80)
        self.matches_tree.column('team1', anchor=tk.W, width=120)
        self.matches_tree.column('team2', anchor=tk.W, width=120)
        self.matches_tree.column('date', width=140)
        self.matches_tree.column('result', width=100)
        self.matches_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.configure_treeview_tags(self.matches_tree)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.matches_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.matches_tree.configure(yscrollcommand=scrollbar.set)

        info_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.matches_info = tk.Label(info_frame, text="Matches: 0 played, 0 to play", 
                                    bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        self.matches_info.pack(side=tk.LEFT)

        # Search
        self.create_search_frame(frame, self.matches_tree, self.filter_matches_tree, "Search match...")

    def setup_knockout_tab(self):
        """Setup Knockout tab"""
        frame = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(frame, text="Knockout")

        btn_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Generate", command=self.generate_knockout_stage, 
                 **self.get_btn_style()).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ('team1', 'team2', 'score', 'played', 'date', 'result', 'round')
        self.knockout_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col, title in zip(columns, ['Team 1', 'Team 2', 'Score', 'Played', 'Date', 'Result', 'Round']):
            self.knockout_tree.heading(col, text=title, anchor=tk.CENTER)
            self.knockout_tree.column(col, anchor=tk.CENTER, width=80)
        self.knockout_tree.column('team1', anchor=tk.W, width=120)
        self.knockout_tree.column('team2', anchor=tk.W, width=120)
        self.knockout_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.configure_treeview_tags(self.knockout_tree)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.knockout_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.knockout_tree.configure(yscrollcommand=scrollbar.set)

        info_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.knockout_info = tk.Label(info_frame, text="Qualified: 0", 
                                      bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        self.knockout_info.pack(side=tk.LEFT)

        # Search
        self.create_search_frame(frame, self.knockout_tree, self.filter_knockout_tree, "Search...")

    def setup_standings_tab(self):
        """Setup Standings tab"""
        frame = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(frame, text="Standings")

        btn_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Button(btn_frame, text="Global", 
                 command=lambda: self.update_standings_tree(False), 
                 **self.get_btn_style()).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ('rank', 'team', 'points', 'played', 'won', 'draw', 'lost', 'gf', 'ga', 'gd', 'status')
        self.standings_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col, title in zip(columns, ['Rank', 'Team', 'Pts', 'Pld', 'W', 'D', 'L', 'F', 'A', 'GD', 'Status']):
            self.standings_tree.heading(col, text=title, anchor=tk.CENTER)
            self.standings_tree.column(col, anchor=tk.CENTER, width=60)
        self.standings_tree.column('team', anchor=tk.W, width=150)
        self.standings_tree.column('status', anchor=tk.W, width=100)
        self.standings_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.configure_treeview_tags(self.standings_tree)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.standings_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.standings_tree.configure(yscrollcommand=scrollbar.set)

        # Search
        self.create_search_frame(frame, self.standings_tree, self.filter_standings_tree, "Search...")

    def setup_stats_tab(self):
        """Setup Statistics tab"""
        frame = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(frame, text="Statistics")

        general_stats = tk.LabelFrame(frame, text="General Statistics", padx=20, pady=20,
                                       bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        general_stats.pack(fill=tk.X, padx=10, pady=10)

        self.stats_labels = {}
        stats_texts = [
            ("total_teams", "Teams: "), ("total_matches", "Matches: "),
            ("played_matches", "Played: "), ("unplayed_matches", "To Play: "),
            ("total_goals", "Goals: "), ("avg_goals", "Average: "),
            ("qualified_teams", "Qualified: "), ("eliminated_teams", "Eliminated: ")
        ]

        for key, text in stats_texts:
            row_frame = tk.Frame(general_stats, bg=Colors.BG_DARK)
            row_frame.pack(fill=tk.X, pady=5)
            tk.Label(row_frame, text=text, bg=Colors.BG_DARK, fg=Colors.FG_TEXT, 
                    width=15, anchor=tk.W).pack(side=tk.LEFT)
            self.stats_labels[key] = tk.Label(row_frame, text="0", 
                font=('Arial', 10, 'bold'), bg=Colors.BG_DARK, fg=Colors.PRIMARY)
            self.stats_labels[key].pack(side=tk.LEFT)

        top_frame = tk.LabelFrame(frame, text="Top 3 Teams", padx=20, pady=20, 
                                  bg=Colors.BG_DARK, fg=Colors.FG_TEXT)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.top_tree = ttk.Treeview(top_frame, columns=('team', 'stat', 'value'), show='headings')
        self.top_tree.heading('team', text='Team')
        self.top_tree.heading('stat', text='Statistic')
        self.top_tree.heading('value', text='Value')
        self.top_tree.column('team', width=150)
        self.top_tree.column('stat', width=150)
        self.top_tree.column('value', width=80)
        self.top_tree.pack(fill=tk.BOTH, expand=True)
        self.configure_treeview_tags(self.top_tree)

    # =========================================================================
    # GROUP FUNCTIONS
    # =========================================================================

    def create_groups_4(self):
        """Create groups of 4 teams"""
        if len(self.tournament.teams) < 4:
            messagebox.showwarning("Warning", "You need at least 4 teams!")
            return
        self.tournament.clear_groups()
        self.tournament.create_groups(4)
        self.tournament.generate_group_matches()
        self.setup_groups_display()
        self.update_all()
        self.status_bar.config(text=f"{len(self.tournament.groups)} groups created")

    def clear_groups(self):
        """Clear groups"""
        self.tournament.clear_groups()
        self.tournament.phase = "group"
        self.setup_groups_display()
        self.update_all()
        self.status_bar.config(text="Groups cleared")

    def setup_groups_display(self):
        """Display groups"""
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        self.groups_frames = {}

        if not self.tournament.groups:
            tk.Label(self.groups_container, 
                    text="No groups. Use 'Create Groups (4)' or 'Manual Groups' first",
                    bg=Colors.BG_DARK, fg=Colors.FG_TEXT, 
                    font=('Arial', 12)).pack(pady=40)
            return

        for group in self.tournament.groups:
            group_frame = tk.LabelFrame(self.groups_container, text=group.name, 
                                        bg=Colors.BG_DARK, fg=group.color, 
                                        font=('Arial', 12, 'bold'), padx=10, pady=10)
            group_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
            self.groups_frames[group.name] = group_frame

            for team_name in group.teams:
                team = self.tournament.get_team(team_name)
                if team:
                    status = "\u2713" if team.qualified else ("\u2717" if team.eliminated else "")
                    tk.Label(
                        group_frame,
                        text=f"{status} {team.name} - {team.points} pts",
                        bg=Colors.BG_CARD, fg=Colors.FG_TEXT, anchor=tk.W,
                    ).pack(fill=tk.X, pady=2)

            if group.teams:
                tk.Button(
                    group_frame, text="Matches",
                    command=lambda g=group.name: self.show_group_matches(g),
                    bg=Colors.PRIMARY, fg=Colors.FG_TEXT, bd=0, relief=tk.FLAT,
                ).pack(pady=5)

    def show_group_matches(self, group_name: str):
        """Show matches for a specific group"""
        group_matches = [m for m in self.tournament.matches if m.group == group_name]
        if not group_matches:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Matches - {group_name}")
        dialog.geometry("600x400")
        dialog.configure(bg=Colors.BG_DARK)

        frame = tk.Frame(dialog, bg=Colors.BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('team1', 'team2', 'score', 'played', 'result')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col, title in zip(columns, ['Team 1', 'Team 2', 'Score', 'Played', 'Result']):
            tree.heading(col, text=title)
            tree.column(col, anchor=tk.CENTER, width=100)
        tree.column('team1', anchor=tk.W, width=150)
        tree.column('team2', anchor=tk.W, width=150)

        for match in sorted(group_matches, key=lambda m: (not m.played, m.date)):
            score = f"{match.score1}-{match.score2}" if match.is_complete else "-"
            played = "Yes" if match.played else "No"
            result = match.get_result() or "To be played"
            tree.insert('', 'end', values=(match.team1, match.team2, score, played, result))

        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

    def generate_knockout_stage(self):
        """Generate knockout stage"""
        if not self.tournament.groups:
            messagebox.showwarning("Warning", "Create groups first!")
            return

        unplayed = [m for m in self.tournament.matches if not m.played]
        if unplayed:
            confirm = messagebox.askyesno(
                "Warning", f"There are {len(unplayed)} unplayed matches. Continue?"
            )
            if not confirm:
                return

        self.tournament.advance_from_groups(self.tournament.teams_to_qualify)
        self.tournament.generate_knockout_matches()
        self.tournament.phase = "knockout"

        self.update_all()
        self.setup_groups_display()
        self.status_bar.config(text="Knockout stage generated")

    def create_groups_manual(self):
        """Create groups manually with custom team selection"""
        if len(self.tournament.teams) < 4:
            messagebox.showwarning("Warning", "You need at least 4 teams!")
            return

        num_groups = simpledialog.askinteger(
            "Manual Groups", "Number of groups:",
            minvalue=2, maxvalue=8, initialvalue=2
        )
        if not num_groups:
            return

        # Create empty groups
        self.tournament.clear_groups()
        self.tournament.create_empty_groups(num_groups)

        # Show composition window
        self.show_group_composition_window()

    # =========================================================================
    # NEW: IMPROVED GROUP COMPOSITION WINDOW
    # =========================================================================

    def show_group_composition_window(self):
        """Show improved window to manually assign teams to groups using checkboxes"""
        if not self.tournament.groups:
            messagebox.showwarning("Warning", "Create groups first!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Group Composition - Toggle Teams")
        dialog.geometry("800x600")
        dialog.configure(bg=Colors.BG_DARK)
        dialog.transient(self.root)
        dialog.grab_set()

        # Main frame
        main_frame = tk.Frame(dialog, bg=Colors.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        tk.Label(
            main_frame,
            text="Assign Teams to Groups (Drag & Drop style)",
            font=("Arial", 14, "bold"),
            bg=Colors.BG_DARK,
            fg=Colors.FG_TEXT,
        ).pack(pady=(0, 15))

        # Create a frame for group selection and team display
        content_frame = tk.Frame(main_frame, bg=Colors.BG_DARK)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel: Groups list
        groups_frame = tk.LabelFrame(
            content_frame, text="Groups",
            bg=Colors.BG_DARK, fg=Colors.FG_TEXT,
            padx=10, pady=10
        )
        groups_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right panel: Teams with checkboxes
        teams_frame = tk.LabelFrame(
            content_frame, text="Teams - Select Group",
            bg=Colors.BG_DARK, fg=Colors.FG_TEXT,
            padx=10, pady=10
        )
        teams_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create group buttons
        group_vars = {}
        for group in self.tournament.groups:
            var = tk.BooleanVar(value=False)
            group_vars[group.name] = var
            cb = tk.Checkbutton(
                groups_frame,
                text=group.name,
                variable=var,
                bg=Colors.BG_DARK,
                fg=group.color,
                selectcolor=Colors.BG_DARK,
                anchor=tk.W,
                command=lambda g=group.name: self._toggle_group_selection(g, group_vars)
            )
            cb.pack(fill=tk.X, pady=5, padx=5)

        # Current selected group (for keyboard shortcut)
        self.current_selected_group = tk.StringVar()

        # Create scrollable team list
        canvas = tk.Canvas(teams_frame, bg=Colors.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(teams_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_DARK)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create team selection widgets
        team_widgets = {}
        sorted_teams = sorted(self.tournament.teams.keys())

        for team_name in sorted_teams:
            team = self.tournament.teams[team_name]
            current_group = team.group if team.group else "None"

            team_frame = tk.Frame(scrollable_frame, bg=Colors.BG_CARD, pady=2)
            team_frame.pack(fill=tk.X, pady=1)

            # Team name
            tk.Label(
                team_frame,
                text=team_name,
                width=20,
                anchor=tk.W,
                bg=Colors.BG_CARD,
                fg=Colors.FG_TEXT,
            ).pack(side=tk.LEFT, padx=5)

            # Group assignment dropdown
            var = tk.StringVar(value=current_group)
            group_options = ["None"] + [g.name for g in self.tournament.groups]

            combo = ttk.Combobox(
                team_frame,
                textvariable=var,
                values=group_options,
                width=12,
                state="readonly",
            )
            combo.pack(side=tk.LEFT, padx=5)

            # Store reference
            team_widgets[team_name] = {'var': var, 'frame': team_frame}

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, pady=15)

        def apply_groups():
            """Apply group assignments"""
            # Count teams per group
            group_counts = {g.name: 0 for g in self.tournament.groups}
            unassigned = []

            for team_name, widget in team_widgets.items():
                group_name = widget['var'].get()
                if group_name == "None":
                    unassigned.append(team_name)
                else:
                    group_counts[group_name] = group_counts.get(group_name, 0) + 1

            # Check limits
            max_per_group = 4
            for group_name, count in group_counts.items():
                if count > max_per_group:
                    messagebox.showwarning(
                        "Warning",
                        f"Group {group_name} has {count} teams. Maximum is {max_per_group} per group!"
                    )
                    return

            # Check if all teams are assigned
            if unassigned:
                confirm = messagebox.askyesno(
                    "Unassigned Teams",
                    f"{len(unassigned)} teams are not assigned to any group. Continue?"
                )
                if not confirm:
                    return

            # Apply assignments
            for team_name, widget in team_widgets.items():
                group_name = widget['var'].get()
                self.tournament.assign_team_to_group(team_name, group_name if group_name != "None" else None)

            # Generate matches
            self.tournament.generate_group_matches()

            self.update_all()
            self.setup_groups_display()
            dialog.destroy()
            self.status_bar.config(text="Groups updated successfully")

        def random_distribution():
            """Distribute teams randomly"""
            team_names = list(sorted_teams)
            random.shuffle(team_names)

            for i, team_name in enumerate(team_names):
                group_index = i % len(self.tournament.groups)
                group_name = self.tournament.groups[group_index].name
                team_widgets[team_name]['var'].set(group_name)

        def clear_all():
            """Clear all assignments"""
            for team_name in sorted_teams:
                team_widgets[team_name]['var'].set("None")

        def auto_balance():
            """Auto-balance teams across groups"""
            team_names = list(sorted_teams)
            random.shuffle(team_names)

            groups = self.tournament.groups
            for i, team_name in enumerate(team_names):
                group = groups[i % len(groups)]
                team_widgets[team_name]['var'].set(group.name)

        tk.Button(
            btn_frame, text="Apply", command=apply_groups, **self.get_btn_style()
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Random",
            command=random_distribution,
            **self.get_btn_style()
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Auto-Balance",
            command=auto_balance,
            **self.get_btn_style()
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Clear",
            command=clear_all,
            bg=Colors.DANGER, fg=Colors.FG_TEXT,
            bd=0, relief=tk.FLAT, padx=10, pady=5,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=Colors.BG_LIGHT, fg=Colors.FG_TEXT,
            bd=0, relief=tk.FLAT, padx=10, pady=5,
        ).pack(side=tk.RIGHT, padx=10)

        dialog.resizable(True, True)

    def _toggle_group_selection(self, group_name: str, group_vars: Dict):
        """Toggle group selection"""
        # This can be used for future drag & drop functionality
        pass

    # =========================================================================
    # TEAM FUNCTIONS
    # =========================================================================

    def add_team_dialog(self, chain_add=True):
        """Add a team. If chain_add=True, keeps asking for more teams."""
        team_name = simpledialog.askstring("Add Team", "Team name:")
        if team_name and team_name.strip():
            team_name = team_name.strip()
            if self.tournament.add_team(team_name):
                self.update_all()
                self.setup_groups_display()
                self.status_bar.config(text=f"Team '{team_name}' added")
                # Chain add: open dialog again for next team
                if chain_add:
                    self.add_team_dialog(chain_add=True)
            else:
                messagebox.showerror("Error", f"Team already exists!")
                # Continue chaining even if duplicate
                if chain_add:
                    self.add_team_dialog(chain_add=True)

    def remove_selected_team(self):
        """Remove a team"""
        selected = self.teams_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No team selected!")
            return

        team_name = self.teams_tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm", f"Remove '{team_name}'?")
        if confirm:
            if self.tournament.remove_team(team_name):
                self.update_all()
                self.setup_groups_display()
                self.status_bar.config(text="Team removed")

    def rename_team_dialog(self):
        """Rename a team"""
        selected = self.teams_tree.selection()
        if not selected:
            return

        old_name = self.teams_tree.item(selected[0])["values"][0]
        new_name = simpledialog.askstring("Rename", f"New name for '{old_name}':")
        if new_name and new_name.strip() and new_name != old_name:
            new_name = new_name.strip()
            if new_name in self.tournament.teams:
                messagebox.showerror("Error", f"'{new_name}' already exists!")
                return

            old_team = self.tournament.teams[old_name]
            new_team = Team(
                name=new_name,
                points=old_team.points,
                goals_for=old_team.goals_for,
                goals_against=old_team.goals_against,
                played=old_team.played,
                won=old_team.won,
                draw=old_team.draw,
                lost=old_team.lost,
                group=old_team.group,
                qualified=old_team.qualified,
                eliminated=old_team.eliminated,
            )
            self.tournament.teams[new_name] = new_team

            for match in self.tournament.matches + self.tournament.knockout_matches:
                if match.team1 == old_name:
                    match.team1 = new_name
                if match.team2 == old_name:
                    match.team2 = new_name

            for group in self.tournament.groups:
                if old_name in group.teams:
                    index = group.teams.index(old_name)
                    group.teams[index] = new_name

            del self.tournament.teams[old_name]
            self.update_all()
            self.setup_groups_display()
            self.status_bar.config(text="Team renamed")

    def reset_all_stats(self):
        """Reset all statistics"""
        if messagebox.askyesno("Confirm", "Reset ALL statistics?"):
            for team in self.tournament.teams.values():
                team.reset_stats()
            for match in self.tournament.matches + self.tournament.knockout_matches:
                match.score1 = None
                match.score2 = None
                match.played = False
            self.tournament.clear_groups()
            self.tournament.knockout_matches = []
            self.tournament.phase = "group"
            self.update_all()
            self.setup_groups_display()
            self.status_bar.config(text="Statistics reset")

    # =========================================================================
    # MATCH FUNCTIONS
    # =========================================================================

    def generate_classic_matches(self):
        """Generate classic matches (no groups)"""
        self.tournament.clear_groups()
        self.tournament.phase = "group"
        self.tournament.generate_matches()
        self.update_all()
        self.setup_groups_display()
        self.status_bar.config(text=f"{len(self.tournament.matches)} matches generated")

    def enter_result_dialog(self):
        """Enter match result"""
        all_matches = self.tournament.get_all_matches()
        unplayed = [m for m in all_matches if not m.played]

        selected = self.matches_tree.selection() or self.knockout_tree.selection()
        match = None

        if selected:
            tree = (
                self.matches_tree
                if self.matches_tree.selection()
                else self.knockout_tree
            )
            values = tree.item(selected[0])["values"]
            for m in all_matches:
                if (m.team1 == values[0] and m.team2 == values[1]) or (
                    m.team1 == values[1] and m.team2 == values[0]
                ):
                    match = m
                    break
        elif unplayed:
            match = unplayed[0]
        else:
            messagebox.showinfo("Info", "All matches have been played!")
            return

        if not match:
            return

        if match.played:
            if not messagebox.askyesno("Modify", "Modify this result?"):
                return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Result: {match.team1} vs {match.team2}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=Colors.BG_DARK)

        frame = tk.Frame(dialog, bg=Colors.BG_DARK, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text=f"{match.team1} vs {match.team2}",
            font=("Arial", 12, "bold"),
            bg=Colors.BG_DARK,
            fg=Colors.FG_TEXT,
        ).grid(row=0, column=0, columnspan=2, pady=10)

        if match.group:
            tk.Label(
                frame,
                text=f"Group: {match.group}",
                bg=Colors.BG_DARK,
                fg=Colors.FG_TEXT,
            ).grid(row=1, column=0, columnspan=2)
        if match.round_name:
            tk.Label(
                frame,
                text=f"Round: {match.round_name}",
                bg=Colors.BG_DARK,
                fg=Colors.FG_TEXT,
            ).grid(row=2, column=0, columnspan=2)

        tk.Label(
            frame, text=f"{match.team1}:", bg=Colors.BG_DARK, fg=Colors.FG_TEXT
        ).grid(row=3, column=0, sticky=tk.E, pady=5)
        score1_var = tk.StringVar(
            value=str(match.score1) if match.score1 is not None else "0"
        )
        ttk.Entry(frame, textvariable=score1_var, width=5).grid(
            row=3, column=1, sticky=tk.W, pady=5
        )

        tk.Label(
            frame, text=f"{match.team2}:", bg=Colors.BG_DARK, fg=Colors.FG_TEXT
        ).grid(row=4, column=0, sticky=tk.E, pady=5)
        score2_var = tk.StringVar(
            value=str(match.score2) if match.score2 is not None else "0"
        )
        ttk.Entry(frame, textvariable=score2_var, width=5).grid(
            row=4, column=1, sticky=tk.W, pady=5
        )

        button_frame = tk.Frame(frame, bg=Colors.BG_DARK)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)

        def save_result():
            try:
                score1 = int(score1_var.get())
                score2 = int(score2_var.get())
                if score1 < 0 or score2 < 0:
                    messagebox.showerror("Error", "Positive scores only!")
                    return

                if (
                    match.played
                    and match.score1 is not None
                    and match.score2 is not None
                ):
                    self.tournament.record_match_result(
                        match, -match.score1, -match.score2
                    )

                self.tournament.record_match_result(match, score1, score2)
                self.update_all()
                self.setup_groups_display()
                self.status_bar.config(text="Result saved")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers!")

        tk.Button(
            button_frame, text="Save", command=save_result, **self.get_btn_style()
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=Colors.DANGER, fg=Colors.FG_TEXT,
            bd=0, relief=tk.FLAT, padx=10, pady=5,
        ).pack(side=tk.LEFT, padx=10)

        dialog.resizable(False, False)

    def remove_selected_match(self):
        """Remove a match"""
        selected = self.matches_tree.selection() or self.knockout_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No match selected!")
            return

        tree = (
            self.matches_tree if self.matches_tree.selection() else self.knockout_tree
        )
        values = tree.item(selected[0])["values"]

        all_matches = self.tournament.matches + self.tournament.knockout_matches
        match_to_remove = None
        match_list = None

        for m in all_matches:
            if (m.team1 == values[0] and m.team2 == values[1]) or (
                m.team1 == values[1] and m.team2 == values[0]
            ):
                match_to_remove = m
                match_list = (
                    self.tournament.matches
                    if m in self.tournament.matches
                    else self.tournament.knockout_matches
                )
                break

        if (
            match_to_remove
            and messagebox.askyesno("Confirm", "Remove this match?")
            and match_list is not None
        ):
            if (
                match_to_remove.played
                and match_to_remove.score1 is not None
                and match_to_remove.score2 is not None
            ):
                self.tournament.record_match_result(
                    match_to_remove, -match_to_remove.score1, -match_to_remove.score2
                )
            match_list.remove(match_to_remove)
            self.update_all()
            self.status_bar.config(text="Match removed")

    # =========================================================================
    # FILTER FUNCTIONS
    # =========================================================================

    def filter_teams_tree(self, search_term: str):
        """Filter teams"""
        for item in self.teams_tree.get_children():
            self.teams_tree.delete(item)
        if search_term == "Search team..." or not search_term.strip():
            self.update_teams_tree()
            return
        search_term = search_term.lower()
        for team in sorted(self.tournament.teams.values(), key=lambda t: t.name):
            if search_term in team.name.lower():
                tags = (
                    ("qualified",)
                    if team.qualified
                    else (("eliminated",) if team.eliminated else ("even",) if hash(team.name) % 2 == 0 else ("odd",))
                )
                self.teams_tree.insert(
                    "",
                    "end",
                    values=(
                        team.name,
                        team.points,
                        team.played,
                        team.won,
                        team.draw,
                        team.lost,
                        team.goals_for,
                        team.goals_against,
                        team.goal_difference,
                        team.group or "",
                    ),
                    tags=tags,
                )

    def filter_matches_tree(self, search_term: str):
        """Filter matches"""
        for item in self.matches_tree.get_children():
            self.matches_tree.delete(item)
        if search_term == "Search match..." or not search_term.strip():
            self.update_matches_tree()
            return
        search_term = search_term.lower()
        for match in sorted(
            self.tournament.get_all_matches(), key=lambda m: (not m.played, m.date)
        ):
            if search_term in f"{match.team1} {match.team2} {match.group}".lower():
                score = f"{match.score1}-{match.score2}" if match.is_complete else "-"
                self.matches_tree.insert(
                    "",
                    "end",
                    values=(
                        match.team1,
                        match.team2,
                        score,
                        "Yes" if match.played else "No",
                        match.date,
                        match.get_result() or "To be played",
                        match.group or "",
                        match.phase,
                    ),
                    tags=self.get_match_tags(match),
                )

    def filter_knockout_tree(self, search_term: str):
        """Filter knockout matches"""
        for item in self.knockout_tree.get_children():
            self.knockout_tree.delete(item)
        if search_term == "Search..." or not search_term.strip():
            self.update_knockout_tree()
            return
        search_term = search_term.lower()
        for match in sorted(
            self.tournament.knockout_matches, key=lambda m: (not m.played, m.date)
        ):
            if search_term in f"{match.team1} {match.team2} {match.round_name}".lower():
                score = f"{match.score1}-{match.score2}" if match.is_complete else "-"
                self.knockout_tree.insert(
                    "",
                    "end",
                    values=(
                        match.team1,
                        match.team2,
                        score,
                        "Yes" if match.played else "No",
                        match.date,
                        match.get_result() or "To be played",
                        match.round_name,
                    ),
                    tags=self.get_match_tags(match),
                )

    def filter_standings_tree(self, search_term: str):
        """Filter standings"""
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)
        if search_term == "Search..." or not search_term.strip():
            self.update_standings_tree()
            return
        search_term = search_term.lower()
        show_groups = self.tournament.groups and True
        if show_groups:
            for group in sorted(self.tournament.groups, key=lambda g: g.name):
                for rank, team in enumerate(
                    self.tournament.get_group_standings(group.name), 1
                ):
                    if search_term in team.name.lower():
                        status = (
                            "\u2713 Qualified"
                            if team.qualified
                            else ("\u2717 Eliminated" if team.eliminated else "")
                        )
                        tags = (
                            ("qualified",)
                            if team.qualified
                            else (
                                ("eliminated",)
                                if team.eliminated
                                else ("even",) if hash(team.name) % 2 == 0 else ("odd",)
                            )
                        )
                        self.standings_tree.insert(
                            "",
                            "end",
                            values=(
                                f"{group.name} {rank}",
                                team.name,
                                team.points,
                                team.played,
                                team.won,
                                team.draw,
                                team.lost,
                                team.goals_for,
                                team.goals_against,
                                team.goal_difference,
                                status,
                            ),
                            tags=tags,
                        )
        else:
            for rank, team in enumerate(self.tournament.get_standings(), 1):
                if search_term in team.name.lower():
                    status = "\u2713" if team.qualified else ("\u2717" if team.eliminated else "")
                    tags = (
                        ("qualified",)
                        if team.qualified
                        else (
                            ("eliminated",)
                            if team.eliminated
                            else ("even",) if hash(team.name) % 2 == 0 else ("odd",)
                        )
                    )
                    self.standings_tree.insert(
                        "",
                        "end",
                        values=(
                            rank,
                            team.name,
                            team.points,
                            team.played,
                            team.won,
                            team.draw,
                            team.lost,
                            team.goals_for,
                            team.goals_against,
                            team.goal_difference,
                            status,
                        ),
                        tags=tags,
                    )

    # =========================================================================
    # UPDATE FUNCTIONS
    # =========================================================================

    def update_teams_tree(self):
        """Update teams display"""
        for item in self.teams_tree.get_children():
            self.teams_tree.delete(item)
        for team in sorted(self.tournament.teams.values(), key=lambda t: t.name):
            tags = (
                ("qualified",)
                if team.qualified
                else (("eliminated",) if team.eliminated else ("even",) if hash(team.name) % 2 == 0 else ("odd",))
            )
            self.teams_tree.insert(
                "",
                "end",
                values=(
                    team.name,
                    team.points,
                    team.played,
                    team.won,
                    team.draw,
                    team.lost,
                    team.goals_for,
                    team.goals_against,
                    team.goal_difference,
                    team.group or "",
                ),
                tags=tags,
            )

    def update_matches_tree(self):
        """Update matches display"""
        for item in self.matches_tree.get_children():
            self.matches_tree.delete(item)
        for match in sorted(
            self.tournament.get_all_matches(),
            key=lambda m: (m.phase != "group", not m.played, m.date),
        ):
            score = f"{match.score1}-{match.score2}" if match.is_complete else "-"
            self.matches_tree.insert(
                "",
                "end",
                values=(
                    match.team1,
                    match.team2,
                    score,
                    "Yes" if match.played else "No",
                    match.date,
                    match.get_result() or "To be played",
                    match.group or "",
                    match.phase,
                ),
                tags=self.get_match_tags(match),
            )
        unplayed = len(self.tournament.get_unplayed_matches())
        played = len(self.tournament.get_played_matches())
        self.matches_info.config(
            text=f"Matches: {played} played, {unplayed} to play",
            bg=Colors.BG_DARK,
            fg=Colors.FG_TEXT,
        )

    def update_knockout_tree(self):
        """Update knockout matches display"""
        for item in self.knockout_tree.get_children():
            self.knockout_tree.delete(item)
        for match in sorted(
            self.tournament.knockout_matches, key=lambda m: (not m.played, m.date)
        ):
            score = f"{match.score1}-{match.score2}" if match.is_complete else "-"
            self.knockout_tree.insert(
                "",
                "end",
                values=(
                    match.team1,
                    match.team2,
                    score,
                    "Yes" if match.played else "No",
                    match.date,
                    match.get_result() or "To be played",
                    match.round_name,
                ),
                tags=self.get_match_tags(match),
            )
        qualified = len([t for t in self.tournament.teams.values() if t.qualified])
        self.knockout_info.config(
            text=f"Qualified: {qualified}", bg=Colors.BG_DARK, fg=Colors.FG_TEXT
        )

    def update_standings_tree(self, show_groups: bool = True):
        """Update standings display"""
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)
        if show_groups and self.tournament.groups:
            for group in sorted(self.tournament.groups, key=lambda g: g.name):
                for rank, team in enumerate(
                    self.tournament.get_group_standings(group.name), 1
                ):
                    status = (
                        "\u2713 Qualified"
                        if team.qualified
                        else ("\u2717 Eliminated" if team.eliminated else "")
                    )
                    tags = (
                        ("qualified",)
                        if team.qualified
                        else (
                            ("eliminated",)
                            if team.eliminated
                            else ("even",) if hash(team.name) % 2 == 0 else ("odd",)
                        )
                    )
                    self.standings_tree.insert(
                        "",
                        "end",
                        values=(
                            f"{group.name} {rank}",
                            team.name,
                            team.points,
                            team.played,
                            team.won,
                            team.draw,
                            team.lost,
                            team.goals_for,
                            team.goals_against,
                            team.goal_difference,
                            status,
                        ),
                        tags=tags,
                    )
        else:
            for rank, team in enumerate(self.tournament.get_standings(), 1):
                status = "\u2713" if team.qualified else ("\u2717" if team.eliminated else "")
                tags = (
                    ("qualified",)
                    if team.qualified
                    else (
                        ("eliminated",)
                        if team.eliminated
                        else ("even",) if hash(team.name) % 2 == 0 else ("odd",)
                    )
                )
                self.standings_tree.insert(
                    "",
                    "end",
                    values=(
                        rank,
                        team.name,
                        team.points,
                        team.played,
                        team.won,
                        team.draw,
                        team.lost,
                        team.goals_for,
                        team.goals_against,
                        team.goal_difference,
                        status,
                    ),
                    tags=tags,
                )

    def update_stats(self):
        """Update statistics"""
        self.stats_labels['total_teams'].config(text=str(len(self.tournament.teams)))
        self.stats_labels['total_matches'].config(
            text=str(len(self.tournament.get_all_matches()))
        )
        self.stats_labels['played_matches'].config(
            text=str(len(self.tournament.get_played_matches()))
        )
        self.stats_labels['unplayed_matches'].config(
            text=str(len(self.tournament.get_unplayed_matches()))
        )

        total_goals = sum(
            (m.score1 or 0) + (m.score2 or 0)
            for m in self.tournament.get_all_matches()
            if m.played
        )
        self.stats_labels['total_goals'].config(text=str(total_goals))

        played = len(self.tournament.get_played_matches())
        avg = total_goals / played if played > 0 else 0
        self.stats_labels['avg_goals'].config(text=f"{avg:.2f}")

        qualified = len([t for t in self.tournament.teams.values() if t.qualified])
        eliminated = len([t for t in self.tournament.teams.values() if t.eliminated])
        self.stats_labels['qualified_teams'].config(text=str(qualified))
        self.stats_labels['eliminated_teams'].config(text=str(eliminated))

        # Top 3
        for item in self.top_tree.get_children():
            self.top_tree.delete(item)

        teams_sorted = self.tournament.get_standings()
        stats = [("Points", lambda t: t.points), ("Goals", lambda t: t.goals_for), 
                ("Goal Diff", lambda t: t.goal_difference), ("Wins", lambda t: t.won)]

        for stat_name, stat_func in stats:
            sorted_teams = sorted(teams_sorted, key=stat_func, reverse=True)
            for i, team in enumerate(sorted_teams[:3]):
                self.top_tree.insert(
                    "",
                    "end",
                    values=(team.name, f"{stat_name} #{i+1}", str(stat_func(team))),
                    tags=("even",) if hash(team.name) % 2 == 0 else ("odd",),
                )

    def update_all(self):
        """Update all displays"""
        self.update_teams_tree()
        self.update_matches_tree()
        self.update_knockout_tree()
        self.update_standings_tree()
        self.update_stats()

    # =========================================================================
    # SAVE/LOAD FUNCTIONS
    # =========================================================================

    def save_data(self):
        """Save data"""
        if TournamentSaver.save_tournament(self.tournament):
            self.status_bar.config(text="Data saved")
            messagebox.showinfo("Success", "Saved to 'data/'")
        else:
            self.status_bar.config(text="Save error")

    def load_data(self):
        """Load data"""
        tournament = TournamentSaver.load_tournament()
        if tournament:
            self.tournament = tournament
            self.update_all()
            self.setup_groups_display()
            self.status_bar.config(text="Data loaded")
            messagebox.showinfo("Success", "Loaded from 'data/'")

    def new_tournament(self):
        """Create new tournament"""
        name = simpledialog.askstring("New Tournament", "Name:")
        if name:
            self.tournament = Tournament(name)
            self.update_all()
            self.setup_groups_display()
            self.status_bar.config(text=f"New tournament: {name}")


def main():
    root = tk.Tk()
    app = TournamentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
