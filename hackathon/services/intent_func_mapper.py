from thefuzz import fuzz

from dao.postgres_dao import get_stored_entities
from dao.postgres_dao import ProjectDAO, MilestoneDAO
from services.postgres_connector import postgres_conn


class IntentFuncMapper:
    def __init__(self):
        self.intent_func_map = {
            'get_project_stages': get_project_stages,
            'get_project_milestones': get_project_milestones,
        }

    def get_func(self, intent):
        return self.intent_func_map[intent]


def get_project_stages(entities: dict):
    project_dao = ProjectDAO(postgres_conn)
    if 'project_name' in entities:
        entities['project_name'] = get_best_similarity_values(entities['project_name'][0], get_stored_entities()['project_name'])
        project_stages = project_dao.get_stage_of_project(entities['project_name'])
        return project_stages

    else:
        project_stages = project_dao.get_all_project_stage()
        return project_stages


def get_project_milestones(entities):
    milestone_dao = MilestoneDAO(postgres_conn)
    if 'project_name' in entities:
        entities['project_name'] = get_best_similarity_values(entities['project_name'][0], get_stored_entities()['project_name'])
        milestones = milestone_dao.get_all_milestones_of_project(entities['project_name'])
        return milestones

    else:
        milestones = milestone_dao.get_all_milestones()
        return milestones


def get_best_similarity_values(value, values):
    sorted_values = sorted(values, key=lambda v: fuzz.token_sort_ratio(v, value), reverse=True)
    return sorted_values[0]
