import random


class Vacuum:
    def __init__(self) -> None:
        self.message_db = {}

    def cleaning_probability(self):
        # taking action
        PROBABILITY = 1 / 10
        random_number = random.random()
        print(f"{PROBABILITY} to {random_number}")
        # check if we clean
        if random_number <= PROBABILITY:
            return True
        else:
            return False

    def needs_cleaning(self, channel_id: str, message_limit: int):
        if channel_id in self.message_db:
            if self.message_db[channel_id] < message_limit:
                self.message_db[channel_id] += 1
            else:
                self.message_db[channel_id] = 0
                return True
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
