import random


class Vacuum:
    def __init__(self) -> None:
        self.message_db = {}

    def cleaning_probability(
        self, factor: float, msg_count: int, lower: int, upper: int
    ):
        # proximity to the upper limit as a value between 0 and 1
        proximity = 1.0 - (msg_count - lower) / (upper - lower)
        decay_factor = factor

        # weighted probability using an exponential decay function
        weighted_probability = (1 - proximity) ** decay_factor
        random_number = random.random()

        print(weighted_probability, random_number)
        # weighted probability exceeds the random number or count bigger than limit
        if weighted_probability > random_number or msg_count > upper:
            return True
        else:
            return False

    def needs_cleaning(
        self, channel_id, activity_limit: int, message_limit: int, factor: float
    ):
        if self.message_db.get(channel_id) != None:
            if self.message_db.get(channel_id) >= activity_limit:
                if self.cleaning_probability(
                    factor,
                    self.message_db.get(channel_id),
                    activity_limit,
                    message_limit,
                ):
                    self.message_db[channel_id] = 0
                    return True
            self.message_db[channel_id] += 1
        else:
            self.message_db[channel_id] = 1

        return False

    def random_channel(self, channel_list: []):
        # random index
        random_index_channel = random.randint(0, len(channel_list) - 1)
        # element at the random index
        random_channel = channel_list[random_index_channel]

        return random_channel

    def random_sound(self, sound_list: []):
        random_index_sound = random.randint(0, len(sound_list) - 1)
        random_sound = sound_list[random_index_sound]

        return random_sound
