import bokeh.plotting as bp
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import gridplot, widgetbox
from bokeh.client import push_session
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import Div, Slider
from .analysis import CorticalLayersAnalysis


class DataViewer:
    info_template = '''
    Min: {}<br />
    Max: {}<br />
    Mean: {}<br />
    STD: {}<br />
    '''

    def __init__(self, analysis: CorticalLayersAnalysis):
        self.analysis = analysis

    def plot_interactive_2d_aal(self):
        data = DataHandler(self.analysis.all_class_means_over_aal)
        starting_image = data.get_coronal_slice(slice=0, cortical_class=0)
        source = ColumnDataSource(data=dict(image=[starting_image]))
        plot = bp.figure(plot_width=starting_image.shape[0] * 3,
                         plot_height=starting_image.shape[1] * 3,
                         x_range=[0, starting_image.shape[0]],
                         y_range=[0, starting_image.shape[1]],
                         title=f'Cortical classes probability over {self.analysis.n_regions} AAL regions',
                         tools=[
                             HoverTool(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])])
        plot.image(image='image', x=0, y=0, dw=starting_image.shape[0], dh=starting_image.shape[1],
                   source=source, palette='Spectral11')
        slice_slider = Slider(start=1, end=self.analysis.aal_1000.shape[2], value=1, step=1,
                              title="Slice")
        class_slider = Slider(start=1, end=self.analysis.n_classes, value=1, step=1, title="Class")
        start_info = starting_image.min(), starting_image.max(), starting_image.mean(), starting_image.std()
        info = Div(text=self.info_template.format(*start_info), width=200, height=100)

        def update_slice(attr, old, new):
            new_image = data.get_coronal_slice(slice=slice_slider.value - 1,
                                               cortical_class=class_slider.value - 1)
            source.data = dict(image=[new_image])
            current_info = new_image.min(), new_image.max(), new_image.mean(), new_image.std()
            info.text = self.info_template.format(*current_info)

        def update_class(attr, old, new):
            new_image = data.get_coronal_slice(slice=slice_slider.value - 1,
                                               cortical_class=class_slider.value - 1)
            source.data = dict(image=[new_image])
            current_info = new_image.min(), new_image.max(), new_image.mean(), new_image.std()
            info.text = self.info_template.format(*current_info)

        slice_slider.on_change('value', update_slice)
        class_slider.on_change('value', update_class)
        curdoc().add_root(gridplot([plot, info], [widgetbox(slice_slider, class_slider)]))
        session = push_session(curdoc())
        session.show()
        session.loop_until_closed()


class DataHandler:
    def __init__(self, image: np.ndarray):
        self.image = image

    def get_sagittal_slice(self, slice: int, cortical_class: int):
        return np.fliplr(np.transpose(self.image[slice, :, :, cortical_class]))

    def get_coronal_slice(self, slice: int, cortical_class: int):
        return self.image[:, slice, :, cortical_class]

    def get_horizontal_slice(self, slice: int, cortical_class: int):
        return np.transpose(self.image[:, :, slice, cortical_class])
