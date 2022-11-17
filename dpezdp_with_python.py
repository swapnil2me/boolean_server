import os
import glob
import subprocess
from datetime import datetime as dt
from pandas.io.json import json_normalize


class DPEZDP():
    """docstring for DPEZDP"""

    def __init__(self, tcase=None, base_path_abs=None, technology=None, keyword=None, kerf=None):
        self.tcase = tcase
        self.base_path_abs = base_path_abs
        self.testing_path = os.path.join(base_path_abs, keyword, tcase.split('/')[-1])
        self.technology = technology
        self.keyword = keyword
        self.kerf = kerf
        self.runs = set()
        self.xor_outputs = set()

    def run_sand(self):
        self._run('sand')

    def run_prod(self):
        self._run('prod')

    def _run(self, mode):
        ts = dt.now().strftime('%Y%m%d%H%M')
        run_dir = os.path.join(self.testing_path, mode + '_' + ts)
        print('making dir: ', run_dir)
        os.makedirs(run_dir, exist_ok=True)
        if self.kerf:
            dpezdp = "dpezdp -mode " + mode + " -ll +smp 16 +cleanup none -runnozz +technology " + self.technology + " " + self.tcase + " " + self.keyword
        else:
            dpezdp = "dpezdp -mode " + mode + " -ll +smp 16 +cleanup none -runnozz +technology " + self.technology + " " + self.tcase + " " + self.keyword
        print('initiating run')
        print('*=' * 15 + '\n' + '=*' * 15)
        print(dpezdp)
        print('*=' * 15 + '\n' + '=*' * 15)
        p = subprocess.Popen(dpezdp, shell=True, cwd=run_dir)
        p.communicate()
        self.runs.add(run_dir)

    def check_mrc_errors(self, only_xor_runs=False):
        self.update_paths()
        run_error_db = []
        summary_file = os.path.join(self.testing_path, 'testing_summary.txt')
        summary_file_handle = open(summary_file, 'w')

        if only_xor_runs:
            xors = self.xor_outputs
            folder_list = []
            for i in xors:
                root_dir = i.split('xor')[0]
                d1 = '_'.join(i.split('/')[-2].split('_')[1:3])
                d2 = '_'.join(i.split('/')[-2].split('_')[3:])
                folder_list.append(os.path.join(root_dir, d1))
                folder_list.append(os.path.join(root_dir, d2))
                with open(i) as file:
                    print('=' * 10 + ' XOR SUMMARY ' + '=' * 10, file=summary_file_handle)
                    print(d1 + ' XOR ' + d2, file=summary_file_handle)
                    xor_lines = file.readlines()
                    summ = 'No differences found.\n' in xor_lines
                    if summ:
                        print(xor_lines[-1], file=summary_file_handle)
                    else:
                        print(''.join(xor_lines[-3:-1]), file=summary_file_handle)

        else:
            folder_list = sorted(self.runs)

        for folder in folder_list:
            f = glob.glob(os.path.join(folder, '*.DB'))[0]
            spec_errors = []
            with open(f, 'r') as db:
                for line in db:
                    if line.strip('\n').endswith('.spec'):
                        err_dict = {'mrc_error_name': line.strip('\n'),
                                    'count': next(db).split()[0]}
                        spec_errors.append(err_dict)
            run_error_db.append({'path': folder,
                                 'mrc_list': spec_errors,
                                 'run_dir': folder.split('/')[-1]
                                 }
                                )
        # print(run_error_db)
        mrc = json_normalize(run_error_db, record_path='mrc_list', meta=['path', 'run_dir'])
        pivot = mrc.pivot(index='mrc_error_name', columns='run_dir', values='count')
        print('=' * 10 + ' MRC SUMMARY ' + '=' * 10, file=summary_file_handle)
        print(pivot, file=summary_file_handle)

        summary_file_handle.close()
        mrc.to_csv(os.path.join(self.testing_path, 'mrc_summary.csv'))

    def update_paths(self):
        run_dir = self.testing_path
        stamp_list = next(os.walk(run_dir))[1]

        run_path = [os.path.join(run_dir, i) for i in stamp_list if not 'xor' in i]
        self.runs.update(run_path)

        xor_path = [os.path.join(run_dir, i, 'xor_summary.txt') for i in stamp_list if 'xor' in i]
        self.xor_outputs.update(xor_path)

    def get_output_oas(self):
        self.update_paths()
        run_paths = sorted(self.runs)
        oas_dir = []
        for path in run_paths:
            f = glob.glob(os.path.join(path, '*.comp.prescale'))[0]
            oas_dir.append({'stamp': f.split('/')[-2],
                            'full_path': f,
                            'mode': f.split('/')[-2].split('_')[0]})
        return oas_dir

    def get_xor_list(self):
        xor_list = []
        oas_dir = self.get_output_oas()
        prod_dirs = list(filter(lambda d: d['mode'] == 'prod', oas_dir))
        sand_dirs = list(filter(lambda d: d['mode'] == 'sand', oas_dir))

        assert len(prod_dirs) == len(sand_dirs), "unequal sand and prod runs"
        for i in zip(prod_dirs, sand_dirs):
            xor_list.append({'prod_path': i[0]['full_path'],
                             'prod_stamp': i[0]['stamp'],
                             'sand_path': i[1]['full_path'],
                             'sand_stamp': i[1]['stamp']})

        return xor_list

    def xor_sand_prod(self):
        xor_list = self.get_xor_list()
        testing_path = self.testing_path
        for i in xor_list:
            xor_dir = os.path.join(testing_path, 'xor_' + i['sand_stamp'] + '_' + i['prod_stamp'])
            cmd = '/afs/btv/data/niagbtv/DEV/bin/xor.pl' + ' ' + i['sand_path'] + ' ' + i[
                'prod_path'] + ' ' + os.path.join(xor_dir, 'xor_output.oas') + ' > ' + os.path.join(xor_dir,
                                                                                                    'xor_summary.txt')
            os.makedirs(xor_dir, exist_ok=True)
            p = subprocess.Popen(cmd, shell=True, cwd=xor_dir)
            p.communicate()
            self.xor_outputs.add(os.path.join(xor_dir, 'xor_summary.txt'))
        print('done XOR')


