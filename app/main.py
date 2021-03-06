import sys, os
import pickle

sys.path.append(os.path.abspath(os.path.join('..', 'research')))

import bokeh.plotting as bp
import numpy as np
import pandas as pd

from bokeh.core.properties import value
from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup, Div, Slider, Select, Panel, Tabs, DataTable, \
    DateFormatter, TableColumn
from bokeh.palettes import Category10
from datetime import datetime
from functools import partial

from research.dao import DataAccessObject, n_classes

dao = DataAccessObject()

"""
Setup
"""
# Define a results set to view (may be a single subject or a summary)
dao.results_set = dao.get_results_set('mean')

# Create a dictionary to easily associate plots with data sources
plot_source_dict = {}

"""
General plotting functions
"""

no_data_div = Div(text='No data to display!', name='no_data_div')
subject_div = Div(text='', name='subject_div', style={'margin': '20px'})


def plot_slice(plane: str, i_slice: int, class_idx: int):
    """
    Plots a specified slice from the current results set

    :param plane: 'sagittal', 'coronal' or 'horizontal'
    :type plane: str
    :param i_slice: index of the desired slice
    :type i_slice: int
    :param class_idx: index of the cortical class
    :type class_idx: int
    :return: bokeh plot
    """
    slice = dao.get_slice(plane, class_idx, i_slice)
    source = ColumnDataSource(data=dict(image=[slice]))

    # Create plot
    plot = bp.figure(plot_width=slice.shape[1] * 2,
                     plot_height=slice.shape[0] * 2,
                     x_range=[0, slice.shape[1]],
                     y_range=[0, slice.shape[0]],
                     title=f'{plane.capitalize()} View',
                     name=f'class_{class_idx}_{plane}')

    # Add hover tool
    hover = HoverTool(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])
    plot.add_tools(hover)

    # Plot image
    plot.image(image='image', x=0, y=0, dw=slice.shape[1], dh=slice.shape[0],
               source=source, palette='Spectral11', name=f'class_{class_idx}_{plane}_image')

    # Update plot sources dictionary
    plot_source_dict[plot] = source

    return plot


def update_plot(plot) -> None:
    """
    Updates a given plot's data and slice

    :param plot: slice plot
    :type plot: bp.figure.Figure
    """

    # Use plot name to build DAO query
    _, class_idx, plane = plot.name.split('_')

    # Get updated slice
    slice = dao.get_slice(plane, int(class_idx), sliders[plane].value)

    # Get the appropriate data source object from the plot sources dictionary
    source = plot_source_dict[plot]

    # Update the plot source with the new slice image
    source.data = dict(image=[slice])


def create_class_multi_planar_plots(index: dict, class_idx: int) -> list:
    """
    Returns a list of three plots in the three planes at the desired coordinates as defined in the index

    :param index: dictionary of indices for the three planes
    :type index: dict
    :param class_idx: class index
    :type index: int
    :return: list of plots in the three planes at the desired coordinates
    :rtype: list
    """
    return [plot_slice(plane, index[plane], class_idx) for plane in index.keys()]


def plot_multi_planar(i_sagittal: int, i_coronal: int, i_horizontal: int, class_idx: int,
                      with_caption=True):
    """
    Returns a layout of the multi-planar plots at the desired coordinates with or without captions

    :param i_sagittal: slice index
    :type i_sagittal: int
    :param i_coronal: slice index
    :type i_coronal: int
    :param i_horizontal: slice index
    :type i_horizontal: int
    :param class_idx: class index
    :type class_idx: int
    :param with_caption: whether to include a caption or not
    :type with_caption: bool
    :return: Multi-planar plots in a row (returned as column with added captions)
    :rtype: bokeh.layouts.column
    """
    index = {'sagittal': i_sagittal, 'coronal': i_coronal, 'horizontal': i_horizontal}
    class_slices = create_class_multi_planar_plots(index, class_idx)
    plots = row(*class_slices, name=f'class_{class_idx}_plots')
    if with_caption:
        caption = Div(text=f'Class {class_idx+1}')
        plots = column(caption, plots, name=f'class_{class_idx}_figure')
    return plots


def plot_area_across_regions(pbr):
    source_dict = {f'Class {class_idx+1}': pbr.data[:, class_idx] for class_idx in
                   range(pbr.data.shape[1])}
    classes = list((source_dict.keys()))[::-1]
    regions = [str(i) for i in range(1, 1001)]
    source_dict['regions'] = regions
    source = ColumnDataSource(data=source_dict)
    plot = bp.figure(x_range=regions, title='Class Area by AAL Region', plot_width=1500)
    plot.vbar_stack(classes, x='regions', width=0.1,
                    color=['blue', 'red', 'yellow', 'green', 'purple', 'grey'],
                    source=source, legend=[value(x) for x in classes])
    plot.y_range.start = 0
    plot.y_range.end = 1
    plot.yaxis.axis_label = 'Class Probability'
    plot.xaxis.axis_label = 'AAL Region'
    # plot.xaxis[0].ticker.ticks = list(range(0,1001,50))[1:]
    plot.xaxis.visible = False
    plot.legend.location = "top_right"
    csf = Div(text='CSF', style={'text-align': 'center'}, width=1000)
    myelin = Div(text='Myelin', style={'text-align': 'center'}, width=1000)
    result = column(csf, plot, myelin)
    return result


