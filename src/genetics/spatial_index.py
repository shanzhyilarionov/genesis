import config


class SpatialIndex:
    def __init__(self, life_list, bucket_size=16):
        self.bucket_size = bucket_size
        self.by_cell = {}
        self.prey_buckets = {}

        for organism in life_list:
            if organism.is_dead():
                continue
            self.add(organism)

    def _cell_key(self, x, y):
        return (x, y)

    def _bucket_key(self, x, y):
        return (x // self.bucket_size, y // self.bucket_size)

    def add(self, organism):
        if organism.is_dead():
            return

        cell_key = self._cell_key(organism.x, organism.y)
        self.by_cell.setdefault(cell_key, []).append(organism)

        if organism.species_id == config.SPECIES_A:
            bucket_key = self._bucket_key(organism.x, organism.y)
            self.prey_buckets.setdefault(bucket_key, []).append(organism)

    def remove(self, organism):
        cell_key = self._cell_key(organism.x, organism.y)
        occupants = self.by_cell.get(cell_key)
        if occupants is not None:
            if organism in occupants:
                occupants.remove(organism)
            if not occupants:
                del self.by_cell[cell_key]

        if organism.species_id == config.SPECIES_A:
            bucket_key = self._bucket_key(organism.x, organism.y)
            prey_list = self.prey_buckets.get(bucket_key)
            if prey_list is not None:
                if organism in prey_list:
                    prey_list.remove(organism)
                if not prey_list:
                    del self.prey_buckets[bucket_key]

    def move(self, organism, old_x, old_y, new_x, new_y):
        if old_x == new_x and old_y == new_y:
            return

        old_cell_key = self._cell_key(old_x, old_y)
        new_cell_key = self._cell_key(new_x, new_y)

        occupants = self.by_cell.get(old_cell_key)
        if occupants is not None:
            if organism in occupants:
                occupants.remove(organism)
            if not occupants:
                del self.by_cell[old_cell_key]

        self.by_cell.setdefault(new_cell_key, []).append(organism)

        if organism.species_id == config.SPECIES_A:
            old_bucket_key = self._bucket_key(old_x, old_y)
            new_bucket_key = self._bucket_key(new_x, new_y)

            if old_bucket_key != new_bucket_key:
                prey_list = self.prey_buckets.get(old_bucket_key)
                if prey_list is not None:
                    if organism in prey_list:
                        prey_list.remove(organism)
                    if not prey_list:
                        del self.prey_buckets[old_bucket_key]

                self.prey_buckets.setdefault(new_bucket_key, []).append(organism)

    def alive_same_cell_count(self, x, y):
        count = 0
        for organism in self.by_cell.get((x, y), []):
            if not organism.is_dead():
                count += 1
        return count

    def prey_exists_in_range(self, x, y, vision_range):
        bx0 = max(0, (x - vision_range) // self.bucket_size)
        bx1 = (x + vision_range) // self.bucket_size
        by0 = max(0, (y - vision_range) // self.bucket_size)
        by1 = (y + vision_range) // self.bucket_size

        for by in range(by0, by1 + 1):
            for bx in range(bx0, bx1 + 1):
                for prey in self.prey_buckets.get((bx, by), []):
                    if prey.is_dead():
                        continue
                    dx = prey.x - x
                    dy = prey.y - y
                    if abs(dx) <= vision_range and abs(dy) <= vision_range:
                        return True
        return False