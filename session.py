class SessionManager:
    def __init__(self, tokens_str, uids_str):
        # تبدیل رشته‌های .env به لیست
        self.tokens = [t.strip() for t in tokens_str.split(",")]
        self.uids = [u.strip() for u in uids_str.split(",")]
        self.current_index = 0
        
        if len(self.tokens) != len(self.uids):
            print("[!] Warning: Tokens and UIDs count mismatch!")

    def get_next_session(self):
        token = self.tokens[self.current_index]
        uid = self.uids[self.current_index]
        
        # حرکت به ایندکس بعدی (چرخشی)
        self.current_index = (self.current_index + 1) % len(self.tokens)
        
        return token, uid