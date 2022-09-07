from MyObjects.svrf_model import SVRF
kw_path = '../03_Etracting_BoolOps/BooleanTree/'
kw_list = [f'bf40dsp{i}.svrf' for i in range(1, 8)]
kw_list.append('nw40erf.svrf')
svrf = SVRF(name=kw_list[-1], path=kw_path)
svrf.update_svrf()
svrf.build_bool_tree()
svrf.build_single_bool_tree()
svrf.print_bool_ops()

nul = svrf.var_dict['NUL']
bf1 = svrf.var_dict['BF1']

# # print(l)
# print([l[i].getRootVal() for i in range(len(l))])