base_path_abs = "/proj/zprep/smore2/Internship_Learning/11_python/01_test_dpezdp_with_py/test14_130cbic"
# tcase_path = '/proj/zprep/smore2/45SP3/tcases_MPWCS73/'
tcase_path = '/proj/zprep/smore2/Internship_Learning/11_python/01_test_dpezdp_with_py/130cbic_tcase'
tcase_list = [os.path.join(tcase_path, i) for i in os.listdir(tcase_path)]
technology = "130CBIC"
kw = "BP130CBIC"

for tcase in tcase_list:
    print('#' * 15 + '\n' + '=' * 15)
    tc = DPEZDP(tcase, base_path_abs, technology, kw)
    tc.run_sand()
    print('#' * 15 + '\n' + '=' * 15)

# tc.run_prod()
# tc.xor_sand_prod()
# tc.check_mrc_errors(True)
# tc = DPEZDP(tcase_list[0], base_path_abs, technology, kw)
# tc.run_sand()

# os.makedirs(test_dir, exist_ok=True)
# dpezdp = "dpezdp -mode " + mode + " -ll +smp 16 +cleanup none -runnozz +technology " + technology + " +kerf " + tcase + " " + kw
# print(dpezdp)
# # os.system("cd " + test_dir)
# # os.system(dpezdp)


# p = subprocess.Popen(dpezdp, shell=True, cwd=test_dir)
# p.communicate()
# /afs/btv/data/niagbtv/DEV/bin/xor.pl sandbox_run.oas production_run.oas xor_sand_prod.oas > xor_sand_prod.txt