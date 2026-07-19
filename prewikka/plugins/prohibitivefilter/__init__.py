import itertools
import pkg_resources

from prewikka import database, error, hookmanager, pluginmanager, resource, template, usergroup, version
from prewikka.dataprovider import Criterion
from prewikka.plugins.filter.filter import FilterDatabase

class PFDatabase(FilterDatabase):
    __sentinel = object()

    @staticmethod
    def is_valid_type(typ):
        return typ in ("user", "group", "tenant")

    @database.use_transaction
    def delete_prohibitivefilter(self, targettype, targetid, user):
        if not self.is_valid_type(targettype):
            return False

        filters = [f.id_ for f in self.get_filters(user)]
        if not filters:
            return False

        self.query("DELETE FROM Prewikka_ProhibitiveFilter_%s "
                   "WHERE targetid = %%(targetid)s AND filterid IN %%(filters)s" % targettype.capitalize(),
                   targetid=targetid, filters=filters)

    def set_prohibitivefilter(self, owner, targettype, targetid, filters):
        if not filters or not self.is_valid_type(targettype):
            return

        rows = self.query("SELECT id FROM Prewikka_Filter WHERE userid = %s AND name IN %s", owner.id, set(filters))
        self.query("INSERT INTO Prewikka_ProhibitiveFilter_%s (filterid, targetid) VALUES %%s" % targettype.capitalize(),
                   ((f[0], targetid) for f in rows))

    def get_prohibitivefilter_list(self, targettype, targetid):
        if not self.is_valid_type(targettype):
            return []

        return self.query("SELECT f.id, f.name, f.userid FROM Prewikka_Filter f "
                          "JOIN Prewikka_ProhibitiveFilter_%s pf ON pf.filterid = f.id "
                          "WHERE targetid = %%s" % targettype.capitalize(), targetid)

    def get_prohibitivefilter_criteria(self, targettype, targetid, criteria_type):
        criteria = Criterion()

        for id_, name, owner in self.get_prohibitivefilter_list(targettype, targetid):
            user = usergroup.User(userid=owner)

            filter = self.get_filter(user, name)
            if not filter:
                raise error.PrewikkaUserError(N_("Prohibitive Filter error"),
                                              N_("There is an issue with your user configuration, please contact the site administrator"))

            criteria &= filter.criteria.get(criteria_type)

        return criteria


class ProhibitiveFilter(pluginmanager.PluginBase):
    plugin_name = "Prohibitive filters"
    plugin_author = version.__author__
    plugin_license = version.__license__
    plugin_version = version.__version__
    plugin_copyright = version.__copyright__
    plugin_description = N_("Prohibitive filters that might be set on a user basis")
    plugin_database_branch = version.__branch__
    plugin_database_version = "0"
    plugin_htdocs = (("prohibitivefilter", pkg_resources.resource_filename(__name__, 'htdocs')),)
    plugin_require = ["prewikka.plugins.filter:FilterPlugin"]

    _template = template.PrewikkaTemplate(__name__, "templates/user.mak")

    def __init__(self):
        pluginmanager.PluginBase.__init__(self)
        self._db = PFDatabase()

    def _check_existing_filter(self, name):
        if not self._db.get_filter(env.request.user, name=name):
            raise error.PrewikkaUserError(N_("Filter error"), N_("Filter '%s' does not exist", name))

    def _read_filters_parameters(self):
        filters = []
        for f in env.request.parameters.getlist("existing_filter"):
            self._check_existing_filter(f)
            filters.append(f)

        return filters

    @hookmanager.register("HOOK_USERMANAGEMENT_EXTRA_CONTENT")
    @hookmanager.register("HOOK_GROUPMANAGEMENT_EXTRA_CONTENT")
    @hookmanager.register("HOOK_TENANTMANAGEMENT_EXTRA_CONTENT")
    def _get_filter_menu(self, target, target_type):
        dset = self._template.dataset()
        dset["available_filters"] = []
        dset["other_users_filters"] = []
        env.log.warning('je suis dedans ===============')
        env.log.warning("%s_MANAGEMENT" % target_type.upper())
        if not env.request.user.has("%s_MANAGEMENT" % target_type.upper()):
            return
        env.log.warning("test passe")

        if target:
            env.log.warning("il y a une target")
            for fid, name, ownerid in self._db.get_prohibitivefilter_list(target_type, target.id):
                env.log.warning(name)
                if ownerid != env.request.user.id:
                    dset["other_users_filters"] += [(usergroup.User(userid=ownerid).name, name)]
                else:
                    dset["available_filters"].append((name, True))

        env.log.warning(dset["available_filters"])
        for fltr in self._db.get_filters(env.request.user):
            if not (fltr.name, True) in dset["available_filters"]:
                env.log.warning(fltr.name)
                dset["available_filters"].append((fltr.name, False))

        return resource.HTMLSource(dset.render())

    @hookmanager.register("HOOK_DATAPROVIDER_CRITERIA_PREPARE")
    def _criteria_prepare(self, criteria_type):
        criteria = Criterion()
        criteria._is_prohibitive_filter = True

        for pftype, pfid in itertools.chain.from_iterable(hookmanager.trigger("HOOK_PROHIBITIVE_FILTER_CRITERIA_IDENTIFIER", criteria_type)):
            criteria += self._db.get_prohibitivefilter_criteria(pftype, pfid, criteria_type)

        return criteria

    @hookmanager.register("HOOK_USERMANAGEMENT_USER_MODIFY")
    @hookmanager.register("HOOK_GROUPMANAGEMENT_GROUP_MODIFY")
    @hookmanager.register("HOOK_TENANTMANAGEMENT_TENANT_MODIFY")
    @database.use_transaction
    def _authobj_modify(self, target):
        target_type = target.__class__.__name__.lower()

        # This is required to not let the user modify his own PF filter
        if not env.request.user.has("%s_MANAGEMENT" % target_type.upper()):
            return

        # Delete all prohibitive filters set by the current user for this target
        # Using upsert in set_prohibitivefilter() instead does not seem possible
        self._db.delete_prohibitivefilter(target_type, target.id, env.request.user)

        exist_filters = self._read_filters_parameters()
        self._db.set_prohibitivefilter(env.request.user, target_type, target.id, exist_filters)
        if exist_filters:
            env.log.info("Changed prohibitive filters to {0} for {1} \"{2}\"".format(", ".join(exist_filters), target_type, target.name))
