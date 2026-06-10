# Football Tournament Organizer

A desktop application to manage football tournaments with groups and knockout stages.
## Author
- GrandeEpine (https://github.com/GrandeEpine)
- I was a member of the organisation for Daiko futsall tournament in June 2026, enjoy my work ! (ofc its vibe coded)

## Features

### Teams
- Add, remove, rename teams
- Reset statistics
- View points, matches, goals, wins/draws/losses

### Groups
- Create groups with custom team composition
- Automatic group matches generation (round-robin)
- Manual team assignment via selection window
- Visual group display with colors

### Matches
- Enter and edit match results
- Generate all matches automatically
- View match history and statistics

### Standings
- Automatic rankings by points, goal difference, goals for
- Group and global standings
- Qualified/eliminated status

### Knockout Stage
- Automatic generation from group phase
- Round-based organization (Round of 16, Quarterfinals, Semifinals, Final)
- Separate knockout match management

### Statistics
- Total teams, matches, goals
- Average goals per match
- Top 3 teams by various stats

### Data Persistence
- Automatic CSV save/load in `data/` directory
- All data preserved between sessions

## Quick Start

### Requirements
- Python 3.8+
- Tkinter (usually included with Python)

On Linux, you may need to install Tkinter:
```bash
sudo apt-get install python3-tk  # Debian/Ubuntu
sudo dnf install python3-tkinter  # Fedora/RHEL
sudo pacman -S tk                # Arch Linux
```

### Run the Application

```bash
cd football
python3 main.py
```

## Usage

### Create a Tournament
1. Click **File → New Tournament** (or use default name)
2. Add teams via **Teams tab → Add**
3. Create groups via **Groups → Create Groups (4)** or **Groups → Manual Groups**
4. Enter match results via **Matches tab → Enter Result**
5. Generate knockout stage via **Groups → Generate Knockout**

### Manual Group Composition
1. Click **Groups → Manual Groups**
2. Enter number of groups (2-8)
3. In the composition window:
   - Select a group for each team using the dropdown
   - Or click **Auto-Balance** for equal distribution
   - Or click **Random** for random distribution
4. Click **Apply** to confirm

### Save & Load
- **File → Save** - Save current tournament
- **File → Load** - Load previously saved tournament
- Data auto-loads on startup if available

## Project Structure

```
football/
├── main.py          # Entry point
├── app.py           # GUI application
├── model.py         # Data models (Team, Match, Group, Tournament)
├── saver.py         # CSV save/load functionality
├── colors.py        # Color theme constants
└── data/            # Saved tournament data (auto-created)
```

## Notes

- No external dependencies required
- Uses only Python standard library
- Data is saved in CSV format for easy editing
- Groups support up to 4 teams each (configurable in code)
- Top 3 teams from each group qualify by default
