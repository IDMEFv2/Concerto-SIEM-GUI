from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import datetime
import sys

from prewikka import database, error, hookmanager, localization, mainmenu, template, utils, view
from prewikka.utils import json
from prewikka.views.statistics.statistics import GenericStats, Widget

from . import charts


_AGGREGATIONS = [
    ("count", N_("count"), None),
    ("count_distinct", N_("count (distinct)"), None),
    ("avg", N_("average"), (int, float)),
    ("min", N_("minimum"), (int, float)),
    ("max", N_("maximum"), (int, float)),
    ("sum", N_("sum"), (int, float)),
]


class DashboardChartCategory(object):
    icon = None
    label = None
    description = None
    template = template.PrewikkaTemplate(__name__, "templates/widgetedition.mak")
    query = True
    aggregation = True
    grouping = True
    filterable = True

    @classmethod
    def is_enabled(cls):
        return True

    @classmethod
    def prepare_edit(cls, widget):
        return {
            "graphtypes": [typ for typ in GenericStats.get_chart_classes()[widget["category"]].TYPES if typ in env.renderer.get_types()],
            "datatypes": [(typ, env.dataprovider.get_label(typ)) for typ in sorted(env.dataprovider.get_types(public=True))],
            "aggregtypes": _AGGREGATIONS,
            "mainmenu": cls._get_menu(widget)
        }

    @classmethod
    def prepare_render(cls, widget):
        return False

    @staticmethod
    def _get_menu(widget):
        parameters = dict(env.request.menu_parameters)
        period = widget.get("period")

        if not period:
            parameters["timeline_mode"] = ""
            parameters["timeline_value"] = 0
            parameters["timeline_unit"] = "month"
            parameters["timeline_offset"] = 0
        else:
            for key, value in period.items():
                parameters["timeline_%s" % key] = value

        for param in ("filter", "datasource"):
            parameters[param] = widget.get(param)

        return mainmenu.HTMLMainMenu(parameters=parameters, refresh=False, period_optional=True, inline=False, label_width=3)


class DashboardChronology(DashboardChartCategory):
    icon = "fa-line-chart"
    label = N_("Chronology")
    description = N_("A temporal representation of the data.")
    template = template.PrewikkaTemplate(__name__, "templates/chronology.mak")


class DashboardDiagram(DashboardChartCategory):
    icon = "fa-pie-chart"
    label = N_("Diagram")
    description = N_("A representation of data by categories.")
    template = template.PrewikkaTemplate(__name__, "templates/diagram.mak")


class DashboardFlux(DashboardChartCategory):
    icon = "fa-random"
    label = N_("Flux")
    description = N_("A representation of data by flux.")
    template = template.PrewikkaTemplate(__name__, "templates/diagram.mak")


class DashboardHeatmap(DashboardChartCategory):
    icon = "fa-thermometer"
    label = N_("Heatmap")
    description = N_("A temporal representation of data by color gradients.")
    template = template.PrewikkaTemplate(__name__, "templates/heatmap.mak")
    grouping = False


class DashboardListing(DashboardChartCategory):
    icon = "fa fa-table"
    label = N_("Listing")
    description = N_("A tabular representation of the data.")
    aggregation = False


class DashboardMetric(DashboardChartCategory):
    icon = "fa-calculator"
    label = N_("Metric")
    description = N_("A numeric representation of the data.")
    template = template.PrewikkaTemplate(__name__, "templates/metric.mak")
    grouping = False


class DashboardMap(DashboardChartCategory):
    icon = "fa-map-o"
    label = N_("Map")
    description = N_("A geographical representation of the data.")
    query = False
    aggregation = False
    grouping = False


class DashboardTreemap(DashboardChartCategory):
    icon = "fa-tree"
    label = N_("Treemap")
    description = N_("A hierarchical representation of the data.")
    template = template.PrewikkaTemplate(__name__, "templates/diagram.mak")


class DashboardView(DashboardChartCategory):
    icon = "fa-eye"
    label = N_("View")
    description = N_("An embedded view.")
    template = template.PrewikkaTemplate(__name__, "templates/view.mak")
    query = False
    aggregation = False
    grouping = False
    filterable = False

    @classmethod
    def is_enabled(cls):
        return any(obj.options for obj in cls._get_views())

    @classmethod
    def prepare_edit(cls, widget):
        return {"viewlist": cls._get_views()}

    @classmethod
    def prepare_render(cls, widget):
        return {"url": url_for(widget["view"], _default=None, **widget.get("parameters", {}))}

    @staticmethod
    def _get_views():
        view_filter = {
            "included_section": ["Behavioral"],
            "excluded_view": ["Heatmap", "Sankey", "Treemap", "Volumetry"]
        }
        for name, tabs in env.menumanager.get_sections().items():
            # Remove this condition to allow the addition of all the views
            if name not in view_filter["included_section"]:
                continue

            section_select = utils.AttrObj(group_label=N_(name), options=[])

            for view_name, (endpoint, kwargs) in tabs.items():
                if view_name in view_filter["excluded_view"]:
                    continue

                section_select.options.append(utils.AttrObj(value=endpoint, label=N_(view_name)))

            yield section_select


