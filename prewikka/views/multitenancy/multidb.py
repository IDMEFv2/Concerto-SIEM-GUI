# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from prewikka import error, idmefdatabase, log, usergroup


class NoTenantAccessError(usergroup.PermissionDeniedError):
    def __init__(self):
        msg = N_("You do not have access to any entity database. "
                 "Please contact your local administrator to request access.")
        error.PrewikkaUserError.__init__(self, N_("Permission Denied"), msg, log_priority=log.WARNING)


class MultiDatabase(object):
    def __init__(self, plugin, datatype):
        self._dbs = {}
        self._plugin = plugin
        self._datatype = datatype

        if datatype == "alert":
            for dbconfig in env.config.idmef_database:
                try:
                    self._dbs[self._get_dbname(dbconfig)] = idmefdatabase.IDMEFDatabase(dbconfig)
                except RuntimeError as e:
                    env.log.error("Multitenancy database [idmef_database %(name)s] error: %(error)s" %
                                  {'error': e, 'name': dbconfig.get_instance_name() or ""})

        else:
            self._dbs = env.dataprovider._backends[datatype]._instances

    @staticmethod
    def _get_dbname(dbconf):
        r = dbconf.get_instance_name()
        return r or "%s@%s" % (dbconf.get("name", "prelude"), dbconf.get("host", "localhost"))

    def __getattr__(self, attr):
        ret = self._plugin.get_current_source(datatype=self._datatype)
        if not ret:
            raise NoTenantAccessError()

        stype, dbname = ret
        if stype == "tenant":
            _, dbname = dbname

        try:
            return getattr(self._dbs[dbname], attr)
        except KeyError:
            raise error.PrewikkaUserError(N_("Configuration error"),
                                          N_("Multitenancy database '%s' not found. Check your configuration.", (dbname or '')))

    def get_database_names(self):
        return sorted(self._dbs)
