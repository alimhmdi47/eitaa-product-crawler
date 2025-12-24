import random
import time

class SessionManager:
    def __init__(self, tokens_str, uids_str, proxies_str=None):
        # اکانت‌ها (جفت‌های ثابت)
        tokens = [t.strip() for t in tokens_str.split(",") if t.strip()]
        uids = [u.strip() for u in uids_str.split(",") if u.strip()]
        # سبد پروکسی‌ها (مستقل از اکانت‌ها)
        self.proxy_pool = [p.strip() for p in proxies_str.split(",") if p.strip()] if proxies_str else []     

        self.accounts = []
        for i, token in enumerate(tokens):
            self.accounts.append({
                "token": token,
                "uid": uids[i] if i < len(uids) else uids[0],
                "next_available_time": 0
            })

    def get_random_session(self):
        now = time.time()
        # ۱. انتخاب اکانت آزاد
        available_accounts = [acc for acc in self.accounts if now > acc["next_available_time"]]
        
        if not available_accounts:
            print("[!] No free accounts. Waiting...")
            time.sleep(10)
            return None, None, None
            
        chosen_acc = random.choice(available_accounts)
        
        # ۲. انتخاب یک پروکسی کاملاً تصادفی از سبد (مستقل از اینکه کی هستی)
        chosen_proxy = random.choice(self.proxy_pool) if self.proxy_pool else None
        
        return chosen_acc["token"], chosen_acc["uid"], chosen_proxy

    def penalize(self, token, duration=600):
        for acc in self.accounts:
            if acc["token"] == token:
                acc["next_available_time"] = time.time() + duration
                break