class DashboardImage(DashboardChartCategory):
    icon = "fa-image"
    label = N_("Image")
    description = N_("An external image.")
    template = template.PrewikkaTemplate(__name__, "templates/image.mak")
    query = False
    aggregation = False
    grouping = False
    filterable = False

    @classmethod
    def prepare_edit(cls, widget):
        return {}

    @classmethod
    def prepare_render(cls, widget):
        return True


def is_virtual_view():
    return hasattr(env.request.view, "_virtual")


class WidgetDatabase(database.DatabaseHelper):
    def _where(self, user=True, view=True, uid=True):
        where = []

        if user:
            where.append("userid = %(user)s")
        if view:
            where.append("view = %(view)s")
        if uid:
            where.append("id = %(id)s")

        return "" if not where else " WHERE %s" % " AND ".join(where)

    def get(self, user, view=None, uid=None, **kwargs):
        result = self.query("SELECT id, config FROM Prewikka_Widget %s" % (self._where(not is_virtual_view(), view, uid)), user=user.id, view=view, id=uid)
        return [Widget(wparam, id_=wid, **kwargs) for wid, wparam in result]

    def create(self, user, view, widget):
        self.query("INSERT INTO Prewikka_Widget (userid, view, id, config) VALUES (%s, %s, %s, %s)",
                   user.id, view, widget["id"], widget.to_db())

    def update(self, user, view, widget):
        try:
            dbwidget = self.get(user, view, widget['id'])[0]
        except IndexError:
            return

        dbwidget.update(widget)
        self.query("UPDATE Prewikka_Widget SET config=%(wparam)s" + self._where(not is_virtual_view()),
                   id=widget['id'], view=view, user=user.id, wparam=dbwidget.to_db())

    def delete(self, user, view=None, uid=None):
        self.query("DELETE FROM Prewikka_Widget" + self._where(user, view, uid), id=uid, view=view, user=user.id)


class Dashboard(GenericStats):
    view_template = template.PrewikkaTemplate(__name__, "templates/dashboard.mak")

    edition_enabled = True
    _mainmenu_options = {}

    def __init__(self):
        GenericStats.__init__(self)
        self._widget_api = WidgetDatabase()
        chart_types = {
            "flux": charts.FluxChart,
            "heatmap": charts.HeatmapChart,
            "listing": charts.ListingChart,
            "map": charts.MapChart,
            "metric": charts.MetricChart,
            "treemap": charts.TreemapChart,
        }
        for item in chart_types.items():
            hookmanager.register("HOOK_CHART_CLASSES", item)

        widget_categories = collections.OrderedDict([
            ("chronology", DashboardChronology),
            ("diagram", DashboardDiagram),
            ("flux", DashboardFlux),
            ("heatmap", DashboardHeatmap),
            ("listing", DashboardListing),
            ("metric", DashboardMetric),
            ("map", DashboardMap),
            ("treemap", DashboardTreemap),
            ("view", DashboardView),
            ("image", DashboardImage)
        ])
        for item in widget_categories.items():
            hookmanager.register("HOOK_WIDGET_CATEGORIES", item, _order=0)

    def get_chart_infos(self, endpoint):
        return sorted(self._widget_api.get(env.request.user, endpoint), key=lambda w: (w["y"], w["x"]))

    @property
    def editable(self):
        return self._get_owner() == env.request.user

    def _get_owner(self):
        return env.request.view._virtual.owner if is_virtual_view() else env.request.user

    def _get_endpoint(self):
        return env.request.view._virtual.endpoint if is_virtual_view() else env.request.view.view_endpoint

    def _get_name(self):
        return env.request.view._virtual.name if is_virtual_view() else env.request.view.view_menu[1]

    def _get_graph(self, widget, **options):
        widget["width"] = int(widget["realwidth"])
        widget["height"] = int(widget["realheight"])

        for graph in self.get_graphs([widget], **options):
            ret = {"title": graph["title"]}
            ret.update(graph["rendering"])
            return ret

    def _update_widgets(self):
        for widget in json.loads(env.request.parameters["widgets"]):
            self._widget_api.update(env.request.user, self._get_endpoint(), widget)

    def _load_widget(self):
        widget = Widget(env.request.parameters["widget"])

        if "save" in widget and self.editable:
            widget.pop('save')

            if "reload" in widget:
                widget.pop("reload")
                self._widget_api.update(env.request.user, self._get_endpoint(), widget)
            else:
                self._widget_api.create(env.request.user, self._get_endpoint(), widget)

        elif "reload" in widget:
            widget.update(self._widget_api.get(env.request.user, self._get_endpoint(), widget["id"])[0])

        categories = Widget.get_categories()
        if widget["category"] not in categories:
            raise error.PrewikkaUserError(N_("Invalid widget"), N_("The widget category does not exist"))

        data = categories[widget["category"]].prepare_render(widget)
        if data:
            return data

        options = {}
        if not self.editable:
            options["owner"] = self._get_owner()

        data = self._get_graph(widget, **options)

        if widget.get("period") and widget["category"] != "chronology":
            dictperiod = dict(('timeline_' + k, v) for k, v in widget["period"].items())
            period = mainmenu.TimePeriod(dictperiod)

            data["period_display"] = {
                "start": localization.format_datetime(period.start),
                "end": localization.format_datetime(period.end)
            }

        if widget.get("filter"):
            data["filter"] = widget.get("filter")

        return data

    def is_edition_enabled(self):
        return self.editable and self.edition_enabled

    def setup(self, dataset):
        GenericStats.setup(self, dataset)

        if "load" in env.request.parameters:
            return self._load_widget()

        elif self.editable and "editable" in env.request.parameters:
            env.request.user.set_property("editable", int(env.request.parameters["editable"]), view=self._get_endpoint())
            return True

        elif "export" in env.request.parameters:
            today = datetime.date.today()
            with utils.mkdownload("dashboard_%s_%s.json" % (self._get_name().lower(), today)) as dl:
                dl.write(json.dumps(self._widget_api.get(env.request.user, self._get_endpoint(), set_id=False), indent=4))

            return dl

        self.edition_enabled = bool(env.request.user.get_property("editable", view=self._get_endpoint(), default=self.edition_enabled))
        if self.edition_enabled:
            if "reset" in env.request.parameters:
                self._widget_api.delete(env.request.user, self._get_endpoint())
                return True

            elif "update" in env.request.parameters:
                self._update_widgets()
                return True

            elif "destroy" in env.request.parameters:
                self._widget_api.delete(env.request.user, self._get_endpoint(), env.request.parameters["destroy"])
                return True

        widget_html = self.widget_template.render()
        charts = self._widget_api.get(env.request.user, self._get_endpoint(), raw=False)

        dataset.update({
            "limit": env.request.parameters["limit"],
            "categories": collections.OrderedDict((k, v) for k, v in Widget.get_categories().items() if k != "text"),
            "options": {
                "charts": charts,
                "default_charts": next(hookmanager.trigger("HOOK_DASHBOARD_DEFAULT_GRAPHS"), []) if self.editable else [],
                "widget_html": widget_html,
                "edit_mode": self.is_edition_enabled(),
                "editable": self.editable,
            },
        })

        # Force the display of the control menu
        env.request.has_menu = True

    def draw(self):
        dataset = self.view_template.dataset()
        data = self.setup(dataset)
        if data:
            return data

        return view.ViewResponse(dataset.render(), menu=mainmenu.HTMLMainMenu(**self._mainmenu_options))


