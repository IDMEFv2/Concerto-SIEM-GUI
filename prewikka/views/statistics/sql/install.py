from __future__ import absolute_import, division, print_function, unicode_literals

from prewikka.database import SQLScript

from prewikka import version


class SQLUpdate(SQLScript):
    type = "install"
    branch = version.__branch__
    version = "0"

    def run(self):
        self.query("""
DROP TABLE IF EXISTS Prewikka_Widget;
CREATE TABLE Prewikka_Widget (
        userid VARCHAR(32) NOT NULL,
        view VARCHAR(255) NOT NULL,
        id VARCHAR(255) NOT NULL,
        config TEXT NOT NULL,
        PRIMARY KEY (userid, id),
        FOREIGN KEY (userid) REFERENCES Prewikka_User(userid) ON DELETE CASCADE
) ENGINE=InnoDB;
""")
