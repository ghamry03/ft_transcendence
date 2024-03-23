class FriendRouter:
    route_app_labels = {"friends_api"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "default"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "default"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None
    
    def allow_syncdb(self, db, model):
        if db == 'default':
            return model._meta.app_label == 'friends_api'
        elif model._meta.app_label == 'friends_api':
            return False
        return None


class UserRouter:
    def db_for_read(self, model, **hints):
        return "users"

    def db_for_write(self, model, **hints):
        return "users"

    def allow_relation(self, obj1, obj2, **hints):
        db_set = {"default", "users"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_syncdb(self, db, model):
        if db == 'users':
            return model._meta.app_label == 'user_api'
        elif model._meta.app_label == 'user_api':
            return False
        return None