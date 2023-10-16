import random


class Vacuum:
    def __init__(self) -> None:
        self.message_db = {}

    def cleaning_probability(self, msg_count: int, upper: int, lower: int):
        # random number above activity limit
        random_number = random.randint(lower, upper)
        # check if we clean
        if random_number == msg_count or msg_count > upper:
            return True
        else:
            return False

    def needs_cleaning(self, channel_id, activity_limit: int, message_limit: int):
        if self.message_db.get(channel_id) != None:
            if self.message_db.get(channel_id) >= activity_limit:
                if self.cleaning_probability(self.message_db.get(channel_id), message_limit, activity_limit):
                    self.message_db[channel_id] = 0
                    return True
            self.message_db[channel_id] += 1
        else:
            self.message_db[channel_id] = 1

        return False

    def generate_vacuum_channel(self, channel_list: [], sound_list: []):
        # random index
        random_index_channel = random.randint(0, len(channel_list) - 1)
        random_index_sound = random.randint(0, len(sound_list) - 1)
        # element at the random index
        random_channel = channel_list[random_index_channel]
        random_sound = sound_list[random_index_sound]

        return [random_channel, random_sound]
