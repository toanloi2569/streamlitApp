from thefuzz import fuzz

from dao.postgres_dao import get_stored_entities
from dao.postgres_dao import ProjectDAO, MilestoneDAO
from services.postgres_connector import postgres_conn


class IntentFuncMapper:
    def __init__(self):
        self.intent_func_map = {
            'get_project_state': get_project_stage,
            'get_project_milestone': get_project_milestone,
        }

    def get_func(self, intent):
        return self.intent_func_map[intent]


def get_project_stage(entities: dict):
    project_dao = ProjectDAO(postgres_conn)
    if 'project' in entities:
        entities['project'] = get_best_similarity_values(entities['project'][0], get_stored_entities()['project'])
        project_states = project_dao.get_stage_of_project(entities['project'])
        return project_states

    else:
        project_states = project_dao.get_all_project_stage()
        return project_states


def get_project_milestone(entities):
    milestone_dao = MilestoneDAO(postgres_conn)
    if 'project' in entities:

        entities['project'] = get_best_similarity_values(entities['project'][0], get_stored_entities()['project'])
        milestones = milestone_dao.get_all_milestones_of_project(entities['project'])
        return milestones

    else:
        milestones = milestone_dao.get_all_milestones()
        return milestones


def get_best_similarity_values(value, values):
    print(value)
    sorted_values = sorted(values, key=lambda v: fuzz.token_sort_ratio(v, value), reverse=True)
    ratio_value = sorted([fuzz.token_sort_ratio(v, value) for v in values], reverse=True)
    print(sorted_values)
    print(ratio_value)
    return sorted_values[0]
