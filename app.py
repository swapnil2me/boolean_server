from flask import Flask, render_template
from MyObjects.svrf_model import SVRF
# import re
import glob
# from MyObjects.svrf_model_full_depth_bool import SVRF

app = Flask(__name__)

kw_path = './SVRFs/'


def get_svrf_list(dir_path):
    """
    glob.glob grabs the svrf's full path
    the path is split at the backslash,
    """
    # svrf_list = [re.sub(r'\\', '', i.split('SVRFs')[1]) for i in glob.glob(dir_path + '*.svrf')]
    svrf_list = [i.split('\\')[1] for i in glob.glob(dir_path + '*.svrf')]
    return svrf_list


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html', kw_list=get_svrf_list(kw_path))


@app.route('/<kw>')
def keyword_tree(kw):
    svrf = SVRF(name=kw, path=kw_path)
    svrf.update_svrf()
    svrf.build_bool_tree()
    svrf.build_single_bool_tree()
    # svrf.print_bool_ops()
    lines = svrf.write_bool_to_list()
    return render_template('boolean_tree.html', body_code='\n'.join(lines), title=kw)


if __name__ == '__main__':
    app.run(debug=True)
