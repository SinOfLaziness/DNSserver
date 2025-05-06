import time

class Cache:
    def __init__(self):
        self.cache = {}

    def get(self, cache_key):
        return self.cache.get(cache_key)

    def save_in_cache(self, resource_records, domain_name, question_type):
        cache_key = f"{domain_name}_{question_type}"
        self.cache[cache_key] = resource_records

    def clean_cache(self):
        now = time.time()
        expired_keys = []
        for key, records in self.cache.items():
            if any(rr.ttl + rr.time_created < now for rr in records):
                expired_keys.append(key)
        for key in expired_keys:
            del self.cache[key]