from psycopg2._psycopg import connection

from services.postgres_connector import postgres_conn
from config import config


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
            f"SELECT stage, name as project_name FROM {config.SCHEMA}.projects;"
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_all_project_with_stage(self, stage):
        sql = (
            f"SELECT name, stage FROM {config.SCHEMA}.projects "
            f"WHERE LOWER(stage) = '{stage.lower()}';"
        )
        print(sql)
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_stage_of_project(self, project_name):
        sql = (
            f"SELECT stage, name AS project_name FROM {config.SCHEMA}.projects WHERE name = '{project_name}';"
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }


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
        columns = [desc[0] for desc in self.cursor.descriptions]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_all_milestones_of_project(self, project_name):
        print(project_name)
        sql = (
            f"SELECT m.\"milestoneDate\", subject, status, description, p.name as project_name "
            f"FROM {config.SCHEMA}.milestones AS m, {config.SCHEMA}.projects AS p "
            f"WHERE m.\"projectId\" = p.id "
            f"  AND LOWER(P.name) like '{project_name.lower()}';"
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }


class IssueDAO:
    def __init__(self, conn: connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_all_issues(self):
        sql = (
            f"SELECT "
            f"  i.\"dueDate\", "
            f"  i.\"startDate\", "
            f"  i.subject, "
            f"  i.description, "
            f"  i.\"rootCause\", "
            f"  i.\"correctiveAction\", "
            f"  i.\"preventiveAction\", "
            f"  i.\"criticalLevel\", "
            f"  i.status, "
            f"  p.name as project_name "
            f"FROM {config.SCHEMA}.issues AS i, {config.SCHEMA}.projects AS p "
            f"WHERE i.\"projectId\" = p.id "
            f"  AND i.type = 'Issues' "
            f"  AND (i.status = 'Open' OR i.status = 'Solving') "
            f"  AND (i.\"updatedAt\" >= NOW() - INTERVAL '1 month') "
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_all_issues_of_project(self, project_name):
        sql = (
            f"SELECT "
            f"  i.\"dueDate\", "
            f"  i.\"startDate\", "
            f"  i.subject, "
            f"  i.description, "
            f"  i.\"rootCause\", "
            f"  i.\"correctiveAction\", "
            f"  i.\"preventiveAction\", "
            f"  i.\"criticalLevel\", "
            f"  i.status, "
            f"  p.name as project_name "
            f"FROM {config.SCHEMA}.issues AS i, {config.SCHEMA}.projects AS p "
            f"WHERE i.\"projectId\" = p.id "
            f"  AND i.type = 'Issues' "
            f"  AND (i.status = 'Open' OR i.status = 'Solving') "
            f"  AND LOWER(p.name) like '{project_name.lower()}';"
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_all_solved_issues(self):
        sql = (
            f"SELECT "
            f"  i.\"dueDate\", "
            f"  i.\"startDate\", "
            f"  i.subject, "
            f"  i.description, "
            f"  i.\"rootCause\", "
            f"  i.\"correctiveAction\", "
            f"  i.\"preventiveAction\", "
            f"  i.\"criticalLevel\", "
            f"  i.status, "
            f"  p.name as project_name "
            f"FROM {config.SCHEMA}.issues AS i, {config.SCHEMA}.projects AS p "
            f"WHERE i.\"projectId\" = p.id "
            f"  AND i.type = 'Issues' "
            f"  AND (i.status = 'Closed' OR i.status = 'Solved') "
            f"  AND (i.\"updatedAt\" >= NOW() - INTERVAL '2 month') "
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_solved_issues_of_project(self, project_name):
        sql = (
            f"SELECT "
            f"  i.\"dueDate\", "
            f"  i.\"startDate\", "
            f"  i.subject, "
            f"  i.description, "
            f"  i.\"rootCause\", "
            f"  i.\"correctiveAction\", "
            f"  i.\"preventiveAction\", "
            f"  i.\"criticalLevel\", "
            f"  i.status, "
            f"  p.name as project_name "
            f"FROM {config.SCHEMA}.issues AS i, {config.SCHEMA}.projects AS p "
            f"WHERE i.\"projectId\" = p.id "
            f"  AND i.type = 'Issues' "
            f"  AND (i.status = 'Closed' OR i.status = 'Solved') "
            f"  AND (i.\"updatedAt\" >= NOW() - INTERVAL '1 month') "
            f"  AND LOWER(p.name) like '{project_name.lower()}';"
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }


class RiskDAO:
    def __init__(self, conn: connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_all_risks(self):
        sql = (
            f"SELECT "
            f"  i.\"dueDate\", "
            f"  i.\"startDate\", "
            f"  i.subject, "
            f"  i.description, "
            f"  i.\"rootCause\", "
            f"  i.\"correctiveAction\", "
            f"  i.\"preventiveAction\", "
            f"  i.\"criticalLevel\", "
            f"  i.status, "
            f"  p.name as project_name "
            f"FROM {config.SCHEMA}.issues AS i, {config.SCHEMA}.projects AS p "
            f"WHERE i.\"projectId\" = p.id "
            f"  AND i.type = 'Risks' "
            f"  AND (i.\"updatedAt\" >= NOW() - INTERVAL '1 month') "
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_all_risks_of_project(self, project_name):
        print(project_name)
        sql = (
            f"SELECT "
            f"  i.\"dueDate\", "
            f"  i.\"startDate\", "
            f"  i.subject, "
            f"  i.description, "
            f"  i.\"rootCause\", "
            f"  i.\"correctiveAction\", "
            f"  i.\"preventiveAction\", "
            f"  i.\"criticalLevel\", "
            f"  i.status, "
            f"  p.name as project_name "
            f"FROM {config.SCHEMA}.issues AS i, {config.SCHEMA}.projects AS p "
            f"WHERE i.\"projectId\" = p.id "
            f"  AND i.type = 'Risks' "
            f"  AND (i.status = 'Open' OR i.status = 'Solving') "
            f"  AND LOWER(p.name) like '{project_name.lower()}';"
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }


class ActivityDAO:
    def __init__(self, conn: connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_all_activities(self):
        sql = (
            f"SELECT p.name as project_name, a.current_status, a.next_plan, a.\"updatedAt\"  "
            f"FROM {config.SCHEMA}.activities AS a, {config.SCHEMA}.projects AS p "
            f"WHERE a.\"projectId\" = p.id "
            f"  AND (a.\"updatedAt\" >= NOW() - INTERVAL '2 week') "
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }

    def get_all_activities_of_project(self, project_name):
        sql = (
            f"SELECT p.name as project_name, a.current_status, a.next_plan, a.\"updatedAt\" "
            f"FROM {config.SCHEMA}.activities AS a, {config.SCHEMA}.projects AS p "
            f"WHERE a.\"projectId\" = p.id "
            f"  AND (a.\"updatedAt\" >= NOW() - INTERVAL '2 week') "
            f"  AND LOWER(p.name) like '{project_name.lower()}';"
        )
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]
        result = self.cursor.fetchall()
        return {
            'columns': columns,
            'result': result
        }


def get_stored_entities():
    project_dao = ProjectDAO(postgres_conn)
    customer_organization_dao = CustomerOrganizationDAO(postgres_conn)

    stored_entities = {
        'project_name': project_dao.get_all_project_name(),
        'organization': customer_organization_dao.get_all_customer_organization_names()
    }
    return stored_entities


stored_entities = get_stored_entities()

