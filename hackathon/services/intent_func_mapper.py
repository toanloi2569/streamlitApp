from thefuzz import fuzz

from dao.postgres_dao import stored_entities, IssueDAO, RiskDAO, ActivityDAO
from dao.postgres_dao import ProjectDAO, MilestoneDAO
from services.postgres_connector import postgres_conn
from config.constance import project_stages


class IntentFuncMapper:
    def __init__(self):
        self.intent_func_map = {
            'get_project_stages': get_project_stages,
            'get_project_milestones': get_project_milestones,
            'get_project_issues': get_project_issues,
            'get_project_risks': get_project_risks,
            'get_solved_issues': get_solved_issues,
            'get_project_activities': get_project_activities,
            'get_bot_info': get_bot_info,
            'other': other_func
        }

    def get_func(self, intent):
        return self.intent_func_map[intent]


def get_project_stages(entities: dict):
    project_dao = ProjectDAO(postgres_conn)
    entities = map_entities(entities)
    if 'project_name' in entities:
        project_stages = project_dao.get_stage_of_project(entities['project_name'])
        return project_stages

    if 'stage' in entities:
        project_stages = project_dao.get_all_project_with_stage(entities['stage'])
        return project_stages

    project_stages = project_dao.get_all_project_stage()
    return project_stages


def get_project_milestones(entities):
    milestone_dao = MilestoneDAO(postgres_conn)
    entities = map_entities(entities)
    if 'project_name' in entities:
        milestones = milestone_dao.get_all_milestones_of_project(entities['project_name'])
        return milestones

    milestones = milestone_dao.get_all_milestones()
    return milestones


def get_project_issues(entities):
    issue_dao = IssueDAO(postgres_conn)
    entities = map_entities(entities)
    if 'project_name' in entities:
        issues = issue_dao.get_all_issues_of_project(entities['project_name'])
        return issues

    issues = issue_dao.get_all_issues()
    return issues


def get_project_risks(entities):
    risk_dao = RiskDAO(postgres_conn)
    entities = map_entities(entities)
    if 'project_name' in entities:
        risks = risk_dao.get_all_risks_of_project(entities['project_name'])
        return risks

    risks = risk_dao.get_all_risks()
    return risks


def get_solved_issues(entities):
    issue_dao = IssueDAO(postgres_conn)
    entities = map_entities(entities)
    if 'project_name' in entities:
        issues = issue_dao.get_solved_issues_of_project(entities['project_name'])
        return issues

    issues = issue_dao.get_all_solved_issues()
    return issues


def get_project_activities(entities):
    activity_dao = ActivityDAO(postgres_conn)
    entities = map_entities(entities)
    if 'project_name' in entities:
        activities = activity_dao.get_all_activities_of_project(entities['project_name'])
        return activities

    activities = activity_dao.get_all_activities()
    return activities


def other_func(entities):
    return 'Trả lời như một câu hỏi thông thường'


def get_bot_info(entities):
    return (
            'Trả lời các intent có thể hỗ trợ, bao gồm: \n' 
            '- get_project_stages: lấy trạng thái của dự án \n'
            '- get_project_milestones: lấy các mốc của dự án \n'
            '- get_project_issues: lấy các vấn đề của dự án \n'
            '- get_project_risks: lấy các rủi ro của dự án \n'
            '- get_solved_issues: lấy các vấn đề đã được giải quyết của dự án \n'
            '- get_project_activities: lấy các hoạt động của dự án \n'
    )


def get_best_similarity_values(value, values):
    sorted_values = sorted(
        values,
        key=lambda v: fuzz.token_sort_ratio(v.replace('_', ' '), value.replace('_', ' ')),
        reverse=True
    )
    return sorted_values[0]


def map_entities(entities):
    if 'project_name' in entities:
        entities['project_name'] = get_best_similarity_values(
            entities['project_name'][0],
            stored_entities['project_name']
        )

    if 'organization' in entities:
        entities['project_name'] = get_best_similarity_values(
            entities['organization'][0],
            stored_entities['project_name']
        )
        entities['organization'] = get_best_similarity_values(
            entities['organization'][0],
            stored_entities['organization']
        )

    if 'stage' in entities:
        entities['stage'] = get_best_similarity_values(
            entities['stage'][0],
            project_stages
        )

    return entities
