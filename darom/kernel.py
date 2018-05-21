import pdb
import time
import random

from darom import process
from darom import resource
from darom.resource import Resource, ResourceRequest
from darom.process import Status

class Kernel:
    def __init__(self, rm, verbose=False):
        self._processes = []
        self._ready_procs = []
        self._run_proc = process.Process(name='IDLE', priority=10)

        self._resources = []

        self._rm = rm
        self._rm._kernel = self

        self._call_planner = True
        self._verbose = verbose

    def __str__(self):
        str = '-----------------------Kernel--------------------\n'
        str += "Processes:\n"
        for p in self._processes:
            str += "\t{}\n".format(p)
        str += "Resources:\n"
        for r in self._resources:
            str += "\t{}\n".format(r)
        str += "Ready Processes:\n"
        for p in self.ready_procs:
            str += "\t{}\n".format(p)
        str += "Run Process:\n"
        str += "\t{}\n".format(self._run_proc)
        str += '------------------------------------------------\n'
        return str

    @property
    def processes(self):
        return self._processes

    @property
    def ready_procs(self):
        return self._ready_procs

    @property
    def run_proc(self):
        return self._run_proc

    @run_proc.setter
    def run_proc(self, run_proc):
        self._run_proc = run_proc

    def _find_res_by_name(self, res_name):
        for res in self._resources:
            if res.name == res_name:
                return res
        raise Exception("Resource '{}' not found!".format(res_name))

    def _print_process_transition(self, old_proc):
        # pass
        # print('\t', [proc.name for proc in self._ready_procs])
        print("{:<15} -> {:>15}".format(old_proc.name if old_proc else "", self._run_proc.name))

    def _select_process(self):
        self._ready_procs.sort(key=lambda p: p.priority, reverse=True)
        max_p = self._ready_procs[0].priority
        candidates = [proc for proc in self._ready_procs if proc.priority == max_p]
        return random.choice(candidates)

    def _add_ready_processes(self):
        for p in self._processes:
            if p.status == Status.READY and p not in self._ready_procs:
                self._ready_procs.append(p)

    def _remove_blocked_processes(self):
        for p in self._ready_procs:
            st = p.status
            if st == Status.BLOCK or st == Status.BLOCKS or st == Status.READYS:
                self._ready_procs.remove(p)

    def _remove_if_exists(self, value, list):
        if value in list:
            list.remove(value)

    def planner(self, window=None, init=None):
        # self._planner_works = True
        while True:
        # while self._call_planner:
            # self._call_planner = False
            self.distributor()
            self._remove_blocked_processes()
            self._add_ready_processes()
            old_proc = self._run_proc
            if self._ready_procs:
                p = self._select_process()
                # pdb.set_trace()
                self._run_proc = p
                self._print_process_transition(old_proc) if self._verbose else None
                p.run()
            else:
                self._run_proc = process.Process(name='IDLE', priority=10)
                # self._print_process_transition(old_proc)
            if window:
                # print('update started')
                window.update()

            if init:
                for f in init:
                    f()
                init=False
        # self._planner_works = False

    # def plan(self):
    #     self._call_planner = True
    #     if not self._planner_works:
    #         self.planner()

    def distributor(self):
        for res in self._resources:
            for req in res._wait_list:
                if res.elements_available(req.amount, req.cond):
                    req.proc.owned_res.extend(res.get_elements(req.amount, req.cond))
                    req.proc.unblock()
                    # self._ready_procs.append(req.proc)
        # self.plan()


    def create_process(self, process):
        print("{:<15} : create_process({})".format(self._run_proc.name, process.name)) if self._verbose else None
        self._run_proc.children.append(process)
        process.kernel = self
        process.parent = self.run_proc
        self._processes.append(process)
        self._ready_procs.append(process)

    def destroy_process(self, process):
        print("{:<15} : destroy proc({})".format(self._run_proc.name, process.name)) if self._verbose else None
        for child in process.children:
            self.destroy_process(child)
            self._remove_if_exists(process, self._run_proc.children)
        self._remove_if_exists(process, self._ready_procs)
        self._remove_if_exists(process, self._processes)

    def stop_process(self, process):
        pass

    def activate_process(self, process):
        pass

    def create_res(self, res_name):
        res = Resource(parent=self._run_proc, name=res_name)

        self._run_proc.created_res.append(res)
        self._resources.append(res)

    def destroy_res(self, res_name):
        pass

    def request_res(self, res_name, amount, cond=None):
        print("{:<15} : request_res({})".format(self._run_proc.name, res_name)) if self._verbose else None
        res = self._find_res_by_name(res_name)
        res.wait_list.append(ResourceRequest(self._run_proc, amount, cond))
        self._run_proc.status = Status.BLOCK

        # self.distributor()

    '''
    elem_data - masyvas, kurio kiekvienas elementas yra resurso elementu duomenys
    '''
    def release_res(self, res_name, elem_data):
        print("{:<15} : release_res({}, {})".format(self._run_proc.name, res_name, elem_data)) if self._verbose else None

        res = self._find_res_by_name(res_name)
        for data in elem_data:
            new_element = resource.ResourceElement(name=res_name, data=data)
            res.elements.append(new_element)

        # self.distributor()