class WidgetEdition(view.View):
    view_help = "#widgetedition"

    def __init__(self):
        view.View.__init__(self)
        self._widget_api = WidgetDatabase()

    @view.route("/dashboard/new")
    @view.route("/dashboard/<widget_id>/edit")
    def edit(self, widget_id=None):
        dataset = {"widget": {}}

        if not widget_id:
            dataset["widget"]["category"] = env.request.parameters["category"]
            return self._edit(dataset)

        try:
            widget = dataset["widget"] = self._widget_api.get(env.request.user, uid=widget_id)[0]
        except IndexError:
            raise error.PrewikkaUserError(N_("Invalid widget"), N_("The widget does not exist"))

        if widget["category"] not in Widget.get_categories():
            raise error.PrewikkaUserError(N_("Invalid widget"), N_("The widget category does not exist"))

        return self._edit(dataset)

    def _edit(self, dataset):
        category = dataset["widget"]["category"]

        dataset["category"] = category
        dataset["categories"] = Widget.get_categories()
        dataset.update(dataset["categories"][category].prepare_edit(dataset["widget"]))

        return dataset["categories"][category].template.render(**dataset)


class GeneralDashboard(Dashboard):
    edition_enabled = False

    def __init__(self):
        Dashboard.__init__(self)
        self.chart_infos = []

    @view.route("/dashboard/general", methods=["GET", "POST"], menu=(N_("Dashboard"), N_("General")), label=N_("Dashboard"), keywords=["inheritable"], help="#dashboard")
    def render(self):
        return self.draw()

    @hookmanager.register("HOOK_REPORTING_TEMPLATE")
    def _report(self):
        return utils.AttrObj(
            charts=self.get_chart_infos("generaldashboard.render"),
            label=N_("General"),
            description=N_("This report presents user-defined statistics."),
            permissions=[]
        )

    @hookmanager.register("HOOK_WIDGET_INIT")
    def _init_widget(self, widget):
        try:
            widget_category = Widget.get_categories()[widget["category"]]
        except KeyError:
            return False

        return widget_category.query

    @hookmanager.register("HOOK_VIEW_VIEWEDITION.DELETE_RESPONSE")
    def _delete_view(self, resp):
        for i in env.request.parameters.getlist("id"):
            self._widget_api.delete(env.request.user, "dynview-%s" % i)
