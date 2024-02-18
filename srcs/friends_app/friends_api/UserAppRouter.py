# project_current/db_router.py

class ProjectOtherRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'user_app':
            return 'users'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'user_app':
            return 'users'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return (
            obj1._meta.app_label == 'user_app' or
            obj2._meta.app_label == 'user_app'
        )

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'user_app':
            return db == 'users'
        return None
