from qpt.executor import CreateExecutableModule as CEM

moudule = CEM(work_dir='./',
              launcher_py_path='main.py',
              save_path='./dist')

moudule.make()