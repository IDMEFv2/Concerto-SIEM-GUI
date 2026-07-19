from prewikka.database import SQLScript

from prewikka import version


class SQLUpdate(SQLScript):
    type = "install"
    branch = version.__branch__
    version = "0"

    def run(self):
        self.query("""
DROP TABLE IF EXISTS Prewikka_ProhibitiveFilter_User;

CREATE TABLE Prewikka_ProhibitiveFilter_User (
        filterid BIGINT UNSIGNED NOT NULL,
        targetid VARCHAR(32) NOT NULL,
        PRIMARY KEY (filterid, targetid),
        FOREIGN KEY (filterid) REFERENCES Prewikka_Filter(id) ON DELETE CASCADE,
        FOREIGN KEY (targetid) REFERENCES Prewikka_User(userid) ON DELETE CASCADE
) ENGINE=InnoDB;


DROP TABLE IF EXISTS Prewikka_ProhibitiveFilter_Group;

CREATE TABLE Prewikka_ProhibitiveFilter_Group (
        filterid BIGINT UNSIGNED NOT NULL,
        targetid VARCHAR(32) NOT NULL,
        PRIMARY KEY (filterid, targetid),
        FOREIGN KEY (filterid) REFERENCES Prewikka_Filter(id) ON DELETE CASCADE,
        FOREIGN KEY (targetid) REFERENCES Prewikka_Group(groupid) ON DELETE CASCADE
) ENGINE=InnoDB;
""")
