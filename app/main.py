import bokeh.plotting as bp
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup, Div, Slider
from functools import partial

from helpers import AllClassAALHandler

data = np.load('/home/flavus/PycharmProjects/cortical_layers/app/all_class_means_aal.npy')

# Create an image wrapper object to easily generate slices
aal_handler = AllClassAALHandler(data)

# Create a dictionary to easily associate plots with data sources
plot_source_dict = {}


def plot_slice(plane: str, i_slice: int, cortical_class: int):
    """
    A function to plot a specified slice from the all classes AAL handler

    :param plane: 'sagittal', 'coronal' or 'horizontal'
    :type plane: str
    :param i_slice: index of the desired slice
    :type i_slice: int
    :param cortical_class: index of the cortical class
    :type cortical_class: int
    :return: bokeh plot
    """
    slice = aal_handler.get_slice(plane, i_slice, cortical_class)
    source = ColumnDataSource(data=dict(image=[slice]))

    plot = bp.figure(plot_width=slice.shape[1] * 2,
                     plot_height=slice.shape[0] * 2,
                     x_range=[0, slice.shape[1]],
                     y_range=[0, slice.shape[0]],
                     title=f'{plane.capitalize()} View',
                     name=f'class_{cortical_class}_{plane}')
    hover = HoverTool(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])
    plot.add_tools(hover)
    plot.image(image='image', x=0, y=0, dw=slice.shape[1], dh=slice.shape[0],
               source=source, palette='Spectral11', name=f'class_{cortical_class}_{plane}_image')
    plot_source_dict[plot] = source
    return plot


def update_plot_slice(plot: bp.figure.Figure, i_slice: int) -> None:
    """
    A function to update a given plot's displayed slice

    :param plot:
    :type plot: bp.figure.Figure
    :param i_slice: index of the desired slice
    :type i_slice: int
    """
    _, cortical_class, plane = plot.name.split('_')
    slice = aal_handler.get_slice(plane, int(i_slice), int(cortical_class))
    source = plot_source_dict[plot]
    source.data = dict(image=[slice])


def plot_multi_planar(i_sagittal_slice: int, i_coronal_slice: int,
                      i_horizontal_slice: int, cortical_class: int):
    slice_index = {'sagittal': i_sagittal_slice,
                   'coronal': i_coronal_slice,
                   'horizontal': i_horizontal_slice}
    plots = row(
        *[plot_slice(plane, slice_index[plane], cortical_class) for plane in slice_index.keys()],
        name=f'class_{cortical_class}_plots')
    caption = Div(text=f'Class {cortical_class+1}')
    plots_with_caption = column(caption, plots, name=f'class_{cortical_class}_figure')
    return plots_with_caption


classes_checkbox = CheckboxGroup(
    labels=[f'Class {i}' for i in range(1, aal_handler.n_classes + 1)])


def update_visible_classes(attr, old, new):
    root_layout = curdoc().get_model_by_name('all_class_figures')
    sublayouts = root_layout.children
    for cortical_class in range(aal_handler.n_classes):
        existing_figure = curdoc().get_model_by_name(f'class_{cortical_class}_figure')
        if cortical_class in classes_checkbox.active:
            if not existing_figure:
                sublayouts.append(
                    plot_multi_planar(sagittal_slice_slider.value, coronal_slice_slider.value,
                                      horizontal_slice_slider.value, cortical_class))
        else:
            if existing_figure:
                sublayouts.remove(existing_figure)


classes_checkbox.on_change('active', update_visible_classes)

sagittal_slice_slider = Slider(start=1, end=aal_handler.image.shape[0], value=0, step=1,
                               title='Sagittal Slice')
coronal_slice_slider = Slider(start=1, end=aal_handler.image.shape[1], value=0, step=1,
                              title='Coronal Slice')
horizontal_slice_slider = Slider(start=1, end=aal_handler.image.shape[2], value=0, step=1,
                                 title='Horizontal Slice')
sliders = {'sagittal': sagittal_slice_slider, 'coronal': coronal_slice_slider,
           'horizontal': horizontal_slice_slider}


def change_slice(attr, old, new, plane: str):
    slider = sliders[plane]
    for cortical_class in classes_checkbox.active:
        existing_plot = curdoc().get_model_by_name(f'class_{cortical_class}_{plane}')
        update_plot_slice(existing_plot, slider.value - 1)


sagittal_slice_slider.on_change('value', partial(change_slice, plane='sagittal'))
coronal_slice_slider.on_change('value', partial(change_slice, plane='coronal'))
horizontal_slice_slider.on_change('value', partial(change_slice, plane='horizontal'))

all_class_figures = column(name='all_class_figures')
final = row(widgetbox(classes_checkbox, sagittal_slice_slider, coronal_slice_slider,
                      horizontal_slice_slider), all_class_figures,
            name='main_layout')

curdoc().add_root(final)