def plot_linear_model_across_regions(measurement: str):
    # Get linear model results dictionary
    source_dict, scores = get_linear_model_results(measurement)

    # Summary div
    n_subjects = len(scores[scores.index.isin([pbr.subject_id for pbr in dao.pbrs])])
    div = Div(text=f'Summary results over {n_subjects} subjects')

    # Create figure
    n_regions = len(source_dict['region'])
    r_plot = bp.figure(x_range=(1, n_regions), name='lm_r_figure', width=1750,
                       title='Quality of Fit')

    # Create R-squared plot
    colors = Category10[10][:2]
    legend_list = ['R-squared', 'Adjusted R-squared']
    x = list(range(1, n_regions + 1))
    ys = [source_dict['rsquared'], source_dict['rsquared_adj']]
    r_plot.xaxis.axis_label = 'AAL Region'
    for color, leg, y in zip(colors, legend_list, ys):
        line = r_plot.line(x, y, line_width=0.5, color=color, legend=leg)
    plot_source_dict[r_plot] = source_dict

    # Create p-values plots
    p_colors = Category10[10][2:]
    p_plots = []
    for class_idx in range(n_classes):
        p_plot = bp.figure(x_range=(1, n_regions), name=f'lm_{class_idx}_p_figure', width=875,
                           title=f'Class {class_idx+1} p-Values')
        p_values = []
        for region_idx in range(n_regions):
            p_values.append(source_dict['corr_pvalues'][region_idx][class_idx])
        p_plot.line(x, p_values, color=p_colors[class_idx])
        p_plot.y_range.start = 0
        p_plot.y_range.end = 1
        p_plot.yaxis.axis_label = 'FDR corr. p-Value'
        p_plot.xaxis.axis_label = 'AAL Region'
        p_plots.append(p_plot)
    p_plots_layout = column(row(*p_plots[:2]), row(*p_plots[2:4]), row(*p_plots[4:]))

    layout = column(div, r_plot, p_plots_layout)
    return layout


def get_linear_model_results(measurement: str):
    if measurement in big_five:
        scores = dao.get_neo_scores(measurement)
    elif measurement in cantab_measures:
        scores = dao.get_cantab_scores(measurement)
    else:
        scores = dao.get_scores(measurement)
    file_name = f'{measurement}_lm_results.pkl'
    file_path = os.path.join('./app/obj', file_name)
    if os.path.isfile(file_path):
        lm_show_message('Loading...', style={'color': 'orange'})
        with open(file_path, 'rb') as f:
            return pickle.load(f), scores
    else:
        lm_show_message('Calculating...', style={'color': 'orange'})
        source_dict = dao.cla.calculate_linear_model_dict(scores)
        with open(file_path, 'wb') as f:
            pickle.dump(source_dict, f, pickle.HIGHEST_PROTOCOL)
        return source_dict, scores


def plot_class_anova(results: pd.DataFrame, class_idx: int):
    x = list(range(1, len(results) + 1))
    metrics = results.columns.tolist()
    colors = Category10[10][:len(metrics)]
    plot = bp.figure(x_range=(1, len(results) + 1), width=875, title=f'Class {class_idx}',
                     name=f'class_{class_idx}_anova')
    for i, metric in enumerate(metrics):
        line = plot.line(x, results[metric].values, color=colors[i], legend=metric,
                         name=f'class_{class_idx}_anova_{metric}')
    plot.y_range.start = 0
    plot.y_range.end = 1
    plot.xaxis.axis_label = 'AAL Region'
    plot.yaxis.axis_label = 'Estimator Value'
    return plot


def plot_anova(categorical_attr: str):
    attribute_values = dao.get_subject_attributes(categorical_attr)
    plots = []
    for class_idx in range(n_classes):
        all_region_results = get_anova_results(class_idx, categorical_attr)
        plots.append(plot_class_anova(all_region_results, class_idx))
    layout = column(row(*plots[:2]), row(*plots[2:4]), row(*plots[4:]))
    return layout


