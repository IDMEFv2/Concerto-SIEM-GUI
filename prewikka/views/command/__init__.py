from __future__ import absolute_import, division, print_function, unicode_literals

import errno
import json
import os
import subprocess
import sys

from prewikka import error, link, resource, template, utils, view, version


_COMMAND_ERRORS = {
    errno.ENOEXEC: N_("Shebang might be missing at the beginning of the script")
}


class Command(view.View, link.LinkManager):
    plugin_name = "System command"
    plugin_author = version.__author__
    plugin_license = version.__license__
    plugin_version = version.__version__
    plugin_copyright = version.__copyright__
    plugin_description = N_("Execution of system commands from the Prewikka console")
    plugin_locale = version.__locale__

    view_permissions = [N_("COMMAND")]

    def __init__(self):
        view.View.__init__(self)
        self._commands = {}

        for i in env.config.commands:
            self._init_url(i.get_instance_name() or "other", i)

    def _check_option(self, option, value):
        if not link.LinkManager._check_option(self, option, value):
            return False

        cmd = value.split(" ")[0]
        if not os.access(cmd, os.X_OK):
            env.log.warning("Plugin Command: could not add %s command because the %s file is not executable" % (option, cmd))
            return False

        return True

    def _register_link(self, paths, label, command):
        self._commands[label] = command
        env.linkmanager.add_link(label, paths, lambda x: url_for("command.command", command=label, value=x))

    @view.route("/command/<command>/<value>")
    def cmdajax(self, command, value):
        try:
            command = self._commands[command]
        except KeyError:
            raise error.PrewikkaUserError(None, N_("Attempt to execute unregistered command '%s'", command))

        command = command.replace("$value", value).split(" ")

        env.request.web.send_stream(json.dumps(_("Running the command") + "<br />..........................................<br />"), sync=True)
        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        except OSError as e:
            raise error.PrewikkaUserError(N_("Command error"), _COMMAND_ERRORS.get(e.errno, e))

        for line in iter(p.stdout.readline, b''):
            line = line.decode("utf-8", errors="replace")
            line = utils.html.escape(line).replace(" ", resource.HTMLSource("&nbsp;")).replace("\n", resource.HTMLSource("<br/>"))
            env.request.web.send_stream(json.dumps(line), sync=True)

        env.request.web.send_stream("close", event="close")

    @view.route("/command/<command>")
    def command(self, command):
        return template.PrewikkaTemplate(__name__, "templates/command.mak").dataset(command=command, value=env.request.parameters["value"])
