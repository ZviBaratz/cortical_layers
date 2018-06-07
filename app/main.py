import bokeh.plotting as bp

from bokeh.core.properties import value
from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup, Div, Slider, Select, Panel, Tabs, DataTable, \
    DateFormatter, TableColumn
from functools import partial

from dao import DataAccessObject
from cfg import n_classes

"""
Setup
"""
# Create a DAO to easily access analysis results
dao = DataAccessObject()

# Define a results set to view (may be a single subject or a summary)
dao.results_set = dao.summary.get_all_class_means()

# Create a dictionary to easily associate plots with data sources
plot_source_dict = {}

"""
General plotting functions
"""

no_data_div = Div(text=f'No data to display!', name='no_data_div')
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
    source_dict = {f'Class {class_idx+1}': pbr[:, class_idx] for class_idx in range(pbr.shape[1])}
    classes = list((source_dict.keys()))[::-1]
    regions = [str(i) for i in range(1, 1001)]
    source_dict['regions'] = regions
    source = ColumnDataSource(data=source_dict)
    plot = bp.figure(x_range=regions, title='Class Area by AAL Region', plot_width=1000,
                     toolbar_location=None, tools="")
    plot.vbar_stack(classes, x='regions', width=0.1,
                    color=['blue', 'red', 'yellow', 'green', 'purple', 'grey'],
                    source=source, legend=[value(x) for x in classes])
    plot.y_range.start = 0
    plot.y_range.end = 1
    plot.yaxis.axis_label = 'Class Probability'
    plot.xaxis.axis_label = 'AAL Region'
    # plot.xaxis[0].ticker.ticks = list(range(0,1001,50))[1:]
    plot.legend.location = "top_right"
    csf = Div(text='CSF', style={'text-align': 'center'}, width=1000)
    myelin = Div(text='Myelin', style={'text-align': 'center'}, width=1000)
    result = column(csf, plot, myelin)
    return result

def create_subject_summary():
    subject_div.text = ''
    subject = dao.selected_subject
    attributes = ['id', 'name_id', 'sex', 'gender', 'date_of_birth', 'dominant_hand']
    for att in attributes:
        value = getattr(subject, att)
        subject_div.text += f'{att}: {value}<br />'


def show_no_data_div():
    root_layout = curdoc().get_model_by_name('all_class_figures')
    sublayouts = root_layout.children
    sublayouts.append(no_data_div)


def remove_no_data_div():
    div = curdoc().get_model_by_name('no_data_div')
    if div:
        root_layout = curdoc().get_model_by_name('all_class_figures')
        sublayouts = root_layout.children
        sublayouts.remove(no_data_div)


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

# Select menu to choose the displayed results set (single subject or summary)
options = ['mean'] + [str(subject) for subject in dao.subjects]
select = Select(title="Results set:", value="mean", options=options)


def change_results_set(attr, old, new):
    set_id = select.value
    if set_id not in ['mean']:
        set_id = set_id[-9:]
    print('\nLooking for:\t' + set_id)
    dao.results_set = dao.get_results_set(set_id)
    print('Results set successfully loaded!')
    if not dao.results_set:
        show_no_data_div()
    else:
        remove_no_data_div()
        for class_idx in classes_checkbox.active:
            for plane in ('sagittal', 'coronal', 'horizontal'):
                existing_plot = curdoc().get_model_by_name(f'class_{class_idx}_{plane}')
                update_plot(existing_plot)


select.on_change('value', change_results_set)

# Sliders for slice changing
sample_img = dao.results_set[0].data
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


"""
Create layout and set as document root
"""

subjects_data = dict(dao.subjects_df[['Name ID', 'Sex', 'Date of Birth']])
subjects_data['id'] = dao.subjects_df.index
source = ColumnDataSource(subjects_data)
columns = [
    TableColumn(field="Name ID", title="Name ID"),
    TableColumn(field="Sex", title="Sex"),
    TableColumn(field="Date of Birth", title="Date of Birth",
                formatter=DateFormatter(format='%d/%m/%Y')),
]
subjects_table = DataTable(source=source, columns=columns, width=600, height=900)

def change_subject_view(attr, old, new):
    subject_id = source.data['id'][source.selected.indices[0]]
    subject_id = str(subject_id).zfill(9)
    dao.selected_subject = dao.get_subject_by_id(subject_id)
    create_subject_summary()

source.on_change('selected', change_subject_view)

subjects_row = row(subjects_table, subject_div)
subjects_tab = Panel(child=subjects_row, title='Subjects')

area_plot = plot_area_across_regions(dao.summary.mean_pbr)
summary_stats_tab = Panel(child=area_plot, title="Summary Statistics")

all_class_figures = column(name='all_class_figures')
final = row(widgetbox(select, classes_checkbox, sagittal_slice_slider, coronal_slice_slider,
                      horizontal_slice_slider), all_class_figures, name='main_layout')
atlas_tab = Panel(child=final, title='Atlas Projection')
tabs = Tabs(tabs=[subjects_tab, summary_stats_tab, atlas_tab])

curdoc().add_root(tabs)