def get_anova_results(class_idx: int, categorical_attr: str):
    file_name = f'{categorical_attr}_{class_idx}_anova_result.pkl'
    file_path = os.path.join('./app/obj', file_name)
    if os.path.isfile(file_path):
        anova_show_message(f'Loading class {class_idx} results...', style={'color': 'orange'})
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    else:
        anova_show_message(f'Calculating class {class_idx+1}...', style={'color': 'orange'})
        attribute_values = dao.get_subject_attributes(categorical_attr)
        results = dao.cla.calculate_anova(class_idx, attribute_values)
        with open(file_path, 'wb') as f:
            pickle.dump(results, f, pickle.HIGHEST_PROTOCOL)
        return results


def create_subject_summary():
    subject_div.text = ''
    subject = dao.chosen_subject
    att_dict = subject.to_dict()
    for att, value in att_dict.items():
        att = att.replace('_', ' ').capitalize()
        subject_div.text += f'{att}: {value}<br />'

    subject_div.text += '<br /><br />'
    subject_div.text += 'Cortical layers results: '
    if hasattr(subject, 'pbr'):
        subject_div.text += 'TRUE'
    else:
        subject_div.text += 'FALSE'

    if hasattr(subject, 'measurements'):
        subject_div.text += '<br /><br /><br />'
        subject_div.text += 'MEASUREMENTS'
        subject_div.text += '<br />'
        df = subject.measurements.df
        dates = df['date'].unique()
        for date in dates:
            formatted_date = datetime.utcfromtimestamp(date.astype(datetime) * 1e-9)
            subject_div.text += f'<br />{formatted_date.date()}<br />'
            current_meas = df.loc[df['date'] == date]
            for i, measurement in current_meas.iterrows():
                value = measurement["value"]
                if value is not np.nan:
                    subject_div.text += f'{measurement["measurement"]}: {value}<br />'


def atlas_show_message(txt: str, style: dict = None):
    atlas_msg_div.text = txt
    atlas_msg_div.style = style


def lm_show_message(txt: str, style: dict = None):
    lm_msg_div.text = txt
    lm_msg_div.style = style


def anova_show_message(txt: str, style: dict = None):
    anova_msg_div.text = txt
    anova_msg_div.style = style


"""
Widgets
"""

# Checkbox to choose which classes to show
classes_checkbox = CheckboxGroup(
    labels=[f'Class {i}' for i in range(1, n_classes + 1)])


def update_visible_classes(attr, old, new):
    if not dao.results_set:
        return
    root_layout = curdoc().get_model_by_name('all_class_figures')
    sublayouts = root_layout.children
    for class_idx in range(n_classes):
        existing_figure = curdoc().get_model_by_name(f'class_{class_idx}_figure')
        if class_idx in classes_checkbox.active:
            if not existing_figure:
                sublayouts.append(
                    plot_multi_planar(sagittal_slice_slider.value, coronal_slice_slider.value,
                                      horizontal_slice_slider.value, class_idx))
        else:
            if existing_figure:
                sublayouts.remove(existing_figure)


classes_checkbox.on_change('active', update_visible_classes)

atlas_msg_div = Div(text='', name='atlas_message')
lm_msg_div = Div(text='', name='lm_message')
anova_msg_div = Div(text='', name='anova_message')

# Select menu to choose the displayed results set (single subject or summary)
options = ['mean'] + [str(subject) for subject in dao.subjects if hasattr(subject, 'pbr')]
select = Select(title="Results set", value="mean", options=options)


def change_results_set(attr, old, new):
    set_id = select.value
    if set_id not in ['mean']:
        set_id = set_id[-9:]
    atlas_show_message(f'Loading results for subject {select.value}...', style={'color': 'orange'})
    dao.results_set = dao.get_results_set(set_id)
    if not dao.results_set:
        atlas_show_message(f'Could not find results for {select.value}!', style={'color': 'red'})
        return
    else:
        atlas_show_message(f'Displaying reults for {select.value}', style={'color': 'green'})
        for class_idx in classes_checkbox.active:
            for plane in ('sagittal', 'coronal', 'horizontal'):
                existing_plot = curdoc().get_model_by_name(f'class_{class_idx}_{plane}')
                update_plot(existing_plot)


select.on_change('value', change_results_set)

# Sliders for slice changing
if dao.results_set:
    sample_img = dao.results_set[0].data
else:
    sample_img = np.zeros((1, 1, 1))
sagittal_slice_slider = Slider(start=1, end=sample_img.shape[0], value=1, step=1,
                               title='Sagittal Slice')
coronal_slice_slider = Slider(start=1, end=sample_img.shape[1], value=1, step=1,
                              title='Coronal Slice')
horizontal_slice_slider = Slider(start=1, end=sample_img.shape[2], value=1, step=1,
                                 title='Horizontal Slice')

# Sliders dictionary for accessibility
sliders = {'sagittal': sagittal_slice_slider, 'coronal': coronal_slice_slider,
           'horizontal': horizontal_slice_slider}


