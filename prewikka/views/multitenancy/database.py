# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from prewikka import database, usergroup, utils


class MultitenancyDatabase(database.DatabaseHelper):
    def get_tenants(self, datatype):
        d = {}
        where = self.kwargs2query({"datatype": datatype}, prefix=" WHERE ") if datatype else ""
        rows = self.query("SELECT name, dbname FROM Prewikka_Tenant AS t "
                          "LEFT JOIN Prewikka_Tenant_Database AS td ON t.id = td.tenantid" + where)
        for name, db in rows:
            d[name] = db

        return d

    def get_user_tenants(self, user, datatype=None):
        if user.has("TENANT_MANAGEMENT"):
            return self.get_tenants(datatype)

        d = {}
        where = self.kwargs2query({"tu.userid": user.id, "td.datatype": datatype}, prefix=" WHERE ")
        rows = self.query("SELECT name, dbname FROM Prewikka_Tenant AS t "
                          "JOIN Prewikka_Tenant_User AS tu ON t.id = tu.tenantid "
                          "LEFT JOIN Prewikka_Tenant_Database AS td ON t.id = td.tenantid" + where)
        for name, db in rows:
            d[name] = db

        groups = [g.id for g in env.auth.get_member_of(user)]
        if groups:
            where = self.kwargs2query({"tg.groupid": groups, "td.datatype": datatype}, prefix=" WHERE ")
            rows = self.query("SELECT name, dbname FROM Prewikka_Tenant AS t "
                              "JOIN Prewikka_Tenant_Group AS tg ON t.id = tg.tenantid "
                              "LEFT JOIN Prewikka_Tenant_Database AS td ON t.id = td.tenantid" + where)
            for name, db in rows:
                d[name] = db

        return d

    def get_tenant_info(self, tenant):
        rows = self.query("SELECT id, contact FROM Prewikka_Tenant WHERE name = %s", tenant)
        if not rows:
            raise KeyError(_("No such entity"))

        tenantid, contact = rows[0]

        rows = self.query("SELECT datatype, dbname FROM Prewikka_Tenant_Database WHERE tenantid = %s", tenantid)
        db = {typ: name for typ, name in rows}

        rows = self.query("SELECT userid FROM Prewikka_Tenant_User WHERE tenantid = %s", tenantid)
        users = [usergroup.User(userid=r[0]) for r in rows]

        rows = self.query("SELECT groupid FROM Prewikka_Tenant_Group WHERE tenantid = %s", tenantid)
        groups = [usergroup.Group(groupid=r[0]) for r in rows]

        return utils.AttrObj(id=tenantid, name=tenant, contact=contact, db=db, users=users, groups=groups)

    def has_tenant(self, tenant):
        rows = self.query("SELECT 1 FROM Prewikka_Tenant WHERE name = %s", tenant)
        return bool(rows)

    def delete_tenant(self, tenant):
        self.query("DELETE FROM Prewikka_Tenant WHERE name = %s", tenant)
        env.log.info("Deleted entity \"%s\"" % tenant)

    @database.use_transaction
    def upsert_tenant(self, tenantid, name, contact, db, users, groups):
        userlst, grouplst = users.items(), groups.items()
        new_tenant = tenantid is None

        self.upsert("Prewikka_Tenant", ("id", "name", "contact"), [(tenantid, name, contact)], pkey=("id",))
        if new_tenant:
            tenantid = self.get_last_insert_ident()

        self.upsert("Prewikka_Tenant_Database", ("tenantid", "datatype", "dbname"), [(tenantid, typ, dbname) for typ, dbname in db.items()],
                    pkey=("tenantid", "datatype"), merge={"tenantid": tenantid})
        self.upsert("Prewikka_Tenant_User", ("tenantid", "userid"), [(tenantid, i[0]) for i in userlst], merge={"tenantid": tenantid})
        self.upsert("Prewikka_Tenant_Group", ("tenantid", "groupid"), [(tenantid, i[0]) for i in grouplst], merge={"tenantid": tenantid})

        if new_tenant:
            env.log.info("Added entity \"%s\"" % name)

        env.log.info("Changed entity \"%(tenant)s\", set users [%(users)s]" % {"users": ", ".join(i[1] for i in userlst), "tenant": name})
        env.log.info("Changed entity \"%(tenant)s\", set groups [%(groups)s]" % {"groups": ", ".join(i[1] for i in grouplst), "tenant": name})
