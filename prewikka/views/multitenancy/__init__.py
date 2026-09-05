# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import pkg_resources

from prewikka import error, hookmanager, resource, response, template, usergroup, utils, view, version
from prewikka.utils.viewhelpers import GridParameters

from .database import MultitenancyDatabase
from .multidb import MultiDatabase


class Tenant(object):
    def __init__(self, name):
        self.name = name

    @property
    def id(self):
        return self.name

    def __str__(self):
        return self.name


class Multitenancy(view.View):
    plugin_name = "Multitenancy"
    plugin_author = version.__author__
    plugin_license = version.__license__
    plugin_version = version.__version__
    plugin_copyright = version.__copyright__
    plugin_description = N_("Multitenancy plugin for Managed Security Service Providers (MSSPs)")
    plugin_database_branch = version.__branch__
    plugin_database_version = "0"
    plugin_htdocs = (("multitenancy", pkg_resources.resource_filename(__name__, 'htdocs')),)
    plugin_require = ["prewikka.plugins.prohibitivefilter:ProhibitiveFilter"]

    view_permissions = [N_("TENANT_MANAGEMENT")]

    _MENU_TMPL = template.PrewikkaTemplate(__name__, "templates/menu.mak")

    def __init__(self):
        self._database_names = {}
        self._init()
        self._db = MultitenancyDatabase()
        view.View.__init__(self)

    @hookmanager.register("HOOK_PLUGINS_PARTIAL_RELOAD")
    def _init(self):
        # WARNING: do not store a reference to the MultiDatabase instance here!
        # This would lead to an increasing number of SQL connections each time the plugin is reloaded.
        multidb = None

        for datatype in ("alert", "heartbeat"):
            # In case of a partial reload, try finding an existing IDMEF MultiDatabase instance
            if env.dataprovider.has_type(datatype) and datatype in self._database_names:
                multidb = env.dataprovider._backends[datatype]._db
                break

        for datatype in ("alert", "heartbeat"):
            if env.dataprovider.has_type(datatype) and datatype not in self._database_names:
                if multidb is None:
                    multidb = MultiDatabase(self, datatype)

                env.dataprovider._backends[datatype]._db = multidb
                self._database_names[datatype] = multidb.get_database_names()

        for datatype in ("log",):  # this could be extended to any non-IDMEF datatype
            if env.dataprovider.has_type(datatype) and datatype not in self._database_names:
                multidb = MultiDatabase(self, datatype)
                env.dataprovider._backends[datatype] = multidb
                self._database_names[datatype] = multidb.get_database_names()

    def _get_database_names(self, datatype):
        if not env.request.user or env.request.user.has("TENANT_MANAGEMENT"):
            return self._database_names.get(datatype, [])
        else:
            return []

    @hookmanager.register("HOOK_MAINMENU_PARAMETERS_REGISTER")
    def _parameters_register_hook(self, view):
        view.optional("datasource", text_type, save=True, general=True)
        return ["datasource"]

    @hookmanager.register("HOOK_PROHIBITIVE_FILTER_CRITERIA_IDENTIFIER")
    def _prohibitive_filter_criteria(self, ctype):
        ret = self.get_current_source(datatype=ctype)
        if ret and ret[0] == "tenant":
            return [("tenant", ret[1][0])]

        return []

    @hookmanager.register("HOOK_MAINMENU_EXTRA_CONTENT")
    def _html_menu(self, ctype, parameters, **kwargs):
        if not kwargs.get("with_datasource", True):
            return

        tenants = self._db.get_user_tenants(env.request.user, ctype)
        dbs = self._get_database_names(ctype)

        if not tenants and not dbs:
            return

        datasource = parameters.get("datasource")
        if not datasource and kwargs.get("period_optional"):
            current_source = None
        else:
            typ, source = self.get_current_source(datasource, ctype)
            current_source = "%s:%s" % (typ, source[0] if typ == "tenant" else source)

        dset = self._MENU_TMPL.dataset(
            current_source=current_source,
            tenants=sorted(tenants),
            databases=dbs,
            **kwargs
        )

        return resource.HTMLSource(dset.render())

    @hookmanager.register("HOOK_USER_ENTITIES")
    def _get_entities(self):
        return sorted(self._db.get_user_tenants(env.request.user).keys())

    @hookmanager.register("HOOK_USER_ENTITY_BY_DATABASE")
    def _get_entity_by_database(self, name, datatype):
        dbs = self._get_database_names(datatype)
        if name in dbs:
            return "database:%s" % name

        for tenant, dbname in self._db.get_user_tenants(env.request.user, datatype).items():
            if dbname == name:
                return "tenant:%s" % tenant

    @hookmanager.register("HOOK_CHART_PREPARE")
    def _chart_prepare(self, query, options):
        datasource = options.get("datasource")
        if datasource:
            env.request.menu_parameters["datasource"] = datasource

    @hookmanager.register("HOOK_CRON_DELETE")
    def _cron_delete(self, criteria, datatype):
        for name in self._get_database_names(datatype):
            env.request.menu_parameters["datasource"] = "database:%s" % name
            env.dataprovider.delete(criteria, type=datatype)
            env.request.cache.multitenancy_current_source.clear()

    def get_default_source(self, datatype, tenants=None):
        dbl = self._get_database_names(datatype)
        if dbl:
            return "database", dbl[0]

        if not tenants and not env.request.user:
            return None

        for tenant, dbname in (tenants or self._db.get_user_tenants(env.request.user, datatype)).items():
            return "tenant", (tenant, dbname)

    def _parse_source_string(self, name):
        if not name:
            return

        source = name.split(":", 1)
        if len(source) != 2:
            return

        return source

    def get_current_source(self, name=None, datatype=None):
        # FIXME #3681: needed because memoize() does not support keyword arguments
        return self._get_current_source(name, datatype)

    @utils.cache.request_memoize("multitenancy_current_source")
    def _get_current_source(self, name, datatype):
        if not name and env.request.view:
            name = env.request.menu_parameters.get("datasource")

        if not name and env.request.user:
            name = env.request.user.get_property("datasource", view=None)

        source = self._parse_source_string(name)
        if not source:
            return self.get_default_source(datatype)

        stype, sname = source
        if stype == "database":
            if sname in self._get_database_names(datatype):
                return "database", sname

            return self.get_default_source(datatype)

        if env.request.user:
            tenants = self._db.get_user_tenants(env.request.user, datatype)
        else:
            tenants = self._db.get_tenants(datatype)

        dbname = tenants.get(sname)
        if dbname:
            return "tenant", (sname, dbname)

        return self.get_default_source(datatype, tenants=tenants)

    @view.route("/entities/edit")
    @view.route("/entities/<path:name>/edit")
    def edit(self, name=None):
        dataset = template.PrewikkaTemplate(__name__, "templates/entityedit.mak").dataset(
            tenant=self._db.get_tenant_info(name) if name else utils.AttrObj(
                id=None, name=None, contact=None, db={}, users=[], groups=[]
            ),
            datatypes=[t for t in self._database_names if t != "heartbeat"],
            alldatabases={datatype: self._get_database_names(datatype) for datatype in self._database_names},
            extra_content=filter(None, hookmanager.trigger("HOOK_TENANTMANAGEMENT_EXTRA_CONTENT", Tenant(name) if name else None, "tenant"))
        )

        return dataset.render()

    @view.route("/entities/delete", methods=["POST"])
    def delete(self):
        for tenant in env.request.parameters.getlist("id"):
            self._db.delete_tenant(tenant)
            list(hookmanager.trigger("HOOK_TENANT_DELETE", Tenant(tenant)))

    @view.route("/entities/save", methods=["POST"])
    @view.route("/entities/<path:name>/save", methods=["POST"])
    def save(self, name=None):
        tenant_id = env.request.parameters.get("tenantid")
        tenant_name = env.request.parameters.get("name")
        tenant_contact = env.request.parameters.get("contact")
        tenant_db = env.request.parameters.get("database", {})
        tenant_users = env.request.parameters.getlist("users")
        tenant_groups = env.request.parameters.getlist("groups")

        if "alert" in tenant_db:
            tenant_db["heartbeat"] = tenant_db["alert"]

        if not tenant_name:
            raise error.PrewikkaUserError(N_("Could not save entity"),
                                          N_("No name for this entity was provided"))

        if tenant_name.startswith("/"):
            raise error.PrewikkaUserError(N_("Could not save entity"),
                                          N_("The entity name cannot start with a slash"))

        if self._db.has_tenant(tenant_name) and name != tenant_name:
            raise error.PrewikkaUserError(N_("Could not save entity"),
                                          N_("This name is already used by another entity"))

        users = {}
        for username in tenant_users:
            user = usergroup.User(username)
            if not env.auth.has_user(user):
                raise error.PrewikkaUserError(N_("Invalid User"),
                                              N_("Requested user '%s' does not exist", username))
            users[user.id] = username

        groups = {}
        for groupname in tenant_groups:
            group = usergroup.Group(groupname)
            if not env.auth.has_group(group):
                raise error.PrewikkaUserError(N_("Invalid Group"),
                                              N_("Requested group '%s' does not exist", groupname))
            groups[group.id] = groupname

        self._db.upsert_tenant(tenant_id, tenant_name, tenant_contact, tenant_db, users, groups)

        list(hookmanager.trigger("HOOK_TENANTMANAGEMENT_TENANT_MODIFY", Tenant(tenant_name)))

        resp = response.PrewikkaResponse({"type": "reload", "target": "view"})

        if not users and not groups:
            resp.add_notification(_("Your changes have been saved successfully. "
                                    "However, there are currently no users or groups associated "
                                    "with this entity, making it unusable."))
        else:
            resp.add_notification(_("Your changes have been saved successfully."))

        return resp

    @view.route("/entities/entities", menu=(N_("Access control"), N_("Entities")), help="#entities", parameters=GridParameters("entities"))
    def listing(self):
        dataset = template.PrewikkaTemplate(__name__, "templates/entities.mak").dataset({
            "data": [],
            "datatypes": [t for t in self._database_names if t != "heartbeat"]
        })

        for (name,) in self._db.query("SELECT name FROM Prewikka_Tenant ORDER BY name"):
            infos = self._db.get_tenant_info(name)

            dataset["data"].append(dict(
                name=resource.HTMLNode("a", name, href=url_for(".edit", name=name)),
                contact=infos.contact,
                users=[user.name for user in infos.users],
                groups=[group.name for group in infos.groups],
                **infos.db
            ))

        return dataset.render()
