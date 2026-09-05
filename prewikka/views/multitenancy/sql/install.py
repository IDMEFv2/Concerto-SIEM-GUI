from __future__ import absolute_import, division, print_function, unicode_literals

from prewikka.database import SQLScript

from prewikka import version


class SQLUpdate(SQLScript):
    type = "install"
    branch = version.__branch__
    version = "0"

    def run(self):
        self.query("""
DROP TABLE IF EXISTS Prewikka_ProhibitiveFilter_Tenant;
DROP TABLE IF EXISTS Prewikka_Tenant_Group;
DROP TABLE IF EXISTS Prewikka_Tenant_User;
DROP TABLE IF EXISTS Prewikka_Tenant_Database;
DROP TABLE IF EXISTS Prewikka_Tenant;


CREATE TABLE Prewikka_Tenant (
    id BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    contact VARCHAR(255)
) ENGINE=InnoDB;


CREATE TABLE Prewikka_Tenant_Database (
    tenantid BIGINT UNSIGNED NOT NULL,
    dbname VARCHAR(255),
    datatype VARCHAR(255),
    PRIMARY KEY (tenantid, datatype),
    FOREIGN KEY (tenantid) REFERENCES Prewikka_Tenant(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE Prewikka_Tenant_User (
    tenantid BIGINT UNSIGNED NOT NULL,
    userid VARCHAR(32),
    PRIMARY KEY (tenantid, userid),
    FOREIGN KEY (tenantid) REFERENCES Prewikka_Tenant(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (userid) REFERENCES Prewikka_User(userid) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE Prewikka_Tenant_Group (
    tenantid BIGINT UNSIGNED NOT NULL,
    groupid VARCHAR(32),
    PRIMARY KEY (tenantid, groupid),
    FOREIGN KEY (tenantid) REFERENCES Prewikka_Tenant(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (groupid) REFERENCES Prewikka_Group(groupid) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE Prewikka_ProhibitiveFilter_Tenant (
        filterid BIGINT UNSIGNED NOT NULL,
        targetid VARCHAR(32) NOT NULL,
        PRIMARY KEY (filterid, targetid),
        FOREIGN KEY (filterid) REFERENCES Prewikka_Filter(id) ON DELETE CASCADE,
        FOREIGN KEY (targetid) REFERENCES Prewikka_Tenant(name) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
""")
