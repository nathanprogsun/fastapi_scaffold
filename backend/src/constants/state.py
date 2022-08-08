from enum import IntEnum


class ResultType(IntEnum):
    no_result = 0
    dataset = 1
    model = 2


class ResultState(IntEnum):
    processing = 0
    ready = 1
    error = 2


class IterationStage(IntEnum):
    prepare_mining = 0
    mining = 1
    label = 2
    prepare_training = 3
    training = 4
    end = 5


class MiningStrategy(IntEnum):
    chunk = 0
    dedup = 1
    customize = 2


class TrainingType(IntEnum):
    object_detect = 1
