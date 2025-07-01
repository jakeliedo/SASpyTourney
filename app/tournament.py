import os, sys
# chèn thư mục libs vào front của sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
SYS_LIBS = os.path.join(ROOT, 'libs')
sys.path.insert(0, SYS_LIBS)
import sqlite3, time

class TournamentManager:
    def __init__(self, db_path='tourney.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS tournament_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT, slot_address TEXT,
            start_time TEXT, end_time TEXT,
            start_credits INTEGER, end_credits INTEGER
        )''')

    def start(self, player_id, addr, credit):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        self.conn.execute('INSERT INTO tournament_session (player_id, slot_address, start_time, start_credits) VALUES (?, ?, ?, ?)',
                        (player_id, addr, now, credit))
        self.conn.commit()

    def end(self, player_id, credit):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        self.conn.execute('''UPDATE tournament_session SET end_time=?, end_credits=? 
                            WHERE player_id=? AND end_time IS NULL''',
                        (now, credit, player_id))
        self.conn.commit()