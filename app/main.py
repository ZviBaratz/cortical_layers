import bokeh.plotting as bp

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup, Div, Slider, Select
from functools import partial

from dao import DataAccessObject, n_classes

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


"""
Widgets
"""

# Checkbox to choose which classes to show
classes_checkbox = CheckboxGroup(
    labels=[f'Class {i}' for i in range(1, n_classes + 1)])


def update_visible_classes(attr, old, new):
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
    set_id = select.value.replace('/', '')
    dao.results_set = dao.get_results_set(set_id)
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
    for class_idx in classes_checkbox.active:
        existing_plot = curdoc().get_model_by_name(f'class_{class_idx}_{plane}')
        update_plot(existing_plot)


sagittal_slice_slider.on_change('value', partial(change_slice, plane='sagittal'))
coronal_slice_slider.on_change('value', partial(change_slice, plane='coronal'))
horizontal_slice_slider.on_change('value', partial(change_slice, plane='horizontal'))

"""
Create layout and set as document root
"""
all_class_figures = column(name='all_class_figures')
final = row(widgetbox(select, classes_checkbox, sagittal_slice_slider, coronal_slice_slider,
                      horizontal_slice_slider), all_class_figures,
            name='main_layout')

curdoc().add_root(final)