def change_slice(attr, old, new, plane: str):
    if not dao.results_set:
        return
    for class_idx in classes_checkbox.active:
        existing_plot = curdoc().get_model_by_name(f'class_{class_idx}_{plane}')
        update_plot(existing_plot)


sagittal_slice_slider.on_change('value', partial(change_slice, plane='sagittal'))
coronal_slice_slider.on_change('value', partial(change_slice, plane='coronal'))
horizontal_slice_slider.on_change('value', partial(change_slice, plane='horizontal'))

# Subjects table

subjects_df = dao.get_subject_attributes_df()
subjects_data = dict(subjects_df)
subjects_data['id'] = subjects_df.index
subjects_source = ColumnDataSource(subjects_data)
columns = [
    TableColumn(field="id", title="ID"),
    TableColumn(field="name_id", title="Name ID"),
    TableColumn(field="sex", title="Sex"),
    TableColumn(field="date_of_birth", title="Date of Birth",
                formatter=DateFormatter(format='%d/%m/%Y')),
]
subjects_table = DataTable(source=subjects_source, columns=columns, width=600, height=900)


def change_subject_view(attr, old, new):
    subject_id = subjects_source.data['id'][subjects_source.selected.indices[0]]
    subject_id = str(subject_id).zfill(9)
    dao.chosen_subject = dao.get_subject_by_id(subject_id)
    create_subject_summary()


subjects_source.on_change('selected', change_subject_view)

# ANOVA attribute select
categorical_attributes = ['sex', 'dominant_hand']
anova_categorical_select = Select(title='Group by', value='sex', options=categorical_attributes)


def update_anova_attribute(attr, old, new):
    anova_layout.children[1] = plot_anova(anova_categorical_select.value)
    anova_show_message('Ready!', style={'color': 'green'})


anova_categorical_select.on_change('value', update_anova_attribute)

# ANOVA statistic checkboxgroup
statistics = ['F', 'p']
anova_statistic_cb = CheckboxGroup(labels=statistics, active=[0, 1])


def update_visible_statistics(attr, old, new):
    for statistic in anova_statistic_cb.labels:
        show_bool = statistics.index(statistic) in anova_statistic_cb.active
        for class_idx in range(n_classes):
            line = curdoc().get_model_by_name(f'class_{class_idx}_anova_{statistic}')
            line.visible = show_bool


anova_statistic_cb.on_change('active', update_visible_statistics)

# Linear model attribute select
big_five = ['agreeableness', 'conscientiousness', 'extraversion', 'neuroticism', 'openness']
cantab_measures = ['DMSMDLAD', 'DMSPC', 'PALFAMS', 'PALTEA', 'RTIFMDRT', 'RTIFMMT', 'RVPA',
                   'RVPMDL', 'SWMBE', 'SWMS']
measurements = ['height', 'weight', 'age'] + big_five + cantab_measures
lm_measurement_select = Select(title='Measurement', value='age', options=measurements)


def update_lm_measurement(attr, old, new):
    lm_layout.children[1] = plot_linear_model_across_regions(lm_measurement_select.value)
    lm_show_message('Ready!', style={'color': 'green'})


lm_measurement_select.on_change('value', update_lm_measurement)

"""
Create layout and set as document root
"""

# Subjects tab
subjects_row = row(subjects_table, subject_div)
subjects_tab = Panel(child=subjects_row, title='Subjects')

# Statistical summary tab
area_plot = plot_area_across_regions(dao.cla.mean_pbr)
summary_stats_tab = Panel(child=area_plot, title="Summary Statistics")

# Atlas projection tab
all_class_figures = column(name='all_class_figures')
control = widgetbox(select, classes_checkbox, sagittal_slice_slider, coronal_slice_slider,
                    horizontal_slice_slider, atlas_msg_div, name='figure_control')
final = row(control, all_class_figures, name='main_layout')
atlas_tab = Panel(child=final, title='Atlas Projection')

# ANOVA tab
anova_plot = plot_anova(anova_categorical_select.value)
anova_show_message('Ready!', style={'color': 'green'})
anova_control = column(row(widgetbox(anova_categorical_select), widgetbox(anova_statistic_cb)), anova_msg_div,
                          name='anova_control')
anova_layout = column(anova_control, anova_plot, name='anova_layout')
anova_tab = Panel(child=anova_layout, title='ANOVA')

# Linear model tab
lm_plot = plot_linear_model_across_regions(lm_measurement_select.value)
lm_show_message('Ready!', style={'color': 'green'})
lm_control = widgetbox(lm_measurement_select, lm_msg_div, name='lm_control')
lm_layout = column(lm_control, lm_plot, name='lm_layout')
lm_tab = Panel(child=lm_layout, title='Linear Models')

tabs = Tabs(tabs=[subjects_tab, summary_stats_tab, atlas_tab, anova_tab, lm_tab])

curdoc().add_root(tabs)
