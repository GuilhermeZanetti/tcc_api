from enum import Enum


class Permissions(Enum):
    READ_PROBLEMS = "read:problems"
    READ_SUBMISSIONS = "read:submissions"
    
    CREATE_PROBLEMS = "create:problems"
    CREATE_SUBMISSIONS = "create:submissions"
    
    UPDATE_PROBLEMS = "update:problems"
    UPDATE_SUBMISSIONS = "update:submissions"
    
    DELETE_PROBLEMS = "delete:problems"
    DELETE_SUBMISSIONS = "delete:submissions"