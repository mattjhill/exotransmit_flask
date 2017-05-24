import flask
import os
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

import numpy as np
from ExoCTK.pal import exotransmit

app = flask.Flask(__name__)

colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

# @app.route('/')
# def index():
#   return flask.render_template('index.html')

# @app.route('/countme/<input_str>')
# def count_me(input_str):
#     return input_str

# # @app.route('/exotransmit/')
# # def exotransmit():

@app.route('/')
def polynomial():
    """ Very simple embedding of a polynomial chart
    """

    # Grab the inputs arguments from the URL
    args = flask.request.args
    if args:
        output_file = 'Spectra/new.dat'
    else:
        output_file = 'Spectra/default.dat'
    # Get all the form arguments in the url with defaults
    eos = getitem(args, 'eos', 'eos_0p1Xsolar_cond.dat')
    tp = getitem(args, 'tp', 't_p_800K.dat')
    g = float(getitem(args, 'g', 9.8))
    R_p = float(getitem(args, 'R_p', 6400000.0))
    R_s = float(getitem(args, 'R_s', 700000000.0))
    P = float(getitem(args, 'P', 0.0))
    Rayleigh = float(getitem(args, 'Rayleigh', 1.0))

    # Create a polynomial line graph with those arguments
    # x = list(range(_from, to + 1))
    if args:
        exotransmit.exotransmit(EOS_file=os.path.join('/EOS', eos),
            T_P_file=os.path.join('/T_P', tp),
            g=g,
            R_planet=R_p,
            R_star=R_s,
            P_cloud=P,
            Rayleigh=Rayleigh, 
            output_file='/Spectra/new.dat',
            )

    x, y = np.loadtxt(output_file, skiprows=2, unpack=True)
    fig = figure(plot_width=1000, plot_height=250, responsive=False)
    fig.line(x/1e-6, y, color='Black', line_width=0.5)
    fig.xaxis.axis_label = 'Wavelength (um)'
    fig.yaxis.axis_label = 'Transit Depth'

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(fig)

    html = flask.render_template(
        'embed.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        eos_files=os.listdir('EOS'),
        tp_files=os.listdir('T_P'),
        tp=tp,
        eos=eos,
        g=g,
        R_p=R_p,
        R_s=R_s,
        P=P,
        Rayleigh=Rayleigh
    )
    return encode_utf8(html)

if __name__ == '__main__':
  app.run()