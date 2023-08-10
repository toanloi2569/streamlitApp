from psycopg2._psycopg import connection

from services.postgres_connector import postgres_conn
from config import config

stored_entities = None


class ProjectDAO:
    def __init__(self, conn: connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_all_project_name(self):
        sql = (
            f"SELECT name FROM {config.SCHEMA}.projects;"
        )
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        result = list(map(lambda x: x[0], result))
        return result

    def get_all_project_stage(self):
        sql = (
            f"SELECT stage FROM {config.SCHEMA}.projects;"
        )
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_stage_of_project(self, project_name):
        sql = (
            f"SELECT stage FROM {config.SCHEMA}.projects WHERE name = '{project_name}';"
        )
        self.cursor.execute(sql)
        return self.cursor.fetchall()


class CustomerOrganizationDAO:
    def __init__(self, conn: connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_all_customer_organization_names(self):
        sql = (
            f"SELECT name FROM {config.SCHEMA}.customer_oganizations;"
        )
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        result = list(map(lambda x: x[0], result))
        return result


class MilestoneDAO:
    def __init__(self, conn: connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_all_milestones(self):
        sql = (
            f"SELECT \"milestoneDate\", subject, status, description FROM {config.SCHEMA}.milestones;"
        )
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_milestones_of_project(self, project_name):
        print(project_name)
        sql = (
            f"SELECT m.\"milestoneDate\", subject, status, description, p.name "
            f"FROM {config.SCHEMA}.milestones AS m, {config.SCHEMA}.projects AS p "
            f"WHERE m.\"projectId\" = p.id "
            f"  AND LOWER(P.name) like '{project_name.lower()}';"
        )
        self.cursor.execute(sql)
        return self.cursor.fetchall()


def get_stored_entities():
    global stored_entities

    if stored_entities is not None:
        return stored_entities

    project_dao = ProjectDAO(postgres_conn)
    customer_organization_dao = CustomerOrganizationDAO(postgres_conn)

    if stored_entities is not None:
        return stored_entities

    stored_entities = {
        'project_name': project_dao.get_all_project_name(),
        'organization': customer_organization_dao.get_all_customer_organization_names()
    }
    return stored_entities




