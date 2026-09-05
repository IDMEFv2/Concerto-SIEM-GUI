# Copyright (C) 2015-2020 CS GROUP - France. All Rights Reserved.
# Author: Yoann Vandoorselaere <yoannv@gmail.com>

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import functools

from itertools import tee

from prewikka import error, localization, statistics, view
from prewikka.dataprovider import Criterion
from prewikka.renderer import RendererItem
from prewikka.utils import json


class MetricChart(statistics.GenericChart):
    TYPES = ["number"]

    def get_data(self):
        query = self.query[0]
        all_paths, all_criteria = self._prepare_query(query)

        data = self._query(all_paths, all_criteria, limit=query.limit, type=query.datatype)
        if data:
            link = self._make_link(query.criteria, **self._menu.get_parameters())
            return RendererItem(data[0][0], None, link)


class MapChart(statistics.DiagramChart):
    TYPES = ["world"]

    def __init__(self, chart_type, title, query, **options):
        query[0].paths, query[0].criteria = self.get_defaults()
        query[0].limit = -1
        statistics.DiagramChart.__init__(self, chart_type, title, query, **options)

    @staticmethod
    def get_defaults():
        return (
            ["alert.additional_data.data"],
            Criterion("alert.additional_data.meaning", "~", "alert\.source\(\d+\)\.node\.location\.country_code")
        )


class ListingChart(statistics.GenericChart):
    TYPES = ["table"]

    def get_data(self):
        query = self.query[0]
        all_paths, all_criteria = self._prepare_query(query)

        data = []
        for row in self._query(all_paths, all_criteria, limit=query.limit, type=query.datatype):
            data.append(RendererItem(series=tuple(row[1:])))  # exclude the time field

        return [data]


class FluxChart(statistics.GenericChart):
    TYPES = ["sankey"]

    def __init__(self, chart_type, title, query, **options):
        if len(query[0].paths) < 2:
            raise error.PrewikkaUserError(N_("Statistics error"), N_("The chart needs at least two paths"))

        statistics.GenericChart.__init__(self, chart_type, title, query, **options)

    @staticmethod
    def _pairwise(iterable):
        """
        s -> (s0,s1), (s1,s2), (s2,s3), ...
        """
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    @staticmethod
    def _getNodeID(nodes, nid, name):
        if not name:
            name = "n/a"

        key = (name, nid)
        if key not in nodes:
            nodes[key] = {'name': name, 'id': len(nodes)}

        return nodes[key]["id"]

    def get_data(self):
        query = self.query[0]
        all_paths, all_criteria = self._prepare_query(query)

        nodes = collections.OrderedDict()
        edges = collections.defaultdict(int)

        for row in self._query(all_paths, all_criteria, limit=query.limit, type=query.datatype):
            for parent, child in self._pairwise(enumerate(row[1:])):
                source = self._getNodeID(nodes, *parent)
                target = self._getNodeID(nodes, *child)
                edges[(source, target)] += row[0]

        data = {
            "nodes": nodes.values(),
            "edges": [{
                "source": key[0],
                "target": key[1],
                "value": value
            } for key, value in edges.items()]
        }

        return data


class HeatmapChart(statistics.GenericChart):
    TYPES = ["heatmap"]

    @staticmethod
    def _ctime_as_timezone():
        if env.request.user.timezone.zone == "UTC":
            return "{backend}.{time_field}"
        else:
            return "timezone({backend}.{time_field}, '%s')" % (env.request.user.timezone.zone)

    def _get_data(self, units):
        query = self.query[0]
        all_paths, all_criteria = self._prepare_query(query)
        all_paths += ["%s:%s/order_desc,group_by" % (self._ctime_as_timezone(), unit) for unit in units]

        # Adjust the value in order to use it as an index:
        # - Subtract 1 to the "month" value because months are from 1 to 12
        # - Same for the "mday" value, from 1 to 31
        # - Subtract the start year to the "year" value
        adjust = {"year": env.request.menu.start.year, "month": 1, "mday": 1, "wday": 0, "hour": 0, "min": 0}

        for row in self._query(all_paths, all_criteria, type=query.datatype):
            item_data = []
            for value, unit in zip(row[1:], units):
                item_data.append(int(value) - adjust[unit])

            yield RendererItem(row[0], item_data)

    def get_data(self):
        render_mapping = {
            'hour': {
                "units": ("hour", "min"),
                "options": {
                    "ylegend": range(0, 24),
                    "ylabel": _("Hours"),
                    "yalign": True,
                    "xlegend": range(0, 60),
                    "xlabel": _("Minutes"),
                    "xalign": True
                }
            },
            'day': {
                "units": ("wday", "hour"),
                "options": {
                    "ylegend": localization.get_day_names().values(),
                    "ylabel": _("Days"),
                    "yalign": False,
                    "xlegend": range(0, 24),
                    "xlabel": _("Hours"),
                    "xalign": True
                }
            },
            'month': {
                "units": ("month", "mday"),
                "options": {
                    "ylegend": localization.get_month_names().values(),
                    "ylabel": _("Months"),
                    "yalign": False,
                    "xlegend": range(1, 32),
                    "xlabel": _("Days"),
                    "xalign": False
                }
            },
            'year': {
                "units": ("year", "month"),
                "options": {
                    "ylegend": [text_type(i) for i in range(env.request.menu.start.year, env.request.menu.end.year + 1)],
                    "ylabel": _("Years"),
                    "yalign": False,
                    "xlegend": localization.get_month_names().values(),
                    "xlabel": _("Months"),
                    "xalign": False
                }
            }
        }

        vtype = render_mapping[self.options["unit"]]
        self.options.update(vtype["options"])
        return self._get_data(vtype["units"])


class TreemapChart(statistics.DiagramChart):
    TYPES = ["treemap"]

    def __init__(self, chart_type, title, query, **options):
        options["additional_paths"] = query[0].paths[1:]
        query[0].paths = query[0].paths[:1]
        statistics.DiagramChart.__init__(self, chart_type, title, query, **options)

    def _prepare_query(self, query):
        all_paths, all_criteria = statistics.DiagramChart._prepare_query(self, query)
        self.options["base_criteria"] = all_criteria
        return all_paths, all_criteria

    def _get_categories(self, query):
        all_paths, all_criteria = self._prepare_query(query)

        for row in self._query(all_paths, all_criteria, limit=query.limit, type=query.datatype):
            count = row[0]
            series = tuple(row[1:])
            crit = functools.reduce(lambda x, y: x & y, (Criterion(path, '=', row[i + 1])
                                                         for i, path in enumerate(query.paths)))
            yield count, series, crit


class TreemapView(view.View):
    @staticmethod
    def _get_data():
        criteria = json.loads(env.request.parameters["criteria"])
        selpath = env.request.parameters.getlist("selected_path")
        curpath = env.request.parameters.getlist("current_path")
        is_last = (len(curpath) == len(selpath) - 1)
        limit = env.request.parameters.get("limit", 10, type=int)

        for i, value in enumerate(curpath):
            criteria += Criterion(selpath[i], "=", value if value != "n/a" else None)

        for count, val in env.dataprovider.query(["count(1)/order_desc", "%s/group_by" % selpath[len(curpath)]], criteria=criteria, limit=limit):
            yield RendererItem(values=count, series=(val,), links=curpath + [val] if not is_last else None)

    @view.route("/statistics/treemap/update", methods=["POST"])
    def update(self):
        return env.renderer.update("treemap", self._get_data())
