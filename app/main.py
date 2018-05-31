import bokeh.plotting as bp
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import gridplot, widgetbox
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import Slider

from helpers import AllClassAALHandler

data = np.load('/home/flavus/PycharmProjects/cortical_layers/app/all_class_means_aal.npy')

# Create an image wrapper object to easily generate slices
aal_handler = AllClassAALHandler(data)
i_sagittal_slice = 100
i_coronal_slice = 100
i_horizontal_slice = 100
cortical_class = 1
sources = aal_handler.get_columndatasources_by_coords(i_sagittal_slice,
                                                      i_coronal_slice,
                                                      i_horizontal_slice,
                                                      cortical_class)

# Create an info paragraph next to the image
# info_div = image.create_slice_info_div(start_slice)


def plot_slice(plane: str):
    source = sources[plane]
    slice = source.data['image'][0]
    plot = bp.figure(plot_width=slice.shape[1] * 2,
                     plot_height=slice.shape[0] * 2,
                     x_range=[0, slice.shape[1]],
                     y_range=[0, slice.shape[0]],
                     title=f'{plane.capitalize()} View',
                     tools=[
                         HoverTool(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])])
    plot.image(image='image', x=0, y=0, dw=slice.shape[1], dh=slice.shape[0],
               source=source, palette='Spectral11')
    return plot


def update_sources(i_sagittal_slice: int, i_coronal_slice: int,
                   i_horizontal_slice: int, cortical_class: int):
    sources = aal_handler.get_columndatasources_by_coords(i_sagittal_slice,
                                                          i_coronal_slice,
                                                          i_horizontal_slice,
                                                          cortical_class)


def plot_multi_planar(i_sagittal_slice: int, i_coronal_slice: int,
                      i_horizontal_slice: int, cortical_class: int):
    # update_sources(i_sagittal_slice,
    #                i_coronal_slice,
    #                i_horizontal_slice,
    #                cortical_class)
    return [plot_slice(plane) for plane in aal_handler.slice_planes]


# final = gridplot([plot_slice(start_slice), info_div], [widgetbox(slice_slider, class_slider)])
multi_planar_plot = plot_multi_planar(i_sagittal_slice, i_coronal_slice, i_horizontal_slice,
                                      cortical_class)
final = gridplot([multi_planar_plot])

curdoc().add_root(final)
