from flask import Flask, render_template
# from MyObjects.svrf_model import SVRF
from MyObjects.svrf_model_full_depth_bool import SVRF

app = Flask(__name__)

kw_path = './SVRFs/'
kw_list = [f'bf40dsp{i}.svrf' for i in range(1, 8)]
kw_list.append('nw40erf.svrf')

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html', kw_list=kw_list)


@app.route('/<kw>')
def keyword_tree(kw):
    svrf = SVRF(name=kw, path=kw_path)
    svrf.update_svrf()
    svrf.build_bool_tree()
    svrf.build_single_bool_tree()
    # svrf.print_bool_ops()
    lines = svrf.write_bool_to_list()
    return render_template('boolean_tree.html', body_code='\n'.join(lines))


if __name__ == '__main__':
    app.run(debug=True)
