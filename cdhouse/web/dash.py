import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from sqlalchemy import func

from cdhouse.web.extensions import db
from cdhouse.web.models import CdHouseModel


def get_region_projects():
    """按市县分组楼盘数"""
    rows = db.session.query(CdHouseModel.region,
                            func.count(CdHouseModel.project_uuid)).group_by(
                                CdHouseModel.region).all()
    return zip(*rows)


def get_region_houses():
    """按市县分组房子套数"""

    rows = db.session.query(
        CdHouseModel.region,
        func.sum(CdHouseModel.houses).label('house_number')).group_by(
            CdHouseModel.region).order_by(db.desc('house_number')).all()
    return zip(*rows)


def get_projects_by_date():
    """按日期统计楼盘数"""
    rows = db.session.query(
        func.date(CdHouseModel.start_time).label('date'),
        func.count(CdHouseModel.project_uuid)).group_by('date')
    return zip(*rows)


def get_open_project_by_region():
    """获取当前各市县在售楼盘数"""
    rows = db.session.query(
        CdHouseModel.region,
        func.count(CdHouseModel.project_uuid).label('project_number')).filter(
            CdHouseModel.status != '报名结束').group_by(
                CdHouseModel.region).order_by(db.desc('project_number')).all()
    return zip(*rows)


def get_layout():
    return html.Div(children=[
        html.H1(children='成都房协商品住房数据统计', id='pie-title'),
        dcc.Graph(id='open-project-bar'),
        dcc.Graph(id='region-pie'),
        dcc.Graph(id='house-bar'),
        dcc.Graph(id='project-line')
    ])


def config_dash(dash_app):
    # 设置页面标题
    dash_app.title = '成都房协商品住房数据统计'
    # 设置页面布局
    dash_app.layout = get_layout()

    @dash_app.callback(
        Output('region-pie', 'figure'), [Input('pie-title', 'id')])
    def update_region_pie(input_value):
        regions, projects_number = get_region_projects()
        return go.Figure(
            data=[
                go.Pie(
                    labels=regions,
                    values=projects_number,
                    hole=0.3,
                    hoverinfo='label+percent',
                    textinfo='value',
                )
            ],
            layout={
                "title": "各市县楼盘数总数",
            })

    @dash_app.callback(
        Output('house-bar', 'figure'), [Input('pie-title', 'id')])
    def update_region_pie(input_value):
        regions, houses = get_region_houses()
        return go.Figure(
            data=[
                go.Bar(
                    x=regions,
                    y=houses,
                    text=houses,
                    textposition='auto',
                    hoverinfo='text',
                    name='房子套数',
                    marker=dict(
                        color='rgb(158,202,225)',
                        line=dict(color='rgb(8,48,107)', width=1.5),
                    ),
                    opacity=0.6),
            ],
            layout=go.Layout(title='各市县房子总套数'))

    @dash_app.callback(
        Output('open-project-bar', 'figure'), [Input('pie-title', 'id')])
    def update_region_pie(input_value):
        regions, projects = get_open_project_by_region()
        return go.Figure(
            data=[
                go.Bar(
                    x=regions,
                    y=projects,
                    text=projects,
                    textposition='auto',
                    hoverinfo='text',
                    name='楼盘数',
                    opacity=0.6,
                    marker=dict(
                        color='rgb(158,202,225)',
                        line=dict(color='rgb(8,48,107)', width=1.5),
                    ),
                ),
            ],
            layout=go.Layout(title='各市县在售楼盘数'))

    @dash_app.callback(
        Output('project-line', 'figure'), [Input('pie-title', 'id')])
    def update_region_pie(input_value):
        dates, projects = get_projects_by_date()
        return go.Figure(
            data=[go.Scatter(
                x=dates,
                y=projects,
            )],
            layout=go.Layout(
                title='楼盘开盘走势',
                xaxis={'tickformat': '%Y-%m-%d'},
            ))
