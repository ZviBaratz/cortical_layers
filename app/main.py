import bokeh.plotting as bp
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import gridplot, widgetbox
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import Slider

from helpers import AllClassAALHandler

data = np.load('/home/flavus/PycharmProjects/cortical_layers/app/all_class_means_aal.npy')

# Create an image wrapper object to easily generate slices
image = AllClassAALHandler(data)

# Create a data source for the start slice
start_slice = image.get_coronal_slice(slice=0, cortical_class=0)
source = ColumnDataSource(data=dict(image=[start_slice]))

# Create slice and class sliders
slice_slider = Slider(start=1, end=100, value=1, step=1, title="Slice")
class_slider = Slider(start=1, end=6, value=1, step=1, title="Class")

# Create an info paragraph next to the image
info_div = image.create_slice_info_div(start_slice)


def plot_slice(slice: np.ndarray):
    plot = bp.figure(plot_width=slice.shape[0] * 3,
                     plot_height=slice.shape[1] * 3,
                     x_range=[0, slice.shape[0]],
                     y_range=[0, slice.shape[1]],
                     tools=[
                         HoverTool(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])])
    plot.image(image='image', x=0, y=0, dw=slice.shape[0], dh=slice.shape[1],
               source=source, palette='Spectral11')
    return plot


def update_slice(attr, old, new):
    new_image = image.get_coronal_slice(slice=slice_slider.value - 1,
                                        cortical_class=class_slider.value - 1)
    source.data = dict(image=[new_image])
    info_div.text = image.get_formatted_slice_info_template(new_image)


def update_class(attr, old, new):
    new_image = image.get_coronal_slice(slice=slice_slider.value - 1,
                                        cortical_class=class_slider.value - 1)
    source.data = dict(image=[new_image])
    info_div.text = image.get_formatted_slice_info_template(new_image)


# Set slider handlers
slice_slider.on_change('value', update_slice)
class_slider.on_change('value', update_class)

final = gridplot([plot_slice(start_slice), info_div], [widgetbox(slice_slider, class_slider)])

curdoc().add_root(final)